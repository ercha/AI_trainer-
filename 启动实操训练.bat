@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PORT=8000

echo =============================================
echo  人工智能训练师三级 - 实操训练系统
echo =============================================
echo.
echo 正在启动本地网页服务...
start "AI Trainer Web" /min cmd /c "py -m http.server %PORT%"
timeout /t 2 >nul
start "" "http://127.0.0.1:%PORT%/实操训练系统.html"
echo.
echo 已打开浏览器。
echo 如果没有自动打开，请访问：
echo http://127.0.0.1:%PORT%/实操训练系统.html
echo.
echo 注意：关闭本窗口不会停止已启动的 Web 服务。
pause
