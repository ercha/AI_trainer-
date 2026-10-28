#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""本地验证 27 道竞赛强化训练题，不执行耗时模型训练。"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys

from competition_todo_alignment import EXPECTED_TODO_GROUPS
from competition_real_exam_workflow import PLOT_SPECS

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

    print("[2/4] 重新生成 27 道强化题")
    subprocess.run(
        [sys.executable, str(ROOT / "生成竞赛强化训练.py"), "--force"],
        cwd=ROOT,
        check=True,
    )

    print("[3/4] 检查 Notebook、TODO 与占位符")
    ids = [f"6.{module}.{index}" for module in range(1, 6) for index in range(1, 6)] + ["6.2.6", "6.3.6"]
    assert len(ids) == 27
    for qid in ids:
        path = SRC / qid / f"{qid}.ipynb"
        assert path.is_file(), f"{qid}: Notebook 不存在"
        nb = json.loads(path.read_text(encoding="utf-8"))
        text = "\n".join("".join(cell.get("source", [])) for cell in nb.get("cells", []))
        assert "# TODO " in text, f"{qid}: 缺少 TODO"
        assert "_____________" in text, f"{qid}: 缺少待填空"
        raw = [int(x) for x in __import__("re").findall(r"# TODO (\d+)(?:-\d+)?", text)]
        groups = []
        for group in raw:
            if not groups or groups[-1] != group:
                groups.append(group)
        expected = list(EXPECTED_TODO_GROUPS[qid])
        assert groups == expected, f"{qid}: TODO 顺序错误，实际 {groups}，应为 {expected}"

        # 防止 TODO 只说“保存结果”却不提供参考答案要求的文件名。
        todo_lines = [line.strip() for line in text.splitlines() if line.lstrip().startswith("# TODO ")]
        audit_todos = [line for line in todo_lines if line.startswith("# TODO 0-")]
        assert any("data_quality_check.csv" in line and "utf-8-sig" in line for line in audit_todos), (
            f"{qid}: TODO 0 缺少数据核验文件名或编码要求"
        )
        _, _, _, _, _, _, plot_file = PLOT_SPECS[qid]
        assert any(plot_file in line for line in todo_lines), f"{qid}: TODO 缺少可视化输出文件名 {plot_file}"

        if qid == "6.3.2":
            for requirement in [
                "RandomHorizontalFlip(p=0.5)",
                "RandomRotation(15)",
                "ColorJitter(brightness=0.2, contrast=0.2)",
                "ToTensor()",
                "BatchNorm2d(24)",
                "Dropout(0.4)",
                "best_flower_cnn.pt",
                "training_curve.png",
            ]:
                assert any(requirement in line for line in todo_lines), (
                    f"6.3.2: TODO 描述遗漏参数或交付物 {requirement}"
                )

    print("[4/4] 将参考答案填回 Notebook 并做完整 Python 语法检查")
    import reference_answers

    for qid in ids:
        answer = reference_answers.get_reference_answer(qid, ROOT)
        ast.parse(answer["code"], filename=f"{qid}_完整答案.py")

    print("OK：27 道强化题均已生成，参考答案与占位符匹配，完整代码语法有效")


if __name__ == "__main__":
    main()
