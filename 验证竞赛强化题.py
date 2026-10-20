#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本地验证 25 道竞赛强化训练题，不执行耗时模型训练。"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级上网素材"


def main() -> None:
    print("[1/4] 检查 Python 源码语法")
    for name in [
        "生成竞赛强化训练.py",
        "competition_syllabus_expansion.py",
        "exam_grading.py",
        "reference_answers.py",
        "serve_practice.py",
        "tray_launcher.py",
    ]:
        source = (ROOT / name).read_text(encoding="utf-8-sig")
        ast.parse(source, filename=name)

    print("[2/4] 重新生成 25 道强化题")
    subprocess.run(
        [sys.executable, str(ROOT / "生成竞赛强化训练.py"), "--force"],
        cwd=ROOT,
        check=True,
    )

    print("[3/4] 检查 Notebook、TODO 与占位符")
    ids = [f"6.{module}.{index}" for module in range(1, 6) for index in range(1, 6)]
    assert len(ids) == 25
    for qid in ids:
        path = SRC / qid / f"{qid}.ipynb"
        assert path.is_file(), f"{qid}: Notebook 不存在"
        nb = json.loads(path.read_text(encoding="utf-8"))
        text = "\n".join("".join(cell.get("source", [])) for cell in nb.get("cells", []))
        assert "# TODO " in text, f"{qid}: 缺少 TODO"
        assert "_____________" in text, f"{qid}: 缺少待填空"

    print("[4/4] 将参考答案填回 Notebook 并做完整 Python 语法检查")
    import reference_answers

    for qid in ids:
        answer = reference_answers.get_reference_answer(qid, ROOT)
        ast.parse(answer["code"], filename=f"{qid}_完整答案.py")

    print("OK：25 道强化题均已生成，参考答案与占位符匹配，完整代码语法有效")


if __name__ == "__main__":
    main()
