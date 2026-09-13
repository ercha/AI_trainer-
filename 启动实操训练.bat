@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PORT=7000"
set "VENV_PY=%~dp0.venv\Scripts\python.exe"

echo =============================================
echo AI Trainer - Practical Training System
echo =============================================
echo.

if not exist "%VENV_PY%" (
    echo ERROR: Virtual environment was not found.
    echo Run install_env.bat first.
    echo.
    pause
    exit /b 1
)

"%VENV_PY%" -c "import notebook, pandas, numpy, sklearn" >nul 2>&1
if errorlevel 1 (
    echo ERROR: The virtual environment is incomplete.
    echo Run install_env.bat again.
    echo.
    pause
    exit /b 1
)

echo Python: %VENV_PY%
echo Starting trainer on http://127.0.0.1:%PORT% ...
start "AI Trainer Web" /min "%VENV_PY%" "%~dp0serve_practice.py" %PORT%

echo Waiting for web server...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 40;$i++){ try { $r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:7000/api/system/status' -TimeoutSec 1; if($r.StatusCode -eq 200){$ok=$true;break} } catch {}; Start-Sleep -Milliseconds 250 }; if($ok){exit 0}else{exit 1}"

if errorlevel 1 (
    echo.
    echo ERROR: The trainer server did not start correctly.
    echo Try this command manually:
    echo     "%VENV_PY%" "%~dp0serve_practice.py" %PORT%
    echo.
    pause
    exit /b 1
)

echo Web server is ready.
start "" "http://127.0.0.1:%PORT%/practice.html"
echo.
echo Browser opened:
echo http://127.0.0.1:%PORT%/practice.html
echo.
echo Jupyter Notebook starts automatically on port 7001 when an exam begins.
echo Keep the minimized server window running while practicing.
echo.
pause
endlocal
