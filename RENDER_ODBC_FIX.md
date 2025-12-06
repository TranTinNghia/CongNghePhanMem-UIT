# Fix: Cài đặt ODBC Driver trên Render.com

## Vấn đề
Render.com không có Microsoft ODBC Driver cho SQL Server được cài đặt sẵn, dẫn đến lỗi:
```
Can't open lib 'ODBC Driver 18 for SQL Server' : file not found
```

## Giải pháp

### Cách 1: Sử dụng Build Command (Khuyến nghị)

Trên Render Dashboard:

1. Vào **Web Service** → **Settings**
2. Tìm **Build Command**
3. Thay đổi thành:
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev && pip install --upgrade pip && pip install -r requirements.txt
```

4. **Start Command** giữ nguyên:
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### Cách 2: Sử dụng build.sh (Nếu Render hỗ trợ)

Nếu Render tự động chạy `build.sh`, file đã được cập nhật. Đảm bảo:

1. File `build.sh` có quyền thực thi:
```bash
chmod +x build.sh
```

2. Trong Render Dashboard → Build Command:
```bash
bash build.sh
```

### Cách 3: Sử dụng Docker (Nếu cần)

Nếu Render không cho phép cài đặt system packages, có thể cần dùng Docker image có sẵn ODBC drivers.

## Kiểm tra sau khi deploy

Sau khi deploy, kiểm tra logs để xem ODBC driver đã được cài đặt chưa. Nếu vẫn lỗi, thử:

1. Kiểm tra xem Render có cho phép cài đặt system packages không
2. Thử dùng FreeTDS thay vì Microsoft ODBC (phức tạp hơn)
3. Xem xét dùng Docker container với ODBC drivers đã cài sẵn

## Lưu ý

- Build command trên Render có thể mất thời gian lâu hơn do cần cài đặt ODBC drivers
- Đảm bảo SQL Server có thể truy cập từ internet (qua Cloudflare Tunnel hoặc public IP)
- Kiểm tra firewall và network settings

