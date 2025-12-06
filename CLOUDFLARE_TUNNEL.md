# Hướng dẫn dùng Cloudflare Tunnel (Miễn phí, Không cần thẻ)

## Vấn đề
ngrok yêu cầu thẻ tín dụng để dùng TCP endpoints. Cloudflare Tunnel miễn phí và không cần thẻ.

## Bước 1: Cài đặt cloudflared

### Windows:
1. Tải từ: https://github.com/cloudflare/cloudflared/releases/latest
2. Tải file `cloudflared-windows-amd64.exe`
3. Đổi tên thành `cloudflared.exe`
4. Đặt vào thư mục (ví dụ: `C:\cloudflared\`)

### Linux (WSL):
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

## Bước 2: Đăng nhập Cloudflare

```bash
cloudflared tunnel login
```

Lệnh này sẽ:
1. Mở trình duyệt
2. Yêu cầu đăng nhập Cloudflare (hoặc đăng ký miễn phí)
3. Chọn domain (nếu có) hoặc bỏ qua
4. Tự động lưu certificate

## Bước 3: Tạo tunnel

```bash
cloudflared tunnel create sql-tunnel
```

Bạn sẽ thấy output:
```
Created tunnel sql-tunnel with id: abc123def456...
```

## Bước 4: Chạy tunnel (Simple mode - Không cần domain)

Tạo file config `config.yml`:

### Windows:
Tạo file `C:\cloudflared\config.yml`:

```yaml
tunnel: sql-tunnel
credentials-file: C:\Users\YOUR_USERNAME\.cloudflared\abc123def456.json

ingress:
  - hostname: sql-tunnel.your-domain.com
    service: tcp://localhost:1433
  - service: http_status:404
```

**HOẶC** dùng lệnh đơn giản hơn (không cần config file):

```bash
cloudflared tunnel --url tcp://localhost:1433
```

Bạn sẽ thấy output:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://abc123def456.trycloudflare.com                                                   |
+--------------------------------------------------------------------------------------------+
```

**QUAN TRỌNG**: Copy URL `abc123def456.trycloudflare.com` (sẽ khác mỗi lần)

## Bước 5: Parse URL để lấy host và port

URL từ Cloudflare có dạng: `tcp://abc123def456.trycloudflare.com:PORT`

Bạn cần lấy:
- **Host**: `abc123def456.trycloudflare.com`
- **Port**: Số port trong URL (ví dụ: `54321`)

## Bước 6: Cấu hình trên Render

1. Vào Render Dashboard → Web Service → Environment
2. Thêm Environment Variables:

   - **Key**: `DB_URL`
     **Value**: `jdbc:sqlserver://abc123def456.trycloudflare.com:54321;databaseName=btn;encrypt=true;trustServerCertificate=true`
     (Thay bằng host và port từ Cloudflare tunnel)

   - **Key**: `DB_USERNAME`
     **Value**: `cdc_user`

   - **Key**: `DB_PASSWORD`
     **Value**: `@TTn120897@`

   - **Key**: `DB_NAME`
     **Value**: `btn`

3. Save và rebuild

## Lưu ý

- URL Cloudflare tunnel thay đổi mỗi lần restart
- Cần update DB_URL trên Render mỗi lần
- Giữ terminal cloudflared mở để tunnel không đóng

## Alternative: Dùng Azure SQL Database (Khuyến nghị cho production)

Nếu muốn giải pháp ổn định hơn, nên dùng Azure SQL Database:
- Free tier có sẵn
- URL cố định
- Không cần giữ tunnel mở
- Xem hướng dẫn trong `DATABASE_SETUP.md`

