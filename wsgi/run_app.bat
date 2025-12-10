@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

for %%I in ("%SCRIPT_DIR%..") do set ROOT_DIR=%%~fI

echo ========================================
echo 🚀 Khởi động Production Server
echo ========================================

REM Kiểm tra --test flag
echo %* | findstr /C:"--test" >nul
if %errorlevel% == 0 (
    echo ⚠️  Cảnh báo: --test flag không được dùng với production server
    echo    -^> Sử dụng: bash run_production_test.sh cho test mode
    exit /b 1
)

REM Kiểm tra gunicorn
where gunicorn >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Gunicorn chưa được cài đặt!
    echo    -^> Chạy: pip install gunicorn
    exit /b 1
)

set SSL_CERT=%ROOT_DIR%\config\certs\cert.pem
set SSL_KEY=%ROOT_DIR%\config\certs\key.pem
set USE_HTTPS=false

if exist "%SSL_CERT%" if exist "%SSL_KEY%" (
    set USE_HTTPS=true
    echo ✅ SSL certificates được tìm thấy
    echo    Certificate: %SSL_CERT%
    echo    Key: %SSL_KEY%
) else (
    echo ⚠️  SSL certificates không tìm thấy
    echo    Server sẽ chạy trên HTTP
)

REM Tính số workers (CPU count * 2 + 1)
for /f "tokens=*" %%i in ('python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)"') do set WORKERS=%%i

echo 📊 Cấu hình:
echo    Workers: %WORKERS%
echo    Port: 5000
echo    Working Directory: %SCRIPT_DIR%
if "%USE_HTTPS%"=="true" (
    echo    Protocol: HTTPS
    echo    URL: https://localhost:5000
) else (
    echo    Protocol: HTTP
    echo    URL: http://localhost:5000
)
echo ========================================
echo.

if "%USE_HTTPS%"=="true" (
    echo 🔒 Khởi động HTTPS server...
    echo ⚠️  Lưu ý: SSL warnings là bình thường với self-signed certificate
    gunicorn --config "%SCRIPT_DIR%gunicorn_config_https.py" --bind 0.0.0.0:5000 --keyfile "%SSL_KEY%" --certfile "%SSL_CERT%" --chdir "%SCRIPT_DIR%" --log-level warning wsgi:application
) else (
    echo 🌐 Khởi động HTTP server...
    gunicorn --config "%SCRIPT_DIR%gunicorn_config.py" --bind 0.0.0.0:5000 --chdir "%SCRIPT_DIR%" wsgi:application
)

endlocal

