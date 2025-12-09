#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR/certs"

echo "Tạo SSL certificate cho development..."

mkdir -p "$CERTS_DIR"

# Tạo private key
openssl genrsa -out "$CERTS_DIR/key.pem" 2048

# Tạo config file cho certificate với Subject Alternative Names
CONFIG_FILE="$CERTS_DIR/cert.conf"
cat > "$CONFIG_FILE" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=VN
ST=HoChiMinh
L=HoChiMinh
O=Development
CN=localhost

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
IP.1 = 127.0.0.1
IP.2 = ::1
EOF

# Tạo certificate request với config
openssl req -new -key "$CERTS_DIR/key.pem" -out "$CERTS_DIR/csr.pem" -config "$CONFIG_FILE"

# Tạo self-signed certificate với extensions
openssl x509 -req -days 365 -in "$CERTS_DIR/csr.pem" -signkey "$CERTS_DIR/key.pem" \
    -out "$CERTS_DIR/cert.pem" -extensions v3_req -extfile "$CONFIG_FILE"

# Cleanup
rm "$CERTS_DIR/csr.pem"
rm "$CONFIG_FILE"

echo "✅ Đã tạo SSL certificate thành công!"
echo "   - Private key: $CERTS_DIR/key.pem"
echo "   - Certificate: $CERTS_DIR/cert.pem"
echo ""
echo "⚠️  Lưu ý: Đây là self-signed certificate, trình duyệt sẽ cảnh báo."
echo "   Để bỏ qua cảnh báo, click 'Advanced' -> 'Proceed to localhost'"
