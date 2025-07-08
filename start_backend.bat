@echo off
chcp 65001 >nul
echo Starting backend service...
echo.

REM Set execution policy
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force"

REM Enter backend directory
cd photox_backend

REM Activate virtual environment
echo Activating virtual environment...
call H:\soft\myphotox\photox_ltb-master\photox_backend\venv311\Scripts\Activate.ps1

REM Check database migrations
echo Checking database migrations...
python manage.py makemigrations
python manage.py migrate

REM Start Django development server
echo Starting Django development server...
python manage.py runserver

pause 