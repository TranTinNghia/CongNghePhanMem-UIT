#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ROOT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Khởi động Production Server${NC}"
echo -e "${GREEN}========================================${NC}"

if ! command -v gunicorn &> /dev/null; then
    echo -e "${RED}❌ Gunicorn chưa được cài đặt!${NC}"
    echo -e "${YELLOW}   -> Chạy: pip install gunicorn${NC}"
    exit 1
fi

SSL_CERT="$ROOT_DIR/config/certs/cert.pem"
SSL_KEY="$ROOT_DIR/config/certs/key.pem"
USE_HTTPS=false

if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    USE_HTTPS=true
    echo -e "${GREEN}✅ SSL certificates được tìm thấy${NC}"
    echo -e "${GREEN}   Certificate: $SSL_CERT${NC}"
    echo -e "${GREEN}   Key: $SSL_KEY${NC}"
else
    echo -e "${YELLOW}⚠️  SSL certificates không tìm thấy${NC}"
    echo -e "${YELLOW}   Server sẽ chạy trên HTTP${NC}"
fi

WORKERS=$(python3 -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")

echo -e "${GREEN}📊 Cấu hình:${NC}"
echo -e "   Workers: $WORKERS"
echo -e "   Port: 5000"
echo -e "   Working Directory: $SCRIPT_DIR"
if [ "$USE_HTTPS" = true ]; then
    echo -e "   Protocol: HTTPS"
    echo -e "   URL: https://localhost:5000"
else
    echo -e "   Protocol: HTTP"
    echo -e "   URL: http://localhost:5000"
fi
echo -e "${GREEN}========================================${NC}"
echo ""

if [ "$USE_HTTPS" = true ]; then
    echo -e "${GREEN}🔒 Khởi động HTTPS server...${NC}"
    echo -e "${YELLOW}⚠️  Lưu ý: SSL warnings là bình thường với self-signed certificate${NC}"
    gunicorn \
        --config "$SCRIPT_DIR/gunicorn_config_https.py" \
        --bind 0.0.0.0:5000 \
        --keyfile "$SSL_KEY" \
        --certfile "$SSL_CERT" \
        --chdir "$SCRIPT_DIR" \
        --log-level warning \
        wsgi:wsgi_application
else
    echo -e "${GREEN}🌐 Khởi động HTTP server...${NC}"
    gunicorn \
        --config "$SCRIPT_DIR/gunicorn_config.py" \
        --bind 0.0.0.0:5000 \
        --chdir "$SCRIPT_DIR" \
        wsgi:wsgi_application
fi
