@echo off
REM AutoML Platform - Quick Start Script for Windows

setlocal enabledelayedexpansion

echo.
echo ==================================
echo    AutoML Platform - Quick Start
echo ==================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Creating .env from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo OK: .env created
        echo Warning: Please edit .env and add your Google API key!
    ) else (
        echo Error: .env.example not found
        pause
        exit /b 1
    )
)

REM Check if LLM_API_KEY is set
findstr /M "LLM_API_KEY" .env > nul
if errorlevel 1 (
    echo Error: LLM_API_KEY not configured in .env
    echo Please edit .env and add your Google API key from https://ai.google.dev
    pause
    exit /b 1
)

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo OK: Python %PYTHON_VERSION% found

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo OK: Node %NODE_VERSION% found

REM Setup backend
echo.
echo Setting up backend...
if not exist "backend" (
    echo Error: backend directory not found
    pause
    exit /b 1
)

if not exist "backend\requirements.txt" (
    echo Error: backend\requirements.txt not found
    pause
    exit /b 1
)

echo Installing Python dependencies...
cd backend
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo Error: Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)
echo OK: Dependencies installed
cd ..

REM Setup frontend
echo.
echo Setting up frontend...
if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install -q
    if errorlevel 1 (
        echo Error: Failed to install Node dependencies
        pause
        exit /b 1
    )
    echo OK: Dependencies installed
) else (
    echo OK: Node dependencies already installed
)

REM Success message
echo.
echo ==================================
echo    Setup Complete!
echo ==================================
echo.
echo Starting servers...
echo.

REM Start backend in a new window
echo Starting Backend Server (port 8000)...
cd backend
start "AutoML Backend" python main.py
cd ..

REM Wait a bit for backend to start
timeout /t 2 /nobreak

REM Start frontend in a new window
echo Starting Frontend Server (port 3000)...
start "AutoML Frontend" cmd /k "npm run dev"

REM Wait for user to close
echo.
echo Servers are starting...
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - Swagger Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C in either window to stop the servers.
echo Close this window to exit.
pause
