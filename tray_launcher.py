from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen
import ctypes
import json
import os
import socket
import subprocess
import threading
import time
import webbrowser

import pystray
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PORT = 7000
TRAY_LOCK_PORT = 7010
BASE_URL = f"http://127.0.0.1:{PORT}"
PRACTICE_URL = BASE_URL + "/practice.html"
STATUS_URL = BASE_URL + "/api/system/status"
EXAM_STATUS_URL = BASE_URL + "/api/exam/status"
PYTHON_EXE = ROOT / ".venv" / "Scripts" / "python.exe"
SERVER_SCRIPT = ROOT / "serve_practice.py"
LOG_PATH = ROOT / "_trainer_service.log"

SERVER_PROCESS: subprocess.Popen | None = None
SERVER_PID: int | None = None
LOCK_SOCKET: socket.socket | None = None
LOG_HANDLE = None

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _message(text: str, title: str = "AI Trainer") -> None:
    try:
        ctypes.windll.user32.MessageBoxW(None, text, title, 0x40)
    except Exception:
        pass


def _confirm(text: str, title: str = "AI Trainer") -> bool:
    try:
        # MB_YESNO | MB_ICONWARNING
        return ctypes.windll.user32.MessageBoxW(None, text, title, 0x34) == 6
    except Exception:
        return True


def _get_json(url: str, timeout: float = 1.0) -> dict | None:
    try:
        with urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def _find_listening_pid(port: int) -> int | None:
    try:
        out = subprocess.check_output(
            ["netstat", "-ano", "-p", "tcp"],
            text=True,
            encoding="utf-8",
            errors="ignore",
            creationflags=CREATE_NO_WINDOW,
        )
        suffix = f":{port}"
        for line in out.splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            local_addr, state, pid = parts[1], parts[3].upper(), parts[4]
            if state == "LISTENING" and local_addr.endswith(suffix) and pid.isdigit():
                return int(pid)
    except Exception:
        pass
    return None


def _acquire_single_instance() -> bool:
    global LOCK_SOCKET
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", TRAY_LOCK_PORT))
        s.listen(1)
        LOCK_SOCKET = s
        return True
    except OSError:
        try:
            s.close()
        except Exception:
            pass
        return False


def _server_environment() -> dict[str, str]:
    env = os.environ.copy()
    current = env.get("JUPYTER_CONFIG_PATH", "").strip()
    env["JUPYTER_CONFIG_PATH"] = str(ROOT) + (os.pathsep + current if current else "")
    return env


def _start_server() -> int:
    global SERVER_PROCESS, SERVER_PID, LOG_HANDLE

    status = _get_json(STATUS_URL, timeout=0.6)
    if status and status.get("ok"):
        pid = _find_listening_pid(PORT)
        if pid:
            SERVER_PID = pid
            return pid

    if _port_open(PORT):
        raise RuntimeError(f"端口 {PORT} 已被其他程序占用")

    if not PYTHON_EXE.exists():
        raise RuntimeError("没有找到 .venv\\Scripts\\python.exe，请先运行 install_env.bat")
    if not SERVER_SCRIPT.exists():
        raise RuntimeError("没有找到 serve_practice.py")

    LOG_HANDLE = open(LOG_PATH, "a", encoding="utf-8", errors="replace")
    LOG_HANDLE.write("\n\n=== launcher start %s ===\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    LOG_HANDLE.flush()

    SERVER_PROCESS = subprocess.Popen(
        [str(PYTHON_EXE), str(SERVER_SCRIPT), str(PORT)],
        cwd=str(ROOT),
        env=_server_environment(),
        stdout=LOG_HANDLE,
        stderr=subprocess.STDOUT,
        creationflags=CREATE_NO_WINDOW,
    )
    SERVER_PID = SERVER_PROCESS.pid

    deadline = time.time() + 20
    while time.time() < deadline:
        if SERVER_PROCESS.poll() is not None:
            raise RuntimeError("训练服务启动失败，请查看 _trainer_service.log")
        status = _get_json(STATUS_URL, timeout=0.6)
        if status and status.get("ok"):
            return SERVER_PROCESS.pid
        time.sleep(0.3)

    raise RuntimeError("等待训练服务启动超时，请查看 _trainer_service.log")


def _open_browser(icon=None, item=None) -> None:
    webbrowser.open(PRACTICE_URL, new=2)


def _stop_server_tree() -> None:
    global SERVER_PROCESS, SERVER_PID, LOG_HANDLE

    pid = SERVER_PID
    if pid is None:
        status = _get_json(STATUS_URL, timeout=0.5)
        if status and status.get("ok"):
            pid = _find_listening_pid(PORT)

    if pid:
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
                creationflags=CREATE_NO_WINDOW,
            )
        except Exception:
            pass

    if SERVER_PROCESS:
        try:
            SERVER_PROCESS.wait(timeout=2)
        except Exception:
            pass

    if LOG_HANDLE:
        try:
            LOG_HANDLE.close()
        except Exception:
            pass
        LOG_HANDLE = None


def _exit_app(icon, item=None) -> None:
    exam = _get_json(EXAM_STATUS_URL, timeout=0.6)
    if exam and exam.get("active"):
        if not _confirm(
            "当前有模拟考试正在进行。\n\n退出会关闭训练服务和 Jupyter。未提交的考试不会生成正式评分记录。\n\n确定退出吗？",
            "AI Trainer",
        ):
            return

    _stop_server_tree()
    try:
        if LOCK_SOCKET:
            LOCK_SOCKET.close()
    except Exception:
        pass
    icon.stop()


def _make_icon() -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, 60, 60), radius=14, fill=(37, 99, 235, 255))
    d.rounded_rectangle((15, 11, 49, 53), radius=4, fill=(255, 255, 255, 255))
    d.rectangle((20, 18, 44, 22), fill=(37, 99, 235, 255))
    d.rectangle((20, 28, 44, 32), fill=(148, 163, 184, 255))
    d.rectangle((20, 38, 38, 42), fill=(148, 163, 184, 255))
    d.ellipse((41, 39, 49, 47), fill=(21, 128, 61, 255))
    return img


def _bootstrap(icon: pystray.Icon) -> None:
    icon.visible = True
    try:
        _start_server()
        time.sleep(0.2)
        _open_browser()
        try:
            icon.notify("实操训练系统已启动", "AI Trainer")
        except Exception:
            pass
    except Exception as exc:
        _message(str(exc), "AI Trainer 启动失败")
        icon.stop()


def main() -> None:
    if not _acquire_single_instance():
        webbrowser.open(PRACTICE_URL, new=2)
        return

    icon = pystray.Icon(
        "AITrainerPractical",
        _make_icon(),
        "AI Trainer 实操训练系统",
        menu=pystray.Menu(
            pystray.MenuItem("打开实操训练", _open_browser, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("退出程序", _exit_app),
        ),
    )
    icon.run(setup=lambda i: threading.Thread(target=_bootstrap, args=(i,), daemon=True).start())


if __name__ == "__main__":
    main()
