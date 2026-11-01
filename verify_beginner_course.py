"""离线检测零基础课程：语法/结构检查，必要时运行 30 个示例。

基础检查（只用 Python 标准库）：
    python verify_beginner_course.py
实际运行所有课程代码（需要先安装依赖；不联网）：
    python verify_beginner_course.py --run
仅运行模块 A 与 C：
    python verify_beginner_course.py --run --modules AC
"""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent


def lessons():
    js = (ROOT / "beginner_course_data.js").read_text(encoding="utf-8")
    tag = "window.BEGINNER_COURSE="
    if tag not in js:
        raise ValueError("未找到课程数据")
    return json.loads(js.split(tag, 1)[1].strip().removesuffix(";"))["modules"]


def validate_notebooks(modules):
    result = []
    for m in modules:
        for lesson in m["steps"]:
            path = ROOT / "beginner_notebooks" / m["id"] / (lesson["id"] + ".ipynb")
            obj = json.loads(path.read_text(encoding="utf-8"))
            source = "".join(obj["cells"][3]["source"])
            ast.parse(source, filename=str(path))
            for c in obj["cells"]:
                if c["cell_type"] == "code":
                    ast.parse("".join(c["source"]), filename=str(path))
            if source != lesson["code"]:
                raise ValueError(f"{lesson['id']} 课程与 Notebook 示例代码不一致")
            result.append((lesson["id"], source))
    return result


def smoke(modules_to_run, scripts):
    failed=[]
    for identifier, code in scripts:
        if identifier[0] not in modules_to_run:
            continue
        env=os.environ.copy()
        env["MPLBACKEND"]="Agg"
        env["PYTHONIOENCODING"]="utf-8"
        env["OMP_NUM_THREADS"]="1"
        with tempfile.TemporaryDirectory(prefix="ai_trainer_beginner_") as temp:
            try:
                p=subprocess.run(
                    [sys.executable, "-c", code],
                    cwd=temp, env=env, capture_output=True,
                    text=True, errors="replace", timeout=90,
                )
                if p.returncode:
                    failed.append(identifier)
                    print(f"FAIL {identifier}\n{(p.stdout+p.stderr)[-1500:]}")
                else:
                    print(f"PASS {identifier}: {p.stdout.strip()[-150:]}")
            except subprocess.TimeoutExpired:
                failed.append(identifier)
                print(f"TIMEOUT {identifier}")
    return failed


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--run",action="store_true",help="依次在独立临时目录运行课程示例")
    parser.add_argument("--run-projects",action="store_true",help="运行五个综合项目参考答案")
    parser.add_argument("--modules",default="ABCDE",help="指定需运行模块，如 AC")
    args=parser.parse_args()
    if set(args.modules)-set("ABCDE"):
        parser.error("--modules 只能包含 A、B、C、D、E")
    suite=unittest.defaultTestLoader.discover(str(ROOT),pattern="test_beginner_course.py")
    tests=unittest.TextTestRunner(verbosity=2).run(suite)
    if not tests.wasSuccessful():
        return 1
    scripts=validate_notebooks(lessons())
    print(f"课程与 Notebook 静态检测通过：{len(scripts)} 节")
    if args.run_projects:
        projects=json.loads((ROOT/"beginner_projects"/"projects.json").read_text(encoding="utf-8"))
        project_scripts=[]
        for project in projects:
            mid=project["id"]
            doc=json.loads((ROOT/"beginner_projects"/"solutions"/f"{mid}_project_solution.ipynb").read_text(encoding="utf-8"))
            source="\n\n".join("".join(c["source"]) for c in doc["cells"] if c["cell_type"]=="code")
            project_scripts.append((mid,source))
        failed=smoke(set(args.modules),project_scripts)
        if failed:
            print("项目参考答案运行失败：",", ".join(failed))
            return 1
    if args.run:
        failed=smoke(set(args.modules),scripts)
        if failed:
            print("示例运行失败：",", ".join(failed))
            return 1
        print("指定模块的示例代码全部运行成功")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
