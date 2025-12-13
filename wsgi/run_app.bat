@echo off
cd /d "%~dp0"
set "SCRIPT_DIR=%CD%"

cd ..
set "ROOT_DIR=%CD%"
cd /d "%SCRIPT_DIR%"

echo ========================================
echo Starting Production Server (Waitress)
echo ========================================
echo Waitress is a pure WSGI server that works on Windows
echo Note: Gunicorn does not work on Windows (requires Unix)
echo For WSL2/Linux, use: bash run_app.sh
echo.

REM Check if Waitress is installed
python -c "import waitress" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Waitress is not installed!
    echo Please run: pip install waitress
    pause
    exit /b 1
)

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
    echo Note: Waitress has limited HTTPS support on Windows.
    echo Using Hypercorn for HTTPS instead.
    echo.
    REM Use Hypercorn for HTTPS on Windows
    python -c "import hypercorn" 2>nul
    if %errorlevel% equ 0 (
        python -m hypercorn wsgi:application --bind 0.0.0.0:5000 --certfile "%SSL_CERT%" --keyfile "%SSL_KEY%" --keep-alive 5 --graceful-timeout 30 --read-timeout 30
    ) else (
        echo ERROR: Hypercorn is not installed for HTTPS support!
        echo Please run: pip install hypercorn
        echo Or use HTTP instead by running: run_app_waitress.bat
        pause
        exit /b 1
    )
) else (
    echo    Protocol: HTTP
    echo    URL: http://localhost:5000
    echo ========================================
    echo Starting HTTP server...
    python -m waitress --listen=0.0.0.0:5000 --call wsgi:wsgi_application
)

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo CRITICAL ERROR: Server failed to start.
    echo Please check the error message above.
    echo ========================================
)

pause
