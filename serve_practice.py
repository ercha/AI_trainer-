from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
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

ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级上网素材"
EXAM_ROOT = ROOT / "_exam_workspace"
HISTORY_ROOT = ROOT / "_exam_history"
JUPYTER_PORT = 7001

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
ACTIVE_SESSION: dict | None = None
LAST_RESULT: dict | None = None


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
        return path.read_text(encoding="utf-8", errors="replace")[-max_chars:]
    except Exception:
        return ""


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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
            raise ApiError(409, f"Jupyter 端口 {JUPYTER_PORT} 已被占用。请关闭其他 Jupyter 服务后再开始考试。")

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
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
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


def _cell_source(cell: dict) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source or "")


def _is_effective_code_cell(cell: dict) -> bool:
    """Return True only for code cells that contain executable content.

    Empty cells and comment-only cells are ignored for the execution-score denominator,
    because Jupyter may legitimately leave their execution_count as None.
    """
    source = _cell_source(cell)
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


def _collect_notebook_state(notebook: dict) -> dict:
    all_code_cells = [c for c in notebook.get("cells", []) if c.get("cell_type") == "code"]
    effective_cells = [c for c in all_code_cells if _is_effective_code_cell(c)]
    sources: list[str] = []
    saved_executed = 0
    saved_errors: list[dict] = []
    effective_ids = {id(c) for c in effective_cells}
    for index, cell in enumerate(all_code_cells, start=1):
        sources.append(_cell_source(cell))
        if id(cell) in effective_ids and cell.get("execution_count") is not None:
            saved_executed += 1
        for output in cell.get("outputs", []) or []:
            if output.get("output_type") == "error":
                saved_errors.append({
                    "cell": index,
                    "ename": output.get("ename", "Error"),
                    "evalue": output.get("evalue", ""),
                })
    return {
        "code_cells": effective_cells,
        "total_code_cells": all_code_cells,
        "code": "\n".join(sources),
        "saved_executed_cells": saved_executed,
        "saved_errors": saved_errors,
    }


def _auto_execute_notebook(workspace: Path, notebook_path: Path) -> dict:
    if importlib.util.find_spec("nbclient") is None or importlib.util.find_spec("nbformat") is None:
        return {
            "available": False,
            "executed_cells": 0,
            "successful_cells": 0,
            "effective_cells": 0,
            "errors": [],
            "engine_error": "未安装 nbclient/nbformat，无法执行自动运行验证",
        }

    try:
        import nbformat
        from nbclient import NotebookClient

        notebook = nbformat.read(str(notebook_path), as_version=4)
        run_book = deepcopy(notebook)
        all_code_cells = [c for c in run_book.cells if c.get("cell_type") == "code"]
        for cell in all_code_cells:
            cell["execution_count"] = None
            cell["outputs"] = []

        kernel_name = (
            run_book.get("metadata", {})
            .get("kernelspec", {})
            .get("name", "python3")
        ) or "python3"
        resources = {"metadata": {"path": str(workspace)}}
        client = NotebookClient(
            run_book,
            timeout=90,
            kernel_name=kernel_name,
            allow_errors=True,
            resources=resources,
            record_timing=False,
        )
        client.execute()

        errors: list[dict] = []
        executed = 0
        successful = 0
        effective_count = 0
        for index, cell in enumerate([c for c in run_book.cells if c.get("cell_type") == "code"], start=1):
            if not _is_effective_code_cell(cell):
                continue
            effective_count += 1
            if cell.get("execution_count") is not None:
                executed += 1
            cell_errors = []
            for output in cell.get("outputs", []) or []:
                if output.get("output_type") == "error":
                    item = {
                        "cell": index,
                        "ename": output.get("ename", "Error"),
                        "evalue": output.get("evalue", ""),
                    }
                    errors.append(item)
                    cell_errors.append(item)
            if cell.get("execution_count") is not None and not cell_errors:
                successful += 1

        return {
            "available": True,
            "executed_cells": executed,
            "successful_cells": successful,
            "effective_cells": effective_count,
            "errors": errors,
            "engine_error": "",
        }
    except Exception as exc:
        return {
            "available": True,
            "executed_cells": 0,
            "successful_cells": 0,
            "effective_cells": 0,
            "errors": [],
            "engine_error": f"{type(exc).__name__}: {exc}",
        }


def _analyze_notebook(session: dict) -> dict:
    workspace: Path = session["workspace"]
    notebook_path = workspace / session["notebook"]
    if not notebook_path.exists():
        raise ApiError(404, "考试 Notebook 文件不存在")

    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ApiError(500, f"无法读取 Notebook：{exc}")

    state = _collect_notebook_state(notebook)
    code = state["code"]
    code_cells = state["code_cells"]
    placeholders = len(re.findall(r"_{5,}", code))

    profile = QUESTION_PROFILES.get(session["qid"], {})
    checks = []
    for label, alternatives in profile.get("checks", []):
        ok = any(token in code for token in alternatives)
        checks.append({"label": label, "ok": ok, "tokens": list(alternatives)})

    auto = _auto_execute_notebook(workspace, notebook_path)

    check_score = round(60 * sum(1 for x in checks if x["ok"]) / len(checks)) if checks else 0
    placeholder_score = 15 if placeholders == 0 else max(0, 15 - placeholders * 3)
    effective_count = len(code_cells)
    if auto["available"] and not auto["engine_error"]:
        run_score = round(15 * auto["successful_cells"] / effective_count) if effective_count else 15
        error_score = 10 if not auto["errors"] else 0
    else:
        run_score = 0
        error_score = 0
    score = min(100, check_score + placeholder_score + run_score + error_score)

    current_files = _list_relative_files(workspace)
    generated = sorted(
        p for p in current_files - session.get("initial_files", set())
        if not p.startswith(".ipynb_checkpoints/")
        and p not in {"jupyter.log", "_exam_session.json", "score.json"}
    )

    return {
        "score": score,
        "score_note": "自动初评：提交时会重新执行 Notebook 验证；空白/纯注释代码 Cell 不参与执行率扣分；仅用于训练自检，不代表官方评分",
        "checks": checks,
        "placeholders": placeholders,
        "code_cells": effective_count,
        "total_code_cells": len(state["total_code_cells"]),
        "saved_executed_cells": state["saved_executed_cells"],
        "saved_errors": state["saved_errors"],
        "auto_execution_available": auto["available"],
        "auto_executed_cells": auto["executed_cells"],
        "auto_successful_cells": auto["successful_cells"],
        "auto_errors": auto["errors"],
        "auto_engine_error": auto["engine_error"],
        "executed_cells": auto["successful_cells"],
        "errors": auto["errors"],
        "generated_files": generated,
        "score_parts": {
            "structure": check_score,
            "placeholders": placeholder_score,
            "execution": run_score,
            "runtime": error_score,
        },
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
            "notebook": session["notebook"],
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

        final_score_path = Path(report["history_dir"]) / "score.json"
        try:
            final_score_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

        LAST_RESULT = report
        ACTIVE_SESSION = None
        return report


def _record_from_folder(folder: Path, status: str) -> dict | None:
    meta = _read_json(folder / "_exam_session.json")
    score = _read_json(folder / "score.json") if status == "submitted" else {}
    qid = str(meta.get("qid") or score.get("qid") or "").strip()
    if not qid:
        m = re.search(r"(\d+\.\d+\.\d+)", folder.name)
        qid = m.group(1) if m else "未知"
    notebook_name = str(meta.get("notebook") or score.get("notebook") or f"{qid}.ipynb")
    notebook_path = folder / notebook_name
    return {
        "id": folder.name,
        "qid": qid,
        "status": status,
        "notebook": notebook_name,
        "started_at_ms": int(meta.get("started_at_ms") or score.get("started_at_ms") or int(folder.stat().st_mtime * 1000)),
        "deadline_ms": int(meta.get("deadline_ms") or 0),
        "duration_minutes": int(meta.get("duration_minutes") or score.get("duration_minutes") or 0),
        "submitted_at_ms": int(score.get("submitted_at_ms") or 0),
        "elapsed_seconds": int(score.get("elapsed_seconds") or 0),
        "score": score.get("score"),
        "has_notebook": notebook_path.exists(),
        "folder": str(folder),
    }


def _list_exam_records() -> list[dict]:
    records: list[dict] = []
    active_id = None
    with LOCK:
        if ACTIVE_SESSION:
            active = _safe_session(ACTIVE_SESSION)
            if active:
                active_id = active["id"]
                records.append({
                    **active,
                    "status": "active",
                    "score": None,
                    "has_notebook": True,
                    "folder": active["workspace"],
                })

    if EXAM_ROOT.is_dir():
        for folder in EXAM_ROOT.iterdir():
            if folder.is_dir() and folder.name != active_id:
                item = _record_from_folder(folder, "unfinished")
                if item:
                    records.append(item)
    if HISTORY_ROOT.is_dir():
        for folder in HISTORY_ROOT.iterdir():
            if folder.is_dir():
                item = _record_from_folder(folder, "submitted")
                if item:
                    records.append(item)

    records.sort(key=lambda x: int(x.get("started_at_ms") or 0), reverse=True)
    return records


def _locate_record(record_id: str) -> tuple[Path, str]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", record_id or ""):
        raise ApiError(400, "记录编号格式不正确")
    with LOCK:
        if ACTIVE_SESSION and ACTIVE_SESSION.get("id") == record_id:
            return Path(ACTIVE_SESSION["workspace"]), "active"
    folder = EXAM_ROOT / record_id
    if folder.is_dir():
        return folder, "unfinished"
    folder = HISTORY_ROOT / record_id
    if folder.is_dir():
        return folder, "submitted"
    raise ApiError(404, "没有找到这条考试记录")


def _output_for_review(output: dict) -> dict:
    typ = output.get("output_type", "")
    if typ == "stream":
        text = output.get("text", "")
        if isinstance(text, list):
            text = "".join(text)
        return {"type": "stream", "text": str(text)}
    if typ == "error":
        tb = output.get("traceback", []) or []
        return {
            "type": "error",
            "ename": output.get("ename", "Error"),
            "evalue": output.get("evalue", ""),
            "text": "\n".join(str(x) for x in tb),
        }
    if typ in {"execute_result", "display_data"}:
        data = output.get("data", {}) or {}
        text = data.get("text/plain", "")
        if isinstance(text, list):
            text = "".join(text)
        result = {"type": typ, "text": str(text)}
        if "image/png" in data:
            result["image_png"] = data["image/png"]
        return result
    return {"type": typ, "text": ""}


def _get_exam_record(record_id: str) -> dict:
    folder, status = _locate_record(record_id)
    meta = _read_json(folder / "_exam_session.json")
    score = _read_json(folder / "score.json") if (folder / "score.json").exists() else {}
    qid = str(meta.get("qid") or score.get("qid") or "")
    notebook_name = str(meta.get("notebook") or score.get("notebook") or f"{qid}.ipynb")
    notebook_path = folder / notebook_name
    if not notebook_path.exists():
        candidates = sorted(folder.glob("*.ipynb"))
        if not candidates:
            raise ApiError(404, "这条记录中没有找到 Notebook")
        notebook_path = candidates[0]
        notebook_name = notebook_path.name

    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ApiError(500, f"无法读取记录中的 Notebook：{exc}")

    cells = []
    for index, cell in enumerate(notebook.get("cells", []), start=1):
        typ = cell.get("cell_type", "")
        if typ not in {"code", "markdown", "raw"}:
            continue
        item = {
            "index": index,
            "cell_type": typ,
            "source": _cell_source(cell),
            "execution_count": cell.get("execution_count"),
            "outputs": [],
        }
        if typ == "code":
            item["outputs"] = [_output_for_review(o) for o in (cell.get("outputs", []) or [])]
        cells.append(item)

    return {
        "id": record_id,
        "qid": qid,
        "status": status,
        "notebook": notebook_name,
        "meta": meta,
        "score": score,
        "cells": cells,
    }


def _system_status() -> dict:
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "notebook_installed": importlib.util.find_spec("notebook") is not None,
        "nbformat_installed": importlib.util.find_spec("nbformat") is not None,
        "nbclient_installed": importlib.util.find_spec("nbclient") is not None,
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
        parsed = urlparse(self.path)
        path = parsed.path
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
            if path == "/api/exam/records":
                self._send_json(200, {"ok": True, "records": _list_exam_records()})
                return
            if path == "/api/exam/record":
                record_id = (parse_qs(parsed.query).get("id") or [""])[0]
                self._send_json(200, {"ok": True, "record": _get_exam_record(record_id)})
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7000
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
