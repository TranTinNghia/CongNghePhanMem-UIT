# Hướng dẫn Deploy ứng dụng lên Web

## Tổng quan

Ứng dụng Flask này cần được deploy lên một hosting service để mọi người có thể truy cập. Dưới đây là các phương án và hướng dẫn chi tiết.

## ⚠️ Lưu ý quan trọng

1. **Database**: Ứng dụng sử dụng SQL Server, cần đảm bảo database có thể truy cập từ internet
2. **Config**: File `config/config.yaml` chứa thông tin nhạy cảm, không được commit lên Git
3. **Secret Key**: Cần thay đổi `app.secret_key` trong `app.py` thành một giá trị ngẫu nhiên mạnh

## Phương án 1: Railway (Khuyến nghị - Miễn phí)

### Bước 1: Chuẩn bị
1. Đăng ký tài khoản tại [railway.app](https://railway.app)
2. Cài đặt Railway CLI (tùy chọn):
   ```bash
   npm i -g @railway/cli
   ```

### Bước 2: Deploy
1. Tạo project mới trên Railway
2. Kết nối GitHub repository
3. Railway sẽ tự động detect Flask app
4. Thêm các Environment Variables:
   - `DB_URL`: Connection string của SQL Server
   - `DB_USERNAME`: Username database
   - `DB_PASSWORD`: Password database
   - `DB_NAME`: Tên database
   - `FLASK_SECRET_KEY`: Secret key cho Flask session

### Bước 3: Cấu hình Database
- Railway cung cấp PostgreSQL miễn phí, nhưng bạn đang dùng SQL Server
- Có thể dùng Azure SQL Database (có free tier) hoặc SQL Server trên VPS

## Phương án 2: Render (Miễn phí)

### Bước 1: Chuẩn bị
1. Đăng ký tại [render.com](https://render.com)
2. Kết nối GitHub account

### Bước 2: Deploy
1. Tạo "New Web Service"
2. Chọn repository
3. Cấu hình:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Environment**: Python 3
4. Thêm Environment Variables (tương tự Railway)

## Phương án 3: PythonAnywhere (Miễn phí - Dễ nhất)

### Bước 1: Đăng ký
1. Đăng ký tại [pythonanywhere.com](https://www.pythonanywhere.com)
2. Tạo tài khoản miễn phí (Beginner account)

### Bước 2: Upload code
1. Vào "Files" tab
2. Upload code hoặc clone từ Git
3. Cài đặt dependencies trong Bash console:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

### Bước 3: Cấu hình Web App
1. Vào "Web" tab
2. Tạo web app mới
3. Chọn "Manual configuration" → Python 3.10
4. Chỉnh sửa WSGI file:
   ```python
   import sys
   path = '/home/yourusername/path/to/app'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app as application
   ```
5. Thêm environment variables trong Web tab

### Bước 4: Cấu hình Database
- PythonAnywhere không hỗ trợ SQL Server trực tiếp
- Cần dùng Azure SQL hoặc SQL Server trên VPS khác

## Phương án 4: VPS (DigitalOcean, Linode, Vultr)

### Bước 1: Tạo VPS
1. Tạo VPS (Ubuntu 22.04) với ít nhất 2GB RAM
2. SSH vào server

### Bước 2: Cài đặt
```bash
# Cập nhật hệ thống
sudo apt update && sudo apt upgrade -y

# Cài đặt Python và dependencies
sudo apt install python3 python3-pip python3-venv -y
sudo apt install unixodbc-dev -y  # Cho pyodbc
sudo apt install freetds-dev freetds-bin -y

# Cài đặt SQL Server ODBC Driver
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Clone code
git clone <your-repo-url>
cd BaiTapNhom

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
pip install gunicorn

# Tạo config.yaml
nano config/config.yaml
# Nhập thông tin database
```

### Bước 3: Chạy với Gunicorn
```bash
# Chạy thử
gunicorn app:app --bind 0.0.0.0:8000

# Tạo systemd service
sudo nano /etc/systemd/system/flaskapp.service
```

Nội dung file service:
```ini
[Unit]
Description=Flask App
After=network.target

[Service]
User=yourusername
WorkingDirectory=/home/yourusername/BaiTapNhom
Environment="PATH=/home/yourusername/BaiTapNhom/venv/bin"
ExecStart=/home/yourusername/BaiTapNhom/venv/bin/gunicorn app:app --bind 0.0.0.0:8000 --workers 2

[Install]
WantedBy=multi-user.target
```

```bash
# Khởi động service
sudo systemctl start flaskapp
sudo systemctl enable flaskapp
```

### Bước 4: Cấu hình Nginx
```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/flaskapp
```

Nội dung:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/flaskapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Các bước chung cần làm

### 1. Cập nhật Secret Key
Trong `app.py`, thay đổi:
```python
app.secret_key = "secret-key"  # ❌ Không an toàn
```

Thành:
```python
import os
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())
```

### 2. Cấu hình Database
- Đảm bảo SQL Server có thể truy cập từ internet
- Mở firewall port 1433
- Cấu hình SQL Server để cho phép remote connections
- Sử dụng connection string an toàn (encrypted)

### 3. Environment Variables
Thay vì dùng `config.yaml`, nên dùng environment variables:
- `DB_URL`: Connection string
- `DB_USERNAME`: Username
- `DB_PASSWORD`: Password
- `DB_NAME`: Database name

### 4. File Uploads
- Đảm bảo thư mục `uploads/` có quyền ghi
- Có thể dùng cloud storage (AWS S3, Azure Blob) cho production

## Khuyến nghị

**Cho dự án học tập/nhỏ:**
- **PythonAnywhere**: Dễ nhất, miễn phí, nhưng cần SQL Server riêng
- **Render**: Dễ deploy, miễn phí, tự động deploy từ Git

**Cho production:**
- **VPS (DigitalOcean/Linode)**: Toàn quyền kiểm soát, ~$5-10/tháng
- **Azure App Service**: Tích hợp tốt với Azure SQL, có free tier

## Troubleshooting

1. **Lỗi kết nối database**: Kiểm tra firewall, connection string
2. **Lỗi pyodbc**: Cần cài đặt ODBC driver trên server
3. **Lỗi OCR**: Cần cài đặt Tesseract và Poppler
4. **Timeout**: Tăng timeout trong Gunicorn config

## Liên hệ hỗ trợ

Nếu gặp vấn đề, kiểm tra logs:
- Railway/Render: Xem logs trong dashboard
- VPS: `sudo journalctl -u flaskapp -f`

