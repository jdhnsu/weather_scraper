@echo off
chcp 65001 >nul
echo ========================================
echo   WeatherScrape Pro - 启动程序
echo ========================================
echo.

cd /d "%~dp0src"

echo 正在检查依赖...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo [警告] 未检测到PyQt5，正在安装...
    pip install PyQt5 pymysql requests
    echo.
)

echo 正在启动程序...
python main.py

pause
