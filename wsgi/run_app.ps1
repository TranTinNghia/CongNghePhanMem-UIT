$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

$ROOT_DIR = Split-Path -Parent $SCRIPT_DIR

Write-Host "========================================" -ForegroundColor Green
Write-Host "🚀 Khởi động Production Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

try {
    $null = python -m gunicorn --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Gunicorn not found"
    }
} catch {
    Write-Host "❌ Gunicorn chưa được cài đặt!" -ForegroundColor Red
    Write-Host "   -> Chạy: pip install gunicorn" -ForegroundColor Yellow
    exit 1
}

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

$WORKERS = (Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors * 2 + 1
if (-not $WORKERS) {
    $WORKERS = (Get-CimInstance Win32_Processor | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum * 2 + 1
    if (-not $WORKERS) {
        $WORKERS = 4
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
    python -m gunicorn `
        --config "$SCRIPT_DIR\gunicorn_config_https.py" `
        --bind 0.0.0.0:5000 `
        --keyfile "$SSL_KEY" `
        --certfile "$SSL_CERT" `
        --chdir "$SCRIPT_DIR" `
        --log-level warning `
        wsgi:application
} else {
    Write-Host "🌐 Khởi động HTTP server..." -ForegroundColor Green
    python -m gunicorn `
        --config "$SCRIPT_DIR\gunicorn_config.py" `
        --bind 0.0.0.0:5000 `
        --chdir "$SCRIPT_DIR" `
        wsgi:application
}

