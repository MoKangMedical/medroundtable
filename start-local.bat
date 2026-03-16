@echo off
chcp 65001 >nul
echo 🚀 MedRoundTable 本地启动
echo ==========================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请安装 Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python 已安装

:: 进入 frontend 目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%frontend"

echo 📁 准备前端文件...
echo 🌐 启动本地服务器...
echo.
echo 📍 本地访问: http://localhost:8080
echo 📱 局域网访问: http://%computername%:8080
echo.
echo 按 Ctrl+C 停止服务
echo.

:: 启动服务器
python -m http.server 8080

pause
