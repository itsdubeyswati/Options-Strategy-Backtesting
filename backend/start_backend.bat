@echo off
echo ============================================
echo  Options Strategy Backtesting Platform
echo  Backend Setup and Launch Script
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

:: Navigate to backend directory
echo [1/6] Navigating to backend directory...
cd /d "C:\Users\swati\Desktop\Projects\Options Strategy Backtesting\backend"

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/6] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/6] Virtual environment already exists
)

:: Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo [4/6] Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

:: Set environment variables
echo [5/6] Setting up environment...
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Please edit .env file with your database credentials
    echo.
)

:: Start the FastAPI server
echo [6/6] Starting FastAPI server...
echo.
echo ✅ Backend server starting on http://localhost:8000
echo ✅ API documentation available at http://localhost:8000/docs
echo ✅ Alternative docs at http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the server
echo ============================================
echo.

python run.py

pause
