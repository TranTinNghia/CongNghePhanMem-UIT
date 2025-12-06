# Hướng dẫn nhanh: Dùng ngrok để kết nối Render với SQL Server local

## Bước 1: Tải và cài đặt ngrok

### Windows:
1. Tải từ: https://ngrok.com/download
2. Giải nén `ngrok.exe` vào thư mục (ví dụ: `C:\ngrok\`)
3. Mở Command Prompt, chạy:
   ```cmd
   cd C:\ngrok
   ```

### Linux (WSL):
```bash
# Tải ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

## Bước 2: Đăng ký và lấy Auth Token

1. Đăng ký miễn phí tại: https://dashboard.ngrok.com/signup
2. Sau khi đăng nhập, vào: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy **Your Authtoken** (dạng: `2abc123def456ghi789jkl012mno345pqr678`)

## Bước 3: Cấu hình ngrok

### Windows (Command Prompt):
```cmd
cd C:\ngrok
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

### Linux (WSL):
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

## Bước 4: Đảm bảo SQL Server đang chạy và cho phép remote connections

### Kiểm tra SQL Server đang chạy:
```cmd
# Windows
netstat -an | findstr 1433
```

Nếu thấy `0.0.0.0:1433` hoặc `127.0.0.1:1433` → SQL Server đang chạy ✅

### Cấu hình SQL Server cho remote connections:

1. Mở **SQL Server Configuration Manager**
2. Vào **SQL Server Network Configuration** → **Protocols for MSSQLSERVER**
3. Right-click **TCP/IP** → **Enable**
4. Double-click **TCP/IP** → Tab **IP Addresses**
5. Scroll xuống **IPAll**
6. Set **TCP Port** = `1433`
7. **OK** → **Restart** SQL Server service

### Mở Windows Firewall:

1. Mở **Windows Defender Firewall with Advanced Security**
2. **Inbound Rules** → **New Rule**
3. Chọn **Port** → **Next**
4. **TCP** → **Specific local ports**: `1433` → **Next**
5. **Allow the connection** → **Next**
6. Chọn tất cả profiles → **Next**
7. Đặt tên: "SQL Server 1433" → **Finish**

## Bước 5: Khởi động ngrok tunnel

### Windows:
```cmd
cd C:\ngrok
ngrok tcp 1433
```

### Linux (WSL):
```bash
ngrok tcp 1433
```

Bạn sẽ thấy output như:
```
Session Status                online
Account                       your-email@example.com
Forwarding                    tcp://0.tcp.ngrok.io:12345 -> localhost:1433

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**QUAN TRỌNG**: Copy địa chỉ `0.tcp.ngrok.io:12345` (số port sẽ khác)

## Bước 6: Cấu hình trên Render

1. Vào [Render Dashboard](https://dashboard.render.com)
2. Chọn Web Service của bạn
3. Tab **"Environment"**
4. Thêm các Environment Variables:

   - **Key**: `DB_URL`
     **Value**: `jdbc:sqlserver://0.tcp.ngrok.io:12345;databaseName=btn;encrypt=true;trustServerCertificate=true`
     (Thay `0.tcp.ngrok.io:12345` bằng địa chỉ ngrok của bạn)

   - **Key**: `DB_USERNAME`
     **Value**: `cdc_user`

   - **Key**: `DB_PASSWORD`
     **Value**: `@TTn120897@`

   - **Key**: `DB_NAME`
     **Value**: `btn`

   - **Key**: `FLASK_SECRET_KEY`
     **Value**: Tạo bằng lệnh: `python -c "import secrets; print(secrets.token_hex(24))"`

5. Click **"Save Changes"**

## Bước 7: Rebuild trên Render

1. Tab **"Manual Deploy"**
2. Click **"Deploy latest commit"**

## Kiểm tra

Sau khi rebuild, kiểm tra logs:
- Không còn lỗi: `Lỗi đọc config: [Errno 2] No such file or directory`
- Có thể đăng nhập và sử dụng ứng dụng

## ⚠️ Lưu ý quan trọng

1. **URL ngrok thay đổi mỗi lần restart**:
   - Mỗi lần bạn tắt và mở lại ngrok, URL sẽ thay đổi
   - Cần update `DB_URL` trên Render mỗi lần
   - Giữ terminal ngrok mở để URL không đổi

2. **Chỉ dùng cho development/testing**:
   - Không phù hợp cho production
   - Dữ liệu thật nên dùng Azure SQL hoặc VPS

3. **Bảo mật**:
   - Đảm bảo SQL Server có password mạnh
   - Chỉ expose khi cần thiết

## Troubleshooting

### Lỗi: "Cannot connect to server"
- Kiểm tra ngrok đang chạy: Xem terminal ngrok có hiển thị "online" không
- Kiểm tra SQL Server đang listen: `netstat -an | findstr 1433`
- Kiểm tra Windows Firewall có block không

### Lỗi: "Login failed"
- Kiểm tra username/password có đúng không
- Kiểm tra SQL Server có cho phép SQL authentication không:
  ```sql
  -- Chạy trong SQL Server Management Studio
  ALTER LOGIN cdc_user WITH PASSWORD = 'your_password';
  ```

### URL ngrok thay đổi
- Giữ terminal ngrok mở
- Hoặc dùng ngrok paid tier ($8/tháng) để có static domain

## Tạo script tự động (Tùy chọn)

Tạo file `start-ngrok.bat` (Windows) hoặc `start-ngrok.sh` (Linux):

### Windows (`start-ngrok.bat`):
```batch
@echo off
cd C:\ngrok
echo Starting ngrok tunnel for SQL Server...
ngrok tcp 1433
pause
```

### Linux (`start-ngrok.sh`):
```bash
#!/bin/bash
echo "Starting ngrok tunnel for SQL Server..."
ngrok tcp 1433
```

Chạy script này mỗi khi cần expose SQL Server.

