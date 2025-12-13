@echo off
cd /d "%~dp0"
set "SCRIPT_DIR=%CD%"

cd ..
set "ROOT_DIR=%CD%"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo Starting Production Server (Hypercorn)
echo ========================================

echo Hypercorn installed at: User Site-packages
echo.

set "SSL_CERT=%ROOT_DIR%\config\certs\cert.pem"
set "SSL_KEY=%ROOT_DIR%\config\certs\key.pem"
set "USE_HTTPS=false"

if exist "%SSL_CERT%" (
    if exist "%SSL_KEY%" (
        set "USE_HTTPS=true"
        echo SSL certificates found.
    )
)

set "WORKERS=4"
python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)" > temp_workers.txt 2>nul
set /p WORKERS=<temp_workers.txt 2>nul
del temp_workers.txt 2>nul

echo Configuration:
echo    Server: Hypercorn
echo    Workers: %WORKERS%
echo    App Dir: %SCRIPT_DIR%

if "%USE_HTTPS%"=="true" (
    echo    Protocol: HTTPS
    echo    URL: https://localhost:5000
    echo ========================================
    echo Starting HTTPS server...
    python -m hypercorn wsgi:asgi_application --bind 0.0.0.0:5000 --workers %WORKERS% --certfile "%SSL_CERT%" --keyfile "%SSL_KEY%" --keep-alive 5 --graceful-timeout 30 --read-timeout 30 --log-level error
) else (
    echo    Protocol: HTTP
    echo    URL: http://localhost:5000
    echo ========================================
    echo Starting HTTP server...
    python -m hypercorn wsgi:asgi_application --bind 0.0.0.0:5000 --workers %WORKERS% --keep-alive 5 --graceful-timeout 30 --read-timeout 30
)

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo CRITICAL ERROR: Server failed to start.
    echo Please check the error message above.
    echo ========================================
)

pause

