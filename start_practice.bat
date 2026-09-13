@echo off
cd /d "%~dp0"
set "PYW=%~dp0.venv\Scripts\pythonw.exe"

if not exist "%PYW%" (
    powershell -NoProfile -WindowStyle Hidden -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Virtual environment not found. Run install_env.bat first.','AI Trainer') | Out-Null"
    exit /b 1
)

start "" "%PYW%" "%~dp0tray_launcher.py"
exit /b 0
