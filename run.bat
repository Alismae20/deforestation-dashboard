@echo off
REM Deforestation Dashboard - Windows Quick Start Script

echo.
echo ========================================
echo  Deforestation Dashboard - Windows
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    echo Download from: https://www.python.org/
    pause
    exit /b 1
)

REM Check if we're in the project directory
if not exist "requirements.txt" (
    echo ERROR: Not in project directory
    echo Please run this script from: C:\Users\aliscia\deforestation-dashboard\
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Starting servers...
echo.
echo Remember:
echo   - Backend will run on http://localhost:5000
echo   - Frontend will run on http://localhost:8000
echo   - Browser will open automatically
echo   - Press Ctrl+C to stop servers
echo.

REM Start backend
start "Deforestation Dashboard - Backend" cmd /k "cd backend && python app.py"

REM Wait for backend to start
timeout /t 3 /nobreak

REM Start frontend
start "Deforestation Dashboard - Frontend" cmd /k "cd frontend && python app.py"

REM Wait for frontend to start
timeout /t 2 /nobreak

REM Open browser
start http://localhost:8000

echo.
echo Dashboard is starting...
echo Open browser: http://localhost:8000
echo.
pause
