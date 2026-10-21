@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo ERROR: 未找到 .venv，请先运行 install_env.bat
    pause
    exit /b 1
)

"%PY%" "%~dp0验证竞赛强化题.py"
if errorlevel 1 (
    echo.
    echo 验证失败，请查看上方错误
    pause
    exit /b 1
)

echo.
echo 25 道竞赛强化题本地验证通过
pause
