@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%PY%" (
    echo 请先运行 安装环境.bat 安装 Python 3.12 虚拟环境。
    pause
    exit /b 1
)
echo 启动 Jupyter Notebook，浏览器中打开 beginner_notebooks 文件夹。
echo 运行期间请勿关闭本窗口。按 Ctrl+C 停止服务。
"%PY%" -m notebook --ServerApp.root_dir="%~dp0" --ServerApp.ip=127.0.0.1
if errorlevel 1 (
    echo Jupyter 启动失败，请检查安装或端口占用。
    pause
    exit /b 1
)
