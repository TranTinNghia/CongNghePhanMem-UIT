@echo off
cd /d "%~dp0"
set "SCRIPT_DIR=%CD%"

cd ..
set "ROOT_DIR=%CD%"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo Starting Production Server (Waitress)
echo ========================================
echo Waitress is a pure WSGI server that works well on Windows
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

echo Configuration:
echo    Server: Waitress
echo    App Dir: %SCRIPT_DIR%

if "%USE_HTTPS%"=="true" (
    echo    Protocol: HTTPS
    echo    URL: https://localhost:5000
    echo ========================================
    echo Starting HTTPS server...
    echo Note: Waitress SSL support requires additional configuration.
    echo Consider using Gunicorn or Hypercorn for HTTPS on Windows.
    python -m waitress --listen=0.0.0.0:5000 --call wsgi:application
) else (
    echo    Protocol: HTTP
    echo    URL: http://localhost:5000
    echo ========================================
    echo Starting HTTP server...
    python -m waitress --listen=0.0.0.0:5000 --call wsgi:application
)

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo CRITICAL ERROR: Server failed to start.
    echo Please check the error message above.
    echo ========================================
)

pause

