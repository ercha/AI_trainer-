@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo ERROR: 未找到 .venv，请先运行 install_env.bat 或 安装环境.bat
    pause
    exit /b 1
)

echo =============================================
echo 安装竞赛强化训练额外依赖
echo =============================================
echo.
"%PY%" -m pip install -r "competition_advanced_requirements.txt"
if errorlevel 1 goto :fail

echo.
echo 正在验证 PyTorch / torchvision / jieba / gensim / requests...
"%PY%" -c "import torch, torchvision, jieba, gensim, requests; print('torch:', torch.__version__); print('torchvision:', torchvision.__version__); print('jieba/gensim/requests: OK')"
if errorlevel 1 goto :fail

echo.
echo 安装完成
pause
exit /b 0

:fail
echo.
echo 安装失败，请检查上方错误信息
pause
exit /b 1
