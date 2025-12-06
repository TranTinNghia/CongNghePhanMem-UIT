# Hướng dẫn đơn giản: Cloudflare Tunnel cho SQL Server

## Cách đơn giản nhất (Không cần đăng nhập Cloudflare)

### Bước 1: Chạy Quick Tunnel

Mở terminal và chạy:

```bash
cloudflared tunnel --url tcp://localhost:1433
```

**KHÔNG CẦN** vào Cloudflare dashboard. Lệnh này sẽ tự động tạo tunnel.

### Bước 2: Copy URL từ output

Bạn sẽ thấy output như:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at:                                         |
|  tcp://abc123def456.trycloudflare.com:54321                                               |
+--------------------------------------------------------------------------------------------+
```

Copy URL: `abc123def456.trycloudflare.com:54321`

### Bước 3: Cấu hình trên Render

Vào Render Dashboard → Web Service → Environment → Thêm:

- **DB_URL**: 
  ```
  jdbc:sqlserver://abc123def456.trycloudflare.com:54321;databaseName=btn;encrypt=true;trustServerCertificate=true
  ```
  (Thay `abc123def456.trycloudflare.com:54321` bằng URL của bạn)

- **DB_USERNAME**: `cdc_user`
- **DB_PASSWORD**: `@TTn120897@`
- **DB_NAME**: `btn`

### Bước 4: Save và Rebuild

1. Save Changes
2. Manual Deploy → Deploy latest commit

## Lưu ý

- **Giữ terminal cloudflared mở** - Nếu đóng terminal, tunnel sẽ ngắt
- **URL thay đổi mỗi lần restart** - Cần update DB_URL trên Render mỗi lần
- **Đảm bảo SQL Server đang chạy** và cho phép remote connections

## Nếu gặp lỗi

### Lỗi: "Cannot connect"
- Kiểm tra SQL Server đang chạy: `netstat -an | findstr 1433`
- Kiểm tra SQL Server cho phép TCP/IP: SQL Server Configuration Manager
- Kiểm tra Windows Firewall có mở port 1433 không

### Lỗi: "Login failed"
- Kiểm tra username/password có đúng không
- Kiểm tra SQL Server có cho phép SQL authentication không

## Tóm tắt nhanh

1. Chạy: `cloudflared tunnel --url tcp://localhost:1433`
2. Copy URL từ output
3. Thêm vào Render: `DB_URL` với URL đó
4. Giữ terminal mở

**KHÔNG CẦN** vào Cloudflare dashboard!

