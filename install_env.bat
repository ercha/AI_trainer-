@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo =============================================
echo AI Trainer - Python 3.12 Environment Installer
echo =============================================
echo.

set "PY_CMD="

where py >nul 2>&1
if not errorlevel 1 (
    py -3.12 -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,12) else 1)" >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py -3.12"
)

if not defined PY_CMD (
    where python >nul 2>&1
    if not errorlevel 1 (
        python -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3,12) else 1)" >nul 2>&1
        if not errorlevel 1 set "PY_CMD=python"
    )
)

if not defined PY_CMD (
    echo ERROR: Python 3.12 was not found.
    echo Install Python 3.12 and make sure the Python Launcher ^(py^) or python.exe is available in PATH.
    echo.
    pause
    exit /b 1
)

echo Python command: %PY_CMD%

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment: .venv
    %PY_CMD% -m venv ".venv"
    if errorlevel 1 goto :fail
) else (
    echo Existing virtual environment found: .venv
)

echo.
echo Upgrading pip / setuptools / wheel...
".venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :fail

echo.
echo Installing requirements.txt...
".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto :fail

echo.
echo Verifying Jupyter Notebook environment...
".venv\Scripts\python.exe" -c "import sys, notebook, jupyter_server, ipykernel, nbformat, numpy, pandas, sklearn; print('Python:', sys.version.split()[0]); print('Notebook:', notebook.__version__); print('pandas:', pandas.__version__); print('numpy:', numpy.__version__); print('scikit-learn:', sklearn.__version__)"
if errorlevel 1 goto :fail

echo.
echo =============================================
echo Installation completed successfully.
echo Next: run [start_practice.bat] or the Chinese launcher.
echo =============================================
echo.
pause
exit /b 0

:fail
echo.
echo ERROR: Installation failed.
echo Review the error above, then run this installer again.
echo.
pause
exit /b 1
