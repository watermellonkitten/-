@echo off
chcp 65001 >nul
title 薄荷终端助手
cd /d "%~dp0"

echo.
echo ===========================================
echo          薄荷终端助手
echo ===========================================
echo.
echo 选项:
echo   1. 启动程序
echo   2. 配置 API 密钥
echo   3. 退出
echo.
set /p choice="请选择 (1/2/3): "

if "%choice%"=="2" (
    python setup_config.py
    pause
    exit /b
)

if "%choice%"=="3" (
    exit /b
)

python main.py
pause
