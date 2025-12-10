@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI"

echo ========================================
echo Starting Production Server
echo ========================================

REM Check gunicorn
python -m gunicorn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Gunicorn is not installed!
    echo Run: pip install gunicorn
    exit /b 1
)

set "SSL_CERT=%ROOT_DIR%\config\certs\cert.pem"
set "SSL_KEY=%ROOT_DIR%\config\certs\key.pem"
set "USE_HTTPS=false"

if exist "%SSL_CERT%" (
    if exist "%SSL_KEY%" (
        set "USE_HTTPS=true"
        echo SSL certificates found
        echo Certificate: %SSL_CERT%
        echo Key: %SSL_KEY%
    )
)

if "%USE_HTTPS%"=="false" (
    echo WARNING: SSL certificates not found
    echo Server will run on HTTP
)

REM Calculate number of workers
for /f "tokens=*" %%i in ('python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)"') do set "WORKERS=%%i"

echo Configuration:
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
    echo Starting HTTPS server...
    echo NOTE: SSL warnings are normal with self-signed certificate
    python -m gunicorn --config "%SCRIPT_DIR%gunicorn_config_https.py" --bind 0.0.0.0:5000 --keyfile "%SSL_KEY%" --certfile "%SSL_CERT%" --chdir "%SCRIPT_DIR%" --log-level warning wsgi:application
) else (
    echo Starting HTTP server...
    python -m gunicorn --config "%SCRIPT_DIR%gunicorn_config.py" --bind 0.0.0.0:5000 --chdir "%SCRIPT_DIR%" wsgi:application
)

endlocal
