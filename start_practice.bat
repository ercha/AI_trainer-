@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PORT=7000"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"

if not exist "%VENV_PY%" (
    echo ERROR: Virtual environment was not found.
    echo Run install_env.bat first.
    pause
    exit /b 1
)

"%VENV_PY%" -c "import notebook, pandas, numpy, sklearn" >nul 2>&1
if errorlevel 1 (
    echo ERROR: The virtual environment is incomplete.
    echo Run install_env.bat again.
    pause
    exit /b 1
)

start "AI Trainer Web" /min "%VENV_PY%" "%~dp0serve_practice.py" %PORT%
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 40;$i++){ try { $r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:7000/api/system/status' -TimeoutSec 1; if($r.StatusCode -eq 200){$ok=$true;break} } catch {}; Start-Sleep -Milliseconds 250 }; if($ok){exit 0}else{exit 1}"
if errorlevel 1 (
    echo ERROR: Trainer server failed to start.
    pause
    exit /b 1
)
start "" "http://127.0.0.1:%PORT%/practice.html"
echo Trainer is running at http://127.0.0.1:%PORT%/practice.html
pause
endlocal
