#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ROOT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🧪 Khởi động Test Server (WSGI)${NC}"
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
else
    echo -e "${YELLOW}⚠️  SSL certificates không tìm thấy, chạy HTTP${NC}"
fi

WORKERS=2

echo -e "${GREEN}📊 Cấu hình:${NC}"
echo -e "   Workers: $WORKERS"
echo -e "   Port: 5001"
echo -e "   Mode: TEST"
echo -e "   Working Directory: $SCRIPT_DIR"
if [ "$USE_HTTPS" = true ]; then
    echo -e "   Protocol: HTTPS"
    echo -e "   URL: https://localhost:5001"
else
    echo -e "   Protocol: HTTP"
    echo -e "   URL: http://localhost:5001"
fi
echo -e "${GREEN}========================================${NC}"
echo ""

export TEST_MODE=true

if [ "$USE_HTTPS" = true ]; then
    echo -e "${GREEN}🔒 Khởi động HTTPS test server...${NC}"
    echo -e "${YELLOW}⚠️  Lưu ý: SSL warnings là bình thường với self-signed certificate${NC}"
    gunicorn \
        --bind 0.0.0.0:5001 \
        --workers $WORKERS \
        --timeout 30 \
        --keyfile "$SSL_KEY" \
        --certfile "$SSL_CERT" \
        --access-logfile - \
        --error-logfile - \
        --log-level warning \
        --chdir "$SCRIPT_DIR" \
        wsgi:application
else
    echo -e "${GREEN}🌐 Khởi động HTTP test server...${NC}"
    gunicorn \
        --bind 0.0.0.0:5001 \
        --workers $WORKERS \
        --timeout 30 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --chdir "$SCRIPT_DIR" \
        wsgi:application
fi
