@echo off
chcp 65001 >nul
echo Starting frontend service...
echo.

REM Set execution policy
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force"

REM Enter frontend directory
cd photox_frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

REM Start frontend development server
echo Starting frontend development server...
npm run dev

pause 