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
echo 安装竞赛强化训练额外依赖
echo =============================================
echo.
echo [1/3] 安装 NVIDIA CUDA 13.2 版 PyTorch
echo      目标：torch 2.14.1+cu132 / torchvision 0.29.1+cu132
echo.

"%PY%" -m pip uninstall -y torch torchvision >nul 2>&1
"%PY%" -m pip install --upgrade torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cu132
if errorlevel 1 goto :fail

echo.
echo [2/3] 安装其余竞赛强化依赖
"%PY%" -m pip install -r "competition_advanced_requirements.txt"
if errorlevel 1 goto :fail

echo.
echo [3/3] 验证 CUDA / RTX GPU / 深度学习依赖
"%PY%" -c "import torch, torchvision, jieba, gensim, requests, nltk, transformers, peft; assert '+cpu' not in torch.__version__, '检测到 CPU 版 PyTorch'; assert torch.version.cuda is not None, 'PyTorch 未包含 CUDA'; assert torch.cuda.is_available(), 'CUDA 不可用，请检查 NVIDIA 驱动'; name=torch.cuda.get_device_name(0); cap=torch.cuda.get_device_capability(0); x=torch.randn(1024,1024,device='cuda'); y=x@x; torch.cuda.synchronize(); print('torch:',torch.__version__); print('torchvision:',torchvision.__version__); print('PyTorch CUDA:',torch.version.cuda); print('GPU:',name); print('Compute Capability:',cap); print('CUDA available:',torch.cuda.is_available()); print('GPU tensor test:',float(y[0,0])); print('transformers:',transformers.__version__); print('peft:',peft.__version__); print('jieba/gensim/requests/nltk: OK')"
if errorlevel 1 goto :fail

echo.
echo =============================================
echo CUDA 版竞赛环境安装完成
echo =============================================
pause
exit /b 0

:fail
echo.
echo 安装或 CUDA 验证失败，请检查上方错误信息
pause
exit /b 1
