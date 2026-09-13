from __future__ import annotations

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import quote, urlparse
import importlib.util
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级上网素材"
EXAM_ROOT = ROOT / "_exam_workspace"
HISTORY_ROOT = ROOT / "_exam_history"
JUPYTER_PORT = 7001

# Current practical-training page exposes these four questions first.
# More question profiles can be added later without changing the API shape.
QUESTION_PROFILES = {
    "1.1.1": {
        "duration": 30,
        "checks": [
            ("读取 CSV", ("pd.read_csv",)),
            ("条件生成风险等级", ("np.where",)),
            ("分类计数", ("value_counts",)),
            ("区间切分", ("pd.cut",)),
            ("分组统计", ("groupby",)),
        ],
    },
    "1.1.2": {
        "duration": 30,
        "checks": [
            ("读取 CSV", ("pd.read_csv",)),
            ("分组聚合", ("groupby", "agg")),
            ("条件筛选", ("isin",)),
            ("缺失值填充", ("fillna", "ffill", "bfill")),
            ("删除列", ("drop",)),
            ("保存 CSV", ("to_csv",)),
        ],
    },
    "2.1.1": {
        "duration": 20,
        "checks": [
            ("读取 CSV", ("pd.read_csv",)),
            ("缺失值统计", ("isnull", "isna")),
            ("删除缺失值", ("dropna",)),
            ("类型转换", ("pd.to_numeric",)),
            ("标准化", ("StandardScaler",)),
            ("训练测试集划分", ("train_test_split",)),
            ("保存 CSV", ("to_csv",)),
        ],
    },
    "2.2.1": {
        "duration": 20,
        "checks": [
            ("读取 CSV", ("pd.read_csv",)),
            ("训练测试集划分", ("train_test_split",)),
            ("标准化", ("StandardScaler",)),
            ("Logistic 回归", ("LogisticRegression",)),
            ("模型训练", (".fit(",)),
            ("模型预测", (".predict(",)),
            ("准确率", ("accuracy_score",)),
        ],
    },
}

LOCK = threading.RLock()
ACTIVE_SESSION = None
LAST_RESULT = None


class ApiError(Exception):
    def __init__(self, status: int, message: str, extra: dict | None = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.extra = extra or {}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.35):
            return True
    except OSError:
        return False


def _safe_session(session: dict | None) -> dict | None:
    if not session:
        return None
    now = _now_ms()
    return {
        "id": session["id"],
        "qid": session["qid"],
        "workspace": str(session["workspace"]),
        "notebook": session["notebook"],
        "duration_minutes": session["duration_minutes"],
        "started_at_ms": session["started_at_ms"],
        "deadline_ms": session["deadline_ms"],
        "remaining_seconds": max(0, int((session["deadline_ms"] - now) / 1000)),
        "expired": now >= session["deadline_ms"],
        "jupyter_url": session.get("jupyter_url", ""),
        "submitted": bool(session.get("submitted")),
    }


def _stop_jupyter(session: dict | None) -> None:
    if not session:
        return
    proc = session.get("_process")
    if proc and proc.poll() is None:
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=8,
                )
            else:
                proc.terminate()
                proc.wait(timeout=8)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    log_handle = session.get("_log_handle")
    if log_handle:
        try:
            log_handle.close()
        except Exception:
            pass


def _read_log_tail(path: Path, max_chars: int = 5000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return text[-max_chars:]
    except Exception:
        return ""


def _list_relative_files(folder: Path) -> set[str]:
    result = set()
    for p in folder.rglob("*"):
        if p.is_file():
            result.add(p.relative_to(folder).as_posix())
    return result


def _start_exam(qid: str) -> dict:
    global ACTIVE_SESSION

    if not re.fullmatch(r"\d+\.\d+\.\d+", qid or ""):
        raise ApiError(400, "题号格式不正确")

    source = SOURCE_ROOT / qid
    if not source.is_dir():
        raise ApiError(404, f"没有找到题目素材目录：{qid}")

    if importlib.util.find_spec("notebook") is None:
        raise ApiError(500, "当前 Python 环境未安装 Jupyter Notebook，请先运行 安装环境.bat")

    with LOCK:
        if ACTIVE_SESSION and not ACTIVE_SESSION.get("submitted"):
            proc = ACTIVE_SESSION.get("_process")
            if proc and proc.poll() is None:
                raise ApiError(409, "已有模拟考试正在进行，请先提交当前考试", {
                    "session": _safe_session(ACTIVE_SESSION)
                })
            _stop_jupyter(ACTIVE_SESSION)
            ACTIVE_SESSION = None

        if _port_open(JUPYTER_PORT):
            raise ApiError(
                409,
                f"Jupyter 端口 {JUPYTER_PORT} 已被占用。请关闭其他 Jupyter 服务后再开始考试。",
            )

        EXAM_ROOT.mkdir(parents=True, exist_ok=True)
        HISTORY_ROOT.mkdir(parents=True, exist_ok=True)

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{stamp}_{qid}"
        workspace = EXAM_ROOT / session_id
        suffix = 1
        while workspace.exists():
            workspace = EXAM_ROOT / f"{session_id}_{suffix}"
            suffix += 1
        session_id = workspace.name

        shutil.copytree(source, workspace)
        initial_files = _list_relative_files(workspace)

        notebook = workspace / f"{qid}.ipynb"
        if not notebook.exists():
            notebooks = sorted(workspace.glob("*.ipynb"))
            if not notebooks:
                shutil.rmtree(workspace, ignore_errors=True)
                raise ApiError(404, f"素材目录中没有找到 .ipynb：{qid}")
            notebook = notebooks[0]

        profile = QUESTION_PROFILES.get(qid, {})
        duration = int(profile.get("duration", 30))
        started = _now_ms()
        deadline = started + duration * 60 * 1000

        meta = {
            "id": session_id,
            "qid": qid,
            "duration_minutes": duration,
            "started_at_ms": started,
            "deadline_ms": deadline,
            "notebook": notebook.name,
        }
        (workspace / "_exam_session.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        log_path = workspace / "jupyter.log"
        log_handle = open(log_path, "w", encoding="utf-8", errors="replace")
        cmd = [
            sys.executable,
            "-m",
            "notebook",
            "--no-browser",
            "--ServerApp.ip=127.0.0.1",
            f"--ServerApp.port={JUPYTER_PORT}",
            "--ServerApp.port_retries=0",
            "--ServerApp.open_browser=False",
            f"--ServerApp.root_dir={workspace}",
            "--ServerApp.allow_remote_access=False",
            "--IdentityProvider.token=",
            "--ServerApp.password=",
        ]
        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        proc = subprocess.Popen(
            cmd,
            cwd=workspace,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )

        session = {
            **meta,
            "workspace": workspace,
            "initial_files": initial_files,
            "jupyter_url": f"http://127.0.0.1:{JUPYTER_PORT}/tree/{quote(notebook.name)}",
            "submitted": False,
            "_process": proc,
            "_log_handle": log_handle,
            "_log_path": log_path,
        }
        ACTIVE_SESSION = session

    # Wait outside the lock so status requests are not blocked for long.
    deadline_wait = time.time() + 25
    while time.time() < deadline_wait:
        if proc.poll() is not None:
            tail = _read_log_tail(log_path)
            with LOCK:
                _stop_jupyter(session)
                if ACTIVE_SESSION is session:
                    ACTIVE_SESSION = None
            raise ApiError(500, "Jupyter Notebook 启动失败", {"log": tail})
        if _port_open(JUPYTER_PORT):
            return _safe_session(session)
        time.sleep(0.35)

    tail = _read_log_tail(log_path)
    with LOCK:
        _stop_jupyter(session)
        if ACTIVE_SESSION is session:
            ACTIVE_SESSION = None
    raise ApiError(500, "等待 Jupyter Notebook 启动超时", {"log": tail})


def _analyze_notebook(session: dict) -> dict:
    workspace: Path = session["workspace"]
    notebook_path = workspace / session["notebook"]
    if not notebook_path.exists():
        raise ApiError(404, "考试 Notebook 文件不存在")

    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ApiError(500, f"无法读取 Notebook：{exc}")

    code_cells = [c for c in notebook.get("cells", []) if c.get("cell_type") == "code"]
    sources = []
    executed = 0
    errors = []
    for index, cell in enumerate(code_cells, start=1):
        source = cell.get("source", "")
        if isinstance(source, list):
            source = "".join(source)
        sources.append(source)
        if cell.get("execution_count") is not None:
            executed += 1
        for output in cell.get("outputs", []) or []:
            if output.get("output_type") == "error":
                errors.append({
                    "cell": index,
                    "ename": output.get("ename", "Error"),
                    "evalue": output.get("evalue", ""),
                })

    code = "\n".join(sources)
    placeholders = len(re.findall(r"_{5,}", code))
    profile = QUESTION_PROFILES.get(session["qid"], {})
    checks = []
    for label, alternatives in profile.get("checks", []):
        ok = any(token in code for token in alternatives)
        checks.append({"label": label, "ok": ok, "tokens": list(alternatives)})

    # Automatic score is only a training self-check, not an official grade.
    if checks:
        check_score = round(60 * sum(1 for x in checks if x["ok"]) / len(checks))
    else:
        check_score = 0
    placeholder_score = 15 if placeholders == 0 else max(0, 15 - placeholders * 3)
    execution_score = round(15 * executed / len(code_cells)) if code_cells else 0
    error_score = 10 if not errors else 0
    score = min(100, check_score + placeholder_score + execution_score + error_score)

    current_files = _list_relative_files(workspace)
    generated = sorted(
        p for p in current_files - session.get("initial_files", set())
        if not p.startswith(".ipynb_checkpoints/")
        and p not in {"jupyter.log", "_exam_session.json"}
    )

    return {
        "score": score,
        "score_note": "自动初评，仅用于训练自检，不代表官方评分",
        "checks": checks,
        "placeholders": placeholders,
        "executed_cells": executed,
        "code_cells": len(code_cells),
        "errors": errors,
        "generated_files": generated,
    }


def _submit_exam(session_id: str) -> dict:
    global ACTIVE_SESSION, LAST_RESULT
    with LOCK:
        session = ACTIVE_SESSION
        if not session:
            raise ApiError(404, "当前没有正在进行的模拟考试")
        if session_id and session_id != session["id"]:
            raise ApiError(409, "提交的考试会话与当前会话不一致")

        report = _analyze_notebook(session)
        submitted_at = _now_ms()
        report.update({
            "id": session["id"],
            "qid": session["qid"],
            "started_at_ms": session["started_at_ms"],
            "submitted_at_ms": submitted_at,
            "elapsed_seconds": max(0, int((submitted_at - session["started_at_ms"]) / 1000)),
            "duration_minutes": session["duration_minutes"],
        })

        session["submitted"] = True
        _stop_jupyter(session)

        workspace: Path = session["workspace"]
        (workspace / "score.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        HISTORY_ROOT.mkdir(parents=True, exist_ok=True)
        history_dir = HISTORY_ROOT / session["id"]
        if history_dir.exists():
            shutil.rmtree(history_dir)
        try:
            shutil.move(str(workspace), str(history_dir))
            report["history_dir"] = str(history_dir)
        except Exception as exc:
            report["history_dir"] = str(workspace)
            report["history_warning"] = str(exc)

        LAST_RESULT = report
        ACTIVE_SESSION = None
        return report


def _system_status() -> dict:
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "notebook_installed": importlib.util.find_spec("notebook") is not None,
        "nbformat_installed": importlib.util.find_spec("nbformat") is not None,
        "jupyter_port": JUPYTER_PORT,
        "source_root_exists": SOURCE_ROOT.is_dir(),
    }


class PracticalHandler(SimpleHTTPRequestHandler):
    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        ".html": "text/html; charset=utf-8",
        ".htm": "text/html; charset=utf-8",
        ".md": "text/plain; charset=utf-8",
        ".txt": "text/plain; charset=utf-8",
        ".csv": "text/csv; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            raise ApiError(400, "请求 JSON 格式不正确")

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/system/status":
                self._send_json(200, {"ok": True, "system": _system_status()})
                return
            if path == "/api/exam/status":
                with LOCK:
                    session = _safe_session(ACTIVE_SESSION)
                    last = LAST_RESULT
                self._send_json(200, {
                    "ok": True,
                    "active": bool(session),
                    "session": session,
                    "last_result": last,
                })
                return
            super().do_GET()
        except ApiError as exc:
            self._send_json(exc.status, {"ok": False, "message": exc.message, **exc.extra})
        except Exception as exc:
            self._send_json(500, {"ok": False, "message": str(exc)})

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self._read_json()
            if path == "/api/exam/start":
                session = _start_exam(str(body.get("qid", "")).strip())
                self._send_json(200, {"ok": True, "session": session})
                return
            if path == "/api/exam/submit":
                report = _submit_exam(str(body.get("session_id", "")).strip())
                self._send_json(200, {"ok": True, "report": report})
                return
            self._send_json(404, {"ok": False, "message": "未知 API"})
        except ApiError as exc:
            self._send_json(exc.status, {"ok": False, "message": exc.message, **exc.extra})
        except Exception as exc:
            self._send_json(500, {"ok": False, "message": str(exc)})


if __name__ == "__main__":
    port = 7000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    EXAM_ROOT.mkdir(parents=True, exist_ok=True)
    HISTORY_ROOT.mkdir(parents=True, exist_ok=True)

    server = ThreadingHTTPServer(("127.0.0.1", port), PracticalHandler)
    print(f"AI Trainer: http://127.0.0.1:{port}/practice.html")
    print(f"Jupyter Notebook exam port: {JUPYTER_PORT}")
    print(f"Python: {sys.executable}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with LOCK:
            _stop_jupyter(ACTIVE_SESSION)
        server.server_close()
