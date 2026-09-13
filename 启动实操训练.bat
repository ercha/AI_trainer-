@echo off
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"
set "PYW=%~dp0.venv\Scripts\pythonw.exe"

if not exist "%PYW%" (
    powershell -NoProfile -WindowStyle Hidden -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('未找到虚拟环境，请先运行 install_env.bat 或 安装环境.bat。','AI Trainer') | Out-Null"
    exit /b 1
)

"%PY%" -c "import pystray, PIL" >nul 2>&1
if errorlevel 1 (
    powershell -NoProfile -WindowStyle Hidden -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('缺少托盘组件。git pull 后请重新运行 install_env.bat 或 安装环境.bat。','AI Trainer') | Out-Null"
    exit /b 1
)

start "" "%PYW%" "%~dp0tray_launcher.py"
exit /b 0
