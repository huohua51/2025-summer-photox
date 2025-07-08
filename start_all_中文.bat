@echo off
chcp 65001 >nul
title PhotoX 项目自动启动脚本
echo ========================================
echo PhotoX 项目自动启动脚本
echo ========================================
echo.

REM 设置执行策略
echo 设置PowerShell执行策略...
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force"

REM 启动后端服务（在新窗口中）
echo 启动后端服务...
start "PhotoX 后端服务" cmd /k "cd /d %~dp0photox_backend && call venv\Scripts\activate.bat && python manage.py makemigrations && python manage.py migrate && python manage.py runserver"

REM 等待3秒让后端启动
echo 等待后端服务启动...
timeout /t 3 /nobreak > nul

REM 启动前端服务（在新窗口中）
echo 启动前端服务...
start "PhotoX 前端服务" cmd /k "cd /d %~dp0photox_frontend && npm run dev"

echo.
echo ========================================
echo 服务启动完成！
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:5173
echo ========================================
echo.
echo 按任意键退出此窗口...
pause > nul 