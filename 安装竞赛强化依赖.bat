@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"
set "PY=%~dp0.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo ERROR: 未找到 .venv，请先运行 install_env.bat 或 安装环境.bat
    pause
    exit /b 1
)

echo =============================================
echo 竞赛强化依赖：自动检测 NVIDIA GPU / CPU
echo =============================================
echo.
echo [1/3] 检测 GPU 并安装匹配的 PyTorch
"%PY%" "install_torch.py" --auto
if errorlevel 1 goto :fail

echo.
echo [2/3] 安装强化训练依赖
"%PY%" -m pip install -r "competition_advanced_requirements.txt"
if errorlevel 1 goto :fail

echo.
echo [3/3] 验证深度学习及自然语言处理模块
"%PY%" -c "import torch, torchvision, jieba, gensim, requests, nltk, transformers, peft; device='cuda' if torch.cuda.is_available() else 'mps' if hasattr(torch.backends,'mps') and torch.backends.mps.is_available() else 'cpu'; x=torch.ones(2,device=device); assert float(x.sum().cpu())==2; print('torch:',torch.__version__,'CUDA:',torch.version.cuda,'device:',device); print('torchvision:',torchvision.__version__); print('transformers:',transformers.__version__,'peft:',peft.__version__); print('NLP dependencies: OK')"
if errorlevel 1 goto :fail

echo.
echo 安装完成：无显卡设备可使用 CPU 执行入门课程。
pause
exit /b 0

:fail
echo.
echo ERROR: 安装失败，请检查上方错误。驱动不兼容可运行：
echo        .venv\Scripts\python.exe install_torch.py --cpu
pause
exit /b 1
