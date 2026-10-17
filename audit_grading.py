"""只读检查题库评分覆盖率；真实执行仅限临时目录中的轻量样例。"""

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import tempfile
from unittest.mock import patch

import serve_practice as server
import exam_grading as grading


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def answer_notebook(qid):
    path = server.ROOT / "人工智能训练师三级素材" / "操作题答案" / f"{qid}_答案.md"
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            text = path.read_text(encoding=encoding)
            break
        except UnicodeDecodeError:
            continue
    sources = [match[1] for match in re.findall(r"(```|~~~)(?:python|py)\s*\n(.*?)\1", text, re.S | re.I)]
    return notebook_from_sources(sources)


def notebook_from_sources(sources):
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3"}},
        "cells": [{"id": f"audit-{i}", "cell_type": "code", "source": source,
                   "metadata": {}, "execution_count": None, "outputs": []}
                  for i, source in enumerate(sources)],
    }


def analyze(qid, notebook, real=False):
    with tempfile.TemporaryDirectory(prefix="ai-trainer-audit-") as folder:
        workspace = Path(folder)
        if real and qid in {"1.1.1", "2.1.1"}:
            filename = "patient_data.csv" if qid == "1.1.1" else "auto-mpg.csv"
            shutil.copyfile(server.SOURCE_ROOT / qid / filename, workspace / filename)
        path = workspace / f"{qid}.ipynb"
        path.write_text(json.dumps(notebook, ensure_ascii=False), encoding="utf-8")
        session = {"workspace": workspace, "notebook": path.name, "qid": qid}
        count = len(server._collect_notebook_state(notebook)["code_cells"])
        if real:
            report = server._analyze_notebook(session)
        else:
            auto = {"available": True, "executed_cells": count, "successful_cells": count,
                    "errors": [], "engine_error": ""}
            with patch.object(server, "_auto_execute_notebook", return_value=auto):
                report = server._analyze_notebook(session)
        return {
            "score": report["score"], "score_status": report["score_status"],
            "failed_checks": [x["label"] for x in report["checks"] if not x["ok"]],
            "auto_successful_cells": report["auto_successful_cells"],
            "auto_errors": report["auto_errors"], "auto_engine_error": report["auto_engine_error"],
            "real_execution": real,
        }


def audit(real=False):
    rows = []
    for folder in sorted(server.SOURCE_ROOT.iterdir()):
        if not folder.is_dir() or not re.fullmatch(r"\d+\.\d+\.\d+", folder.name):
            continue
        notebooks = list(folder.rglob("*.ipynb"))
        if not notebooks:
            continue
        qid = folder.name
        profile = server.QUESTION_PROFILES.get(qid, {})
        kind = "reference_and_result" if profile.get("checker") == "reference_and_result" else "ast" if profile.get("checker") else "keyword" if profile.get("checks") else "unconfigured"
        row = {"qid": qid, "kind": kind, "notebooks": len(notebooks)}
        row["rule_count"] = len(grading.reference_rules(qid)[0])
        page = server.ROOT / "人工智能训练师三级素材" / "人工智能训练师三级考试平台模拟界面" / f"{qid}.html"
        row["original_question_page_exists"] = page.exists()
        row["question_page_exists"] = page.exists() or (qid.startswith(("5.", "6.")) and (server.ROOT / "exam_question.html").exists())
        answer = server.ROOT / "人工智能训练师三级素材" / "操作题答案" / f"{qid}_答案.md"
        if answer.exists():
            markdown = answer.read_text(encoding="utf-8-sig")
            row["workspace_answer_code_missing"] = not bool(grading.code_blocks(markdown))
        if page.exists():
            parser = PageText()
            parser.feed(page.read_text(encoding="utf-8-sig"))
            if "考核时间" in parser.parts:
                value = parser.parts[parser.parts.index("考核时间") + 1]
                match = re.fullmatch(r"(\d+)\s*min", value, re.I)
                if match and int(match[1]) != profile.get("duration", 30):
                    row["duration_mismatch"] = {"question_minutes": int(match[1]), "exam_minutes": profile.get("duration", 30)}
        if kind in {"keyword", "reference_and_result"}:
            source = "\n".join("# " + line for rule in grading.reference_rules(qid)[0] for line in __import__('ast').unparse(rule).splitlines())
            spoof = notebook_from_sources([source + "\nprint('audit only')"])
            row["comments_only_spoof"] = analyze(qid, spoof)
            if qid in {"1.1.1", "1.1.2", "2.1.1", "2.2.1"}:
                row["reference_structure_ok"] = all(x["ok"] for x in grading.structure_checks(qid, answer_notebook(qid)))
            else:
                row["reference_note"] = "强化题答案是填空片段，不作为完整 Notebook 评分基线"
            starter = json.loads(notebooks[0].read_text(encoding="utf-8-sig"))
            code = server._collect_notebook_state(starter)["code"]
            row["starter"] = {
                "placeholders": len(re.findall(r"_{5,}", code)),
                "matching_checks": [x["label"] for x in grading.structure_checks(qid, starter) if x["ok"]],
                "total_checks": row["rule_count"],
            }
        elif kind == "unconfigured":
            row["no_rule_fallback"] = analyze(qid, notebook_from_sources(["print('audit only')"]))
        rows.append(row)

    cases = {}
    for qid in ("1.1.1", "1.1.2", "2.1.1", "2.2.1"):
        equivalent = answer_notebook(qid)
        for cell in equivalent["cells"]:
            cell["source"] = cell["source"].replace("import pandas as pd", "import pandas as pandas").replace("pd.", "pandas.")
        cases[f"{qid}_equivalent_pandas_alias"] = analyze(qid, equivalent)

    wrong_ratio = answer_notebook("1.1.1")
    for cell in wrong_ratio["cells"]:
        cell["source"] = cell["source"].replace("/ len(data)", "/ 1")
    cases["1.1.1_wrong_ratio"] = analyze("1.1.1", wrong_ratio, real=real)

    no_scaling = answer_notebook("2.1.1")
    for cell in no_scaling["cells"]:
        cell["source"] = cell["source"].replace("scaler.fit_transform(df[numeric_cols])", "df[numeric_cols]")
    cases["2.1.1_no_scaling"] = analyze("2.1.1", no_scaling, real=real)

    int_string = answer_notebook("1.1.4")
    for cell in int_string["cells"]:
        cell["source"] = cell["source"].replace(".astype(int)", ".astype('int')")
    cases["1.1.4_equivalent_astype_string"] = analyze("1.1.4", int_string)

    reassigned = answer_notebook("1.1.4")
    reassigned["cells"][1]["source"] += "\ndata['ReviewScore'] = 0\n"
    cases["1.1.4_correct_then_overwritten"] = analyze("1.1.4", reassigned)

    if real:
        spoof = notebook_from_sources(["# pd.read_csv np.where value_counts pd.cut groupby\nprint('audit only')"])
        cases["1.1.1_comments_only_spoof"] = analyze("1.1.1", spoof, real=True)
        empty = notebook_from_sources(["# pd.read_csv np.where value_counts pd.cut groupby"])
        cases["1.1.1_no_executable_code"] = analyze("1.1.1", empty, real=True)
        equivalent = answer_notebook("1.1.1")
        for cell in equivalent["cells"]:
            cell["source"] = cell["source"].replace("import pandas as pd", "import pandas as pandas").replace("pd.", "pandas.")
        cases["1.1.1_equivalent_pandas_alias_real"] = analyze("1.1.1", equivalent, real=True)
    return {
        "summary": {"questions_with_notebooks": len(rows),
                    **{kind: sum(row["kind"] == kind for row in rows) for kind in ("reference_and_result", "ast", "keyword", "unconfigured")}},
        "missing_qids": [row["qid"] for row in rows if row["kind"] == "unconfigured"],
        "questions": rows,
        "cases": cases,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--real", action="store_true", help="在临时目录实际执行 5 个轻量反例，不执行训练或联网任务")
    args = parser.parse_args()
    print(json.dumps(audit(real=args.real), ensure_ascii=True, indent=2))
