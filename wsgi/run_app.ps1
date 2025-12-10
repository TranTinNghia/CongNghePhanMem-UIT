# PowerShell script to run the Flask application on Windows
$ErrorActionPreference = "Stop"

# Get script directory
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

# Get root directory (one level up from wsgi)
$ROOT_DIR = Split-Path -Parent $SCRIPT_DIR

Write-Host "========================================" -ForegroundColor Green
Write-Host "🚀 Khởi động Production Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check for --test flag
if ($args -contains "--test") {
    Write-Host "⚠️  Cảnh báo: --test flag không được dùng với production server" -ForegroundColor Yellow
    Write-Host "   -> Sử dụng: bash run_production_test.sh cho test mode" -ForegroundColor Yellow
    exit 1
}

# Check if gunicorn is installed
try {
    $null = Get-Command gunicorn -ErrorAction Stop
} catch {
    Write-Host "❌ Gunicorn chưa được cài đặt!" -ForegroundColor Red
    Write-Host "   -> Chạy: pip install gunicorn" -ForegroundColor Yellow
    exit 1
}

# Check SSL certificates
$SSL_CERT = Join-Path $ROOT_DIR "config\certs\cert.pem"
$SSL_KEY = Join-Path $ROOT_DIR "config\certs\key.pem"
$USE_HTTPS = $false

if ((Test-Path $SSL_CERT) -and (Test-Path $SSL_KEY)) {
    $USE_HTTPS = $true
    Write-Host "✅ SSL certificates được tìm thấy" -ForegroundColor Green
    Write-Host "   Certificate: $SSL_CERT" -ForegroundColor Green
    Write-Host "   Key: $SSL_KEY" -ForegroundColor Green
} else {
    Write-Host "⚠️  SSL certificates không tìm thấy" -ForegroundColor Yellow
    Write-Host "   Server sẽ chạy trên HTTP" -ForegroundColor Yellow
}

# Calculate number of workers (CPU count * 2 + 1)
$WORKERS = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors * 2 + 1
if (-not $WORKERS) {
    # Fallback if WMI query fails
    $WORKERS = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum * 2 + 1
    if (-not $WORKERS) {
        $WORKERS = 4  # Default fallback
    }
}

Write-Host "📊 Cấu hình:" -ForegroundColor Green
Write-Host "   Workers: $WORKERS"
Write-Host "   Port: 5000"
Write-Host "   Working Directory: $SCRIPT_DIR"
if ($USE_HTTPS) {
    Write-Host "   Protocol: HTTPS" -ForegroundColor Green
    Write-Host "   URL: https://localhost:5000" -ForegroundColor Green
} else {
    Write-Host "   Protocol: HTTP" -ForegroundColor Green
    Write-Host "   URL: http://localhost:5000" -ForegroundColor Green
}
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($USE_HTTPS) {
    Write-Host "🔒 Khởi động HTTPS server..." -ForegroundColor Green
    Write-Host "⚠️  Lưu ý: SSL warnings là bình thường với self-signed certificate" -ForegroundColor Yellow
    & gunicorn `
        --config "$SCRIPT_DIR\gunicorn_config_https.py" `
        --bind 0.0.0.0:5000 `
        --keyfile "$SSL_KEY" `
        --certfile "$SSL_CERT" `
        --chdir "$SCRIPT_DIR" `
        --log-level warning `
        wsgi:application
} else {
    Write-Host "🌐 Khởi động HTTP server..." -ForegroundColor Green
    & gunicorn `
        --config "$SCRIPT_DIR\gunicorn_config.py" `
        --bind 0.0.0.0:5000 `
        --chdir "$SCRIPT_DIR" `
        wsgi:application
}

