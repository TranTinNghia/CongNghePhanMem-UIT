# Hướng dẫn kết nối Render với SQL Server trên máy local

## Vấn đề
Render (cloud) không thể truy cập trực tiếp `localhost` của bạn. Cần tạo tunnel để expose SQL Server ra internet.

## Giải pháp: Sử dụng ngrok (Miễn phí, Dễ nhất)

### Bước 1: Cài đặt ngrok

#### Windows:
1. Tải ngrok từ: https://ngrok.com/download
2. Giải nén file `ngrok.exe`
3. Đặt vào thư mục dễ tìm (ví dụ: `C:\ngrok\`)

#### Linux/Mac:
```bash
# Download và cài đặt
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Hoặc dùng snap
sudo snap install ngrok
```

### Bước 2: Đăng ký và lấy Auth Token

1. Đăng ký tài khoản miễn phí tại: https://dashboard.ngrok.com/signup
2. Vào Dashboard → "Your Authtoken"
3. Copy authtoken

### Bước 3: Cấu hình ngrok

#### Windows:
```cmd
# Mở Command Prompt
cd C:\ngrok
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

#### Linux/Mac:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### Bước 4: Khởi động ngrok tunnel

```bash
# Expose SQL Server port 1433
ngrok tcp 1433
```

Bạn sẽ thấy output như:
```
Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    tcp://0.tcp.ngrok.io:12345 -> localhost:1433
```

**Quan trọng**: Copy địa chỉ `0.tcp.ngrok.io:12345` (số port sẽ khác mỗi lần chạy)

### Bước 5: Cấu hình trên Render

1. Vào Render Dashboard → Web Service → Environment
2. Thêm Environment Variables:

- **DB_URL**: 
  ```
  jdbc:sqlserver://0.tcp.ngrok.io:12345;databaseName=btn;encrypt=true;trustServerCertificate=true
  ```
  (Thay `0.tcp.ngrok.io:12345` bằng địa chỉ ngrok của bạn)

- **DB_USERNAME**: `cdc_user` (hoặc username của bạn)

- **DB_PASSWORD**: `@TTn120897@` (hoặc password của bạn)

- **DB_NAME**: `btn`

### Bước 6: Đảm bảo SQL Server cho phép remote connections

#### Trên Windows:
1. Mở **SQL Server Configuration Manager**
2. Vào **SQL Server Network Configuration** → **Protocols for MSSQLSERVER**
3. Enable **TCP/IP**
4. Double-click **TCP/IP** → Tab **IP Addresses**
5. Scroll xuống **IPAll** → Set **TCP Port** = `1433`
6. **OK** và restart SQL Server service

#### Kiểm tra SQL Server đang listen:
```cmd
netstat -an | findstr 1433
```

### Bước 7: Cấu hình Windows Firewall

1. Mở **Windows Defender Firewall**
2. **Advanced settings** → **Inbound Rules** → **New Rule**
3. Chọn **Port** → **TCP** → **Specific local ports**: `1433`
4. **Allow the connection**
5. **Next** → **Finish**

### Bước 8: Rebuild trên Render

1. Vào Render Dashboard
2. **Manual Deploy** → **Deploy latest commit**

## Lưu ý quan trọng

### ⚠️ Ngrok Free Tier:
- **URL thay đổi mỗi lần restart** ngrok
- Cần update DB_URL trên Render mỗi lần restart ngrok
- Có giới hạn số lượng connections

### ✅ Ngrok Paid Tier ($8/tháng):
- **Static domain** (URL không đổi)
- Không giới hạn connections
- Phù hợp cho production

### 🔒 Bảo mật:
- Chỉ dùng cho development/testing
- **KHÔNG** dùng cho production với dữ liệu thật
- Đảm bảo SQL Server có password mạnh

## Giải pháp thay thế: Cloudflare Tunnel (Miễn phí, URL cố định)

### Bước 1: Cài đặt cloudflared
```bash
# Windows: Tải từ https://github.com/cloudflare/cloudflared/releases
# Linux/Mac:
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

### Bước 2: Tạo tunnel
```bash
cloudflared tunnel create sql-tunnel
cloudflared tunnel route dns sql-tunnel sql.yourdomain.com
```

### Bước 3: Chạy tunnel
```bash
cloudflared tunnel run sql-tunnel
```

## Troubleshooting

### Lỗi: "Cannot connect"
- Kiểm tra ngrok đang chạy không: Xem terminal ngrok
- Kiểm tra SQL Server đang listen port 1433: `netstat -an | findstr 1433`
- Kiểm tra Windows Firewall có block không

### Lỗi: "Login failed"
- Kiểm tra username/password có đúng không
- Kiểm tra SQL Server có cho phép SQL authentication không

### URL ngrok thay đổi
- Mỗi lần restart ngrok, URL sẽ thay đổi
- Cần update DB_URL trên Render
- Hoặc dùng ngrok paid tier để có static domain

## Khuyến nghị

**Cho development/testing:**
- ✅ Dùng **ngrok free** (đơn giản, nhanh)
- ⚠️ Nhớ update DB_URL mỗi lần restart ngrok

**Cho production:**
- ✅ Dùng **Azure SQL Database** hoặc **VPS với SQL Server**
- ❌ **KHÔNG** dùng ngrok cho production

