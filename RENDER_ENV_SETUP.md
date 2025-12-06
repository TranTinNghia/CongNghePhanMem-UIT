# Hướng dẫn cấu hình Environment Variables trên Render

## Vấn đề
Ứng dụng cần file `config/config.yaml` để kết nối database, nhưng file này không được commit lên Git (vì chứa password). Trên Render, cần dùng Environment Variables.

## Giải pháp

Code đã được cập nhật để đọc từ Environment Variables nếu không có file `config.yaml`.

### Bước 1: Thêm Environment Variables trên Render

1. Vào [Render Dashboard](https://dashboard.render.com)
2. Chọn Web Service của bạn
3. Vào tab **"Environment"**
4. Thêm các Environment Variables sau:

#### Database Connection String
- **Key**: `DB_URL`
- **Value**: Connection string của SQL Server
  - Format: `jdbc:sqlserver://your-server:1433;databaseName=btn;encrypt=true;trustServerCertificate=true`
  - Ví dụ: `jdbc:sqlserver://your-server.database.windows.net:1433;databaseName=btn;encrypt=true;trustServerCertificate=true`

#### Database Username
- **Key**: `DB_USERNAME`
- **Value**: Username để kết nối database
  - Ví dụ: `cdc_user`

#### Database Password
- **Key**: `DB_PASSWORD`
- **Value**: Password để kết nối database
  - Ví dụ: `your_password_here`

#### Database Name (Optional)
- **Key**: `DB_NAME`
- **Value**: Tên database (mặc định: `btn`)
  - Ví dụ: `btn`

### Bước 2: Thêm Flask Secret Key

- **Key**: `FLASK_SECRET_KEY`
- **Value**: Một chuỗi ngẫu nhiên mạnh (hoặc để Render tự generate)
  - Có thể tạo bằng: `python -c "import secrets; print(secrets.token_hex(24))"`
  - Ví dụ: `a1b2c3d4e5f6...` (ít nhất 24 ký tự)

### Bước 3: Save và Rebuild

1. Click **"Save Changes"**
2. Vào tab **"Manual Deploy"**
3. Click **"Deploy latest commit"**

## Format DB_URL

### Azure SQL Database
```
jdbc:sqlserver://your-server.database.windows.net:1433;databaseName=btn;encrypt=true;trustServerCertificate=true
```

### SQL Server trên VPS/Server
```
jdbc:sqlserver://your-server-ip:1433;databaseName=btn;encrypt=true;trustServerCertificate=true
```

### SQL Server với domain
```
jdbc:sqlserver://sql.yourdomain.com:1433;databaseName=btn;encrypt=true;trustServerCertificate=true
```

## Kiểm tra

Sau khi rebuild, kiểm tra logs:
- Không còn lỗi: `Lỗi đọc config: [Errno 2] No such file or directory`
- Có thể đăng nhập và sử dụng ứng dụng

## Lưu ý

- **KHÔNG BAO GIỜ** commit password hoặc thông tin nhạy cảm lên Git
- Environment Variables trên Render được mã hóa và bảo mật
- Có thể dùng Render's Secret Files nếu cần

## Troubleshooting

### Lỗi: "Không thể kết nối với bất kỳ ODBC driver nào"
- Kiểm tra SQL Server có cho phép remote connections không
- Kiểm tra firewall có mở port 1433 không
- Kiểm tra DB_URL, DB_USERNAME, DB_PASSWORD có đúng không

### Lỗi: "Lỗi đọc config"
- Đảm bảo đã thêm đầy đủ 3 environment variables: DB_URL, DB_USERNAME, DB_PASSWORD
- Kiểm tra format của DB_URL có đúng không

