# Fix: Cloudflare Tunnel không hỗ trợ TCP cho SQL Server

## Vấn đề
Cloudflare Quick Tunnel (`cloudflared tunnel --url tcp://localhost:1433`) có thể không hỗ trợ TCP trực tiếp cho SQL Server, dẫn đến lỗi:
```
Unexpected EOF from the server
Adaptive Server connection failed
```

## Giải pháp

### Giải pháp 1: Dùng Named Tunnel (Khuyến nghị)

#### Bước 1: Đăng nhập Cloudflare
```bash
cloudflared tunnel login
```

#### Bước 2: Tạo Named Tunnel
```bash
cloudflared tunnel create sql-tunnel
```

Output sẽ hiển thị tunnel ID, ví dụ: `abc123def456...`

#### Bước 3: Tạo file config
Tạo file `~/.cloudflared/config.yml`:

```yaml
tunnel: sql-tunnel
credentials-file: /home/YOUR_USERNAME/.cloudflared/abc123def456.json

ingress:
  - hostname: sql-tunnel.your-domain.com
    service: tcp://localhost:1433
  - service: http_status:404
```

**LƯU Ý**: Named tunnel yêu cầu domain. Nếu không có domain, dùng giải pháp 2.

#### Bước 4: Chạy tunnel
```bash
cloudflared tunnel run sql-tunnel
```

### Giải pháp 2: Dùng SSH Tunnel (Đơn giản hơn)

Nếu bạn có quyền truy cập SSH vào máy chạy SQL Server:

#### Trên máy local (có SQL Server):
```bash
ssh -R 1433:localhost:1433 user@render-server
```

#### Trên Render, DB_URL:
```
jdbc:sqlserver://localhost:1433;databaseName=btn;encrypt=true;trustServerCertificate=true
```

### Giải pháp 3: Dùng ngrok với TCP (Cần thẻ)

Nếu có thẻ tín dụng, ngrok hỗ trợ TCP tốt hơn:

```bash
ngrok tcp 1433
```

### Giải pháp 4: Dùng Public IP (Nếu có)

Nếu SQL Server có public IP và firewall cho phép:

1. Mở port 1433 trên firewall
2. Cho phép remote connections trong SQL Server
3. Dùng public IP trực tiếp trong DB_URL

## Kiểm tra Cloudflare Tunnel

Để kiểm tra xem tunnel có hoạt động không:

```bash
# Test kết nối từ máy khác
telnet asian-ltd-flickr-livecam.trycloudflare.com 1433
```

Nếu không kết nối được, tunnel không hỗ trợ TCP.

## Khuyến nghị

**Giải pháp tốt nhất**: Dùng **SSH Tunnel** hoặc **Public IP** nếu có thể.

Nếu không có, có thể cần:
1. Mua domain và dùng Named Tunnel
2. Hoặc dùng ngrok với thẻ tín dụng
3. Hoặc host SQL Server trên cloud (Azure SQL, AWS RDS, etc.)

