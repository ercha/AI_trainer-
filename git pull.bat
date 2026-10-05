@echo off
cd /d "%~dp0"

echo 正在执行 git pull...
git pull

if errorlevel 0 (
    echo.
    echo git pull 成功
) else (
    echo.
    echo git pull 失败
)

pause