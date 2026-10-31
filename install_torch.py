#!/usr/bin/env python3
"""为竞赛 A-E 的 PyTorch 练习安装合适运行时。

requirements.txt 是静态依赖清单，无法执行显卡检测；本脚本在安装时选择官方 wheel。
用法：
    python install_torch.py --auto
    python install_torch.py --cpu
    python install_torch.py --gpu
    python install_torch.py --auto --dry-run
"""
from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys

TORCH_VERSION = "2.14.1"
VISION_VERSION = "0.29.1"
CUDA_INDEX = "https://download.pytorch.org/whl/cu132"
CPU_INDEX = "https://download.pytorch.org/whl/cpu"


def detect_nvidia() -> tuple[bool, str]:
    """使用驱动附带的 nvidia-smi 发现可见的 NVIDIA GPU，不依赖先安装 torch。"""
    exe = shutil.which("nvidia-smi")
    if not exe:
        return False, "未找到 nvidia-smi（可能没有 NVIDIA GPU 或尚未安装驱动）"
    try:
        result = subprocess.run(
            [exe, "-L"], capture_output=True, text=True, errors="replace",
            timeout=15, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"nvidia-smi 无法运行：{exc}"
    lines = [s.strip() for s in result.stdout.splitlines() if s.strip().startswith("GPU ")]
    if result.returncode != 0 or not lines:
        return False, (result.stderr.strip() or "nvidia-smi 没有发现可用 NVIDIA GPU")
    return True, "；".join(lines)


def choose_backend(mode: str, system: str, has_nvidia: bool) -> str:
    if mode == "cpu":
        return "cpu"
    if mode == "gpu":
        if system == "Darwin":
            return "mps"
        if not has_nvidia:
            raise RuntimeError("强制 GPU 模式要求 NVIDIA GPU 和正确安装的驱动（macOS 使用 MPS）")
        return "cuda"
    if system == "Darwin":
        return "mps"  # 通过 PyPI 安装官方 macOS wheel，可能可使用 Apple MPS。
    return "cuda" if has_nvidia else "cpu"


def verify(backend: str) -> tuple[bool, str]:
    """使用独立 Python 子进程验证包、实际张量运算和 GPU 可用性。"""
    script = r"""
import torch, torchvision
assert torch.__version__.split('+')[0] == '2.14.1', torch.__version__
assert torchvision.__version__.split('+')[0] == '0.29.1', torchvision.__version__
backend = __import__('sys').argv[1]
if backend == 'cuda':
    assert torch.version.cuda is not None, '安装的是非 CUDA 版本'
    assert torch.cuda.is_available(), 'CUDA 不可用，请检查 NVIDIA 驱动兼容性'
    device = torch.device('cuda')
elif backend == 'mps':
    # 部分旧版 Mac 不支持 MPS，允许使用同一官方 macOS wheel 的 CPU 计算。
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
else:
    assert torch.version.cuda is None, 'CPU 环境误装 CUDA wheel'
    device = torch.device('cpu')
x = torch.tensor([2.0, 3.0], device=device)
assert float((x * 2).sum().cpu()) == 10.0
print('torch =', torch.__version__)
print('torchvision =', torchvision.__version__)
print('backend =', backend, 'actual_device =', device)
if device.type == 'cuda':
    print('GPU =', torch.cuda.get_device_name(0))
"""
    result = subprocess.run(
        [sys.executable, "-c", script, backend],
        capture_output=True, text=True, errors="replace", check=False,
    )
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def install(backend: str, *, force: bool = False) -> None:
    ok, info = verify(backend)
    if ok and not force:
        print("已安装匹配的 PyTorch，跳过重复下载。")
        print(info)
        return
    packages = [f"torch=={TORCH_VERSION}", f"torchvision=={VISION_VERSION}"]
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    if force:
        cmd.append("--force-reinstall")
    elif info:
        # 相同的公共版本号，CPU 与 CUDA 本地版本可能被 pip 视为满足要求。
        # 先移除不兼容的 wheel，保证切换版本确实生效。
        old = subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision"],
            check=False,
        )
        if old.returncode != 0:
            raise RuntimeError("无法清理不匹配的旧版 PyTorch")
    if backend == "cuda":
        cmd += ["--index-url", CUDA_INDEX]
    elif backend == "cpu":
        cmd += ["--index-url", CPU_INDEX]
    # macOS 使用 PyPI 的 macOS wheel，其运行时可自动选择 MPS/CPU。
    cmd += packages
    print("安装来源：", CUDA_INDEX if backend == "cuda" else CPU_INDEX if backend == "cpu" else "PyPI")
    subprocess.run(cmd, check=True)
    ok, info = verify(backend)
    print(info)
    if not ok:
        raise RuntimeError("安装完成但运行测试失败；请检查驱动，并尝试 python install_torch.py --cpu")
    print("PyTorch 验证通过。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="自动检测 NVIDIA GPU 并选择 PyTorch CPU/CUDA 版本")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--auto", action="store_true", help="默认：检测 NVIDIA GPU；Mac 使用官方 MPS/CPU wheel")
    group.add_argument("--cpu", action="store_true", help="强制安装 CPU 版")
    group.add_argument("--gpu", action="store_true", help="要求 GPU 版，无 NVIDIA GPU 时直接报错")
    parser.add_argument("--dry-run", action="store_true", help="仅输出检测结果，不安装")
    parser.add_argument("--force", action="store_true", help="重新安装即使版本已匹配")
    args = parser.parse_args(argv)
    system = platform.system()
    has_nvidia, detail = detect_nvidia()
    print("操作系统：", system)
    print("设备检测：", detail)
    mode = "cpu" if args.cpu else "gpu" if args.gpu else "auto"
    try:
        backend = choose_backend(mode, system, has_nvidia)
        print("选择运行时：", backend.upper())
        if args.dry_run:
            return 0
        install(backend, force=args.force)
        return 0
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
