# PhotoX 项目自动启动脚本 (PowerShell版本)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PhotoX 项目自动启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置执行策略
Write-Host "设置PowerShell执行策略..." -ForegroundColor Yellow
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# 获取脚本所在目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 启动后端服务
Write-Host "启动后端服务..." -ForegroundColor Green
$backendPath = Join-Path $scriptPath "photox_backend"
$backendCommand = "cd '$backendPath'; .\venv\Scripts\Activate.ps1; python manage.py makemigrations; python manage.py migrate; python manage.py runserver"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

# 等待3秒让后端启动
Write-Host "等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 启动前端服务
Write-Host "启动前端服务..." -ForegroundColor Green
$frontendPath = Join-Path $scriptPath "photox_frontend"
$frontendCommand = "cd '$frontendPath'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "服务启动完成！" -ForegroundColor Green
Write-Host "后端地址: http://localhost:8000" -ForegroundColor White
Write-Host "前端地址: http://localhost:5173" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 