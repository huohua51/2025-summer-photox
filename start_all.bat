@echo off
chcp 65001 >nul
echo ========================================
echo PhotoX Project Auto Start Script
echo ========================================
echo.

REM Set execution policy
echo Setting PowerShell execution policy...
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force"

REM Start backend service (in new window)
echo Starting backend service...
start "PhotoX Backend" cmd /k "cd /d %~dp0photox_backend && call H:\soft\myphotox\photox_ltb-master\photox_backend\venv311\Scripts\activate.bat && python manage.py makemigrations && python manage.py migrate && python manage.py runserver"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend service (in new window)
echo Starting frontend service...
start "PhotoX Frontend" cmd /k "cd /d %~dp0photox_frontend && npm run dev"

echo.
echo ========================================
echo Services started successfully!
echo Backend URL: http://localhost:8000
echo Frontend URL: http://localhost:5173
echo ========================================
echo.
echo Press any key to exit...
pause > nul 