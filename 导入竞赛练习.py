#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将竞赛题目.zip 中的模块 A-E 导入实操训练系统。

用法：
    python 导入竞赛练习.py 竞赛题目.zip
    python 导入竞赛练习.py

不传参数时，会依次在脚本目录、当前目录和用户下载目录查找“竞赛题目.zip”。
只写入 5.1.1 ~ 5.1.5 竞赛专项目录及对应参考答案，不修改原有 40 道题。
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级上网素材"
ANSWER_ROOT = ROOT / "人工智能训练师三级素材" / "操作题答案"
DOC_ROOT = ROOT / "人工智能训练师三级素材" / "竞赛专项原始资料"

QUESTIONS = {
    "5.1.1": {
        "module": "模块A",
        "letter": "A",
        "title": "人脸图像离线数据增强",
        "assets": [("prefix", "模块A/attendance_face/")],
    },
    "5.1.2": {
        "module": "模块B",
        "letter": "B",
        "title": "K-Means 图像分割与新闻主题聚类",
        "assets": [("prefix", "模块B/input/")],
    },
    "5.1.3": {
        "module": "模块C",
        "letter": "C",
        "title": "CNN 手写数字识别",
        "assets": [("prefix", "模块C/images/")],
    },
    "5.1.4": {
        "module": "模块D",
        "letter": "D",
        "title": "影评 Word2Vec 词向量训练与语义分析",
        "assets": [
            ("file", "模块D/corpus.txt"),
            ("file", "模块D/stopwords.dic"),
        ],
    },
    "5.1.5": {
        "module": "模块E",
        "letter": "E",
        "title": "图书出版数据分析与 AI 智能报告",
        "assets": [("file", "模块E/book_data.json")],
    },
}

E_ANALYSIS_ANSWER = """
## 模块 E 任务分析参考要点

### 1. 从问题定义到原型系统交付

1. **问题定义与需求分析**：明确业务痛点、用户、输入输出、成功指标、边界条件和合规要求，形成需求说明与验收标准。
2. **技术方案设计**：选择数据处理、模型/API、系统架构和开发工具，明确模块接口、风险和资源需求，形成技术方案与原型设计。
3. **数据准备**：完成数据采集、清洗、标注、质量检查、训练/验证划分及数据版本管理，形成可复用数据集和数据说明。
4. **功能模块开发**：分别实现数据处理、模型推理/调用、业务逻辑、可视化与报告等模块，并进行单元测试。
5. **系统集成与测试**：完成接口联调、功能测试、异常测试、性能测试和结果验证，修复问题并形成测试记录。
6. **交付与展示**：整理可运行原型、部署说明、用户说明、测试报告和演示材料，按典型业务流程现场演示并说明关键技术与效果。

### 2. 工程化开发与交付

- 代码应结构清晰、命名统一、关键逻辑有必要注释，并通过版本控制保存变更。
- 固定依赖版本、随机种子、配置项和数据路径，提供 requirements/环境说明、启动命令与示例输入，保证结果可复现。
- 密钥、接口地址等配置与代码分离，不在源码中提交真实密钥。
- 文档至少包含 README、环境与部署说明、数据说明、接口/模块说明、测试报告、已知限制和使用手册。
- 演示材料应准备流程图、关键结果截图/图表、典型输入输出和备用离线结果；展示时按“问题-方案-实现-结果-价值”组织。

### 3. 生成式 AI、低代码和可视化工具的辅助作用

- **生成式 AI**：用于需求梳理、代码/测试样例生成、调试解释、提示词优化、报告草拟和文档整理，但关键代码和结论需要人工验证。
- **低代码工具**：用于快速搭建数据流、API 编排、表单和业务原型，降低重复开发成本，适合验证业务流程和快速迭代。
- **可视化工具**：用于数据探索、质量检查、模型结果对比、运行监控和成果展示，使异常、趋势和业务指标更易发现与沟通。
"""


def find_archive(arg: str | None) -> Path:
    if arg:
        p = Path(arg).expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"未找到压缩包：{p}")
        return p

    candidates = [
        ROOT / "竞赛题目.zip",
        Path.cwd() / "竞赛题目.zip",
        Path.home() / "Downloads" / "竞赛题目.zip",
        Path.home() / "下载" / "竞赛题目.zip",
    ]
    for p in candidates:
        if p.is_file():
            return p.resolve()
    raise FileNotFoundError(
        "未找到“竞赛题目.zip”。请将压缩包放到项目根目录，"
        "或执行：python 导入竞赛练习.py <压缩包路径>"
    )


def write_zip_member(zf: zipfile.ZipFile, member: str, target: Path) -> None:
    info = zf.getinfo(member)
    if info.is_dir():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(info, "r") as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)


def copy_prefix(zf: zipfile.ZipFile, prefix: str, destination: Path) -> int:
    count = 0
    for info in zf.infolist():
        name = info.filename.replace("\\", "/")
        if info.is_dir() or not name.startswith(prefix):
            continue
        rel = Path(name[len(prefix):])
        if not rel.parts:
            continue
        write_zip_member(zf, info.filename, destination / rel)
        count += 1
    return count


def build_answer(qid: str, spec: dict, solution: str) -> str:
    # 不把考试环境提供的密钥字面值写入题库答案。
    solution = re.sub(
        r'(?m)^API_KEY\s*=\s*["\'][^"\']*["\']\s*$',
        'API_KEY = "请填写考试环境提供的 API Key"',
        solution,
    )
    extra = E_ANALYSIS_ANSWER if qid == "5.1.5" else ""
    return (
        f"# {qid} {spec['title']} - 参考答案\n\n"
        "> 由竞赛资料包中的已完成脚本生成，供训练复盘使用。"
        "模拟考试时请先独立完成再查看。\n\n"
        "## 完整参考代码\n\n"
        "~~~python\n"
        f"{solution.rstrip()}\n"
        "~~~\n"
        f"{extra}\n"
    )


def import_archive(archive: Path) -> None:
    SOURCE_ROOT.mkdir(parents=True, exist_ok=True)
    ANSWER_ROOT.mkdir(parents=True, exist_ok=True)
    DOC_ROOT.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "r") as zf:
        names = {i.filename.replace("\\", "/"): i.filename for i in zf.infolist()}

        for qid, spec in QUESTIONS.items():
            letter = spec["letter"]
            notebook_member = f"{spec['module']}/{letter}.ipynb"
            solution_member = f"{spec['module']}/{letter}.py"
            if notebook_member not in names:
                raise RuntimeError(f"压缩包缺少：{notebook_member}")
            if solution_member not in names:
                raise RuntimeError(f"压缩包缺少：{solution_member}")

            target = SOURCE_ROOT / qid
            if target.exists():
                shutil.rmtree(target)
            target.mkdir(parents=True)

            write_zip_member(zf, names[notebook_member], target / f"{qid}.ipynb")

            asset_count = 0
            for kind, member in spec["assets"]:
                if kind == "prefix":
                    asset_count += copy_prefix(zf, member, target / Path(member).name)
                elif kind == "file":
                    if member not in names:
                        raise RuntimeError(f"压缩包缺少：{member}")
                    write_zip_member(zf, names[member], target / Path(member).name)
                    asset_count += 1

            solution = zf.read(names[solution_member]).decode("utf-8-sig", errors="replace")
            answer = build_answer(qid, spec, solution)
            (ANSWER_ROOT / f"{qid}_答案.md").write_text(answer, encoding="utf-8")

            print(f"[完成] {qid} {spec['title']}：Notebook 1 个，素材 {asset_count} 个")

        # 保存原始竞赛任务书，便于复核题意；不参与模拟考试运行。
        for info in zf.infolist():
            name = info.filename.replace("\\", "/")
            base = Path(name).name
            if info.is_dir():
                continue
            if base in {"任务书A-D.pdf", "任务书E.pdf"} or (
                base.startswith("2026年") and base.endswith("赛项技术文件.pdf")
            ):
                write_zip_member(zf, info.filename, DOC_ROOT / base)

    print()
    print("竞赛 A-E 练习已导入题库：5.1.1 ~ 5.1.5")
    print(f"素材目录：{SOURCE_ROOT}")
    print(f"参考答案：{ANSWER_ROOT}")
    print("请重新启动实操训练服务或刷新页面后开始练习。")


def main() -> int:
    parser = argparse.ArgumentParser(description="导入竞赛题目.zip 中的 A-E 练习")
    parser.add_argument("archive", nargs="?", help="竞赛题目.zip 路径")
    args = parser.parse_args()
    try:
        archive = find_archive(args.archive)
        print(f"正在导入：{archive}")
        import_archive(archive)
        return 0
    except (FileNotFoundError, zipfile.BadZipFile, RuntimeError, KeyError) as exc:
        print(f"导入失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
