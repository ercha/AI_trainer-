@echo off
setlocal
cd /d "%~dp0"
set "PORT=7000"
set "PY_CMD="

where py >nul 2>&1
if not errorlevel 1 set "PY_CMD=py"

if not defined PY_CMD (
    where python >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo =============================================
    echo AI Trainer - Practical Training System
    echo =============================================
    echo.
    echo ERROR: Python was not found in PATH.
    echo Please install Python or add Python to PATH, then run this file again.
    echo.
    pause
    exit /b 1
)

echo =============================================
echo AI Trainer - Practical Training System
echo =============================================
echo.
echo Python command: %PY_CMD%
echo Starting local web server on 127.0.0.1:%PORT% ...

if /i "%PY_CMD%"=="py" (
    start "AI Trainer Web" /min py serve_practice.py %PORT%
) else (
    start "AI Trainer Web" /min python serve_practice.py %PORT%
)

echo Waiting for web server...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ok=$false; for($i=0;$i -lt 20;$i++){ try { $r=Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:7000/practice.html' -TimeoutSec 1; if($r.StatusCode -eq 200){$ok=$true;break} } catch {}; Start-Sleep -Milliseconds 300 }; if($ok){exit 0}else{exit 1}"

if errorlevel 1 (
    echo.
    echo ERROR: The web server did not start correctly.
    echo Try this command manually in this folder:
    echo     %PY_CMD% serve_practice.py %PORT%
    echo Then open:
    echo     http://127.0.0.1:%PORT%/practice.html
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
echo Markdown answer files are served as UTF-8.
pause
endlocal
