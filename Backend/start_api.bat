@echo off
echo ============================================
echo Multi-Agent API Server Startup
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

:: Display Python version
echo Using Python:
python --version
echo.

:: Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and add your API keys
    echo.
    pause
    exit /b 1
)

:: Install/verify dependencies
echo Checking dependencies...
python -m pip install -q flask flask-cors langsmith python-dotenv
if errorlevel 1 (
    echo WARNING: Some dependencies may not have installed correctly
    echo Continuing anyway...
)
echo.

echo Starting API server...
echo.
echo Server will be available at: http://localhost:5000
echo LangSmith tracing: ENABLED
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python api_server.py

pause
