"""整理参考答案供页面查看，不运行代码，也不改写原始题目或评分基线。"""

import ast
import json
from pathlib import Path
import re

import exam_grading as grading


def complete_advanced_code(qid: str, notebook: dict, snippets: str) -> str:
    nodes = ast.parse(snippets).body
    values = []
    for node in nodes:
        value = node.value
        if isinstance(value, ast.Tuple) and len(value.elts) == 1:
            value = value.elts[0]
        values.append(ast.unparse(value))
    # 这两题的答案以多条语句表示一个填空，需还原为对应的表达式。
    if qid == "6.1.3":
        values = [values[0], f"({values[1]})[1]", f"({values[2]})[1]",
                  "cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel), "
                  "cv2.MORPH_CLOSE, kernel, iterations=2)"]
    elif qid == "6.3.2":
        values = [", ".join(values[:4]), *values[4:]]
    elif qid == "6.3.3":
        for index in (1, 3):
            values[index] = ast.unparse(nodes[index])

    blocks = []
    position = 0
    for index, cell in enumerate(notebook.get("cells", []), 1):
        if cell.get("cell_type") != "code":
            continue
        source = grading.source_text(cell)
        lines = []
        for line in source.splitlines():
            if not line.lstrip().startswith("#"):
                def replace(_match):
                    nonlocal position
                    if position >= len(values):
                        raise ValueError(f"{qid} 的参考填空数量不足")
                    value = values[position]
                    position += 1
                    return value
                line = re.sub(r"_{5,}", replace, line)
            lines.append(line)
        completed = "\n".join(lines)
        ast.parse(completed)
        blocks.append(f"# ====== Cell {index} ======\n{completed}")
    if position != len(values):
        raise ValueError(f"{qid} 的参考填空与题目框架不匹配")
    return "\n\n".join(blocks)


def get_reference_answer(qid: str, root: Path) -> dict:
    if not re.fullmatch(r"\d+\.\d+\.\d+", qid):
        raise ValueError("题号格式不正确")
    path = root / "人工智能训练师三级素材" / "操作题答案" / f"{qid}_答案.md"
    raw = path.read_bytes()
    try:
        markdown = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        markdown = raw.decode("gb18030")
    fenced = re.findall(r"^(```|~~~)[ \t]*(python|py)?[ \t]*\r?\n(.*?)^\1[ \t]*\r?$",
                        markdown, re.M | re.S | re.I)
    # 未标语言的围栏常是示例输出，不能拼入供复制的 Python 程序。
    blocks = [body for _fence, language, body in fenced if language]
    code = "\n\n".join(blocks[-1:] if qid.startswith("3.2.") else blocks).strip()
    if qid.startswith("6."):
        source = root / "人工智能训练师三级素材" / "人工智能训练师三级上网素材" / qid / f"{qid}.ipynb"
        notebook = json.loads(source.read_text(encoding="utf-8-sig"))
        code = complete_advanced_code(qid, notebook, code)
        title = markdown.splitlines()[0]
        markdown = f"{title}\n\n## 完整答案代码\n\n~~~python\n{code}\n~~~\n\n## 原始填空参考\n\n" + markdown
    return {"qid": qid, "code": code, "markdown": markdown}
