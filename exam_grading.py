"""题目框架检查与运行结果验收，不执行参考答案或加载提交的模型文件。"""

import ast
from copy import deepcopy
from functools import lru_cache
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级上网素材"
ANSWERS = ROOT / "人工智能训练师三级素材" / "操作题答案"
PAGES = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级考试平台模拟界面"
QIDS = ([f"1.1.{i}" for i in range(1, 6)] + [f"2.{j}.{i}" for j in (1, 2) for i in range(1, 6)]
        + [f"3.2.{i}" for i in range(1, 6)] + [f"5.1.{i}" for i in range(1, 6)]
        + [f"6.{j}.{i}" for j in range(1, 6) for i in range(1, 6)] + ["6.2.6", "6.3.6"])
ADVANCED_MINUTES = [
    40, 45, 45, 40, 40,
    50, 55, 55, 50, 55,
    60, 60, 65, 70, 70,
    50, 55, 55, 65, 55,
    60, 65, 65, 70, 75,
]
ADVANCED_EXTRA_MINUTES = {"6.2.6": 55, "6.3.6": 65}


class PageText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def duration_minutes(qid):
    page = PAGES / f"{qid}.html"
    if page.exists():
        parser = PageText()
        parser.feed(page.read_text(encoding="utf-8-sig"))
        if "考核时间" in parser.parts:
            value = parser.parts[parser.parts.index("考核时间") + 1]
            match = re.search(r"\d+", value)
            if match:
                return int(match[0])
    if qid in ADVANCED_EXTRA_MINUTES:
        return ADVANCED_EXTRA_MINUTES[qid]
    if qid.startswith("6.") and qid in QIDS:
        parts = [int(x) for x in qid.split(".")]
        return ADVANCED_MINUTES[(parts[1] - 1) * 5 + parts[2] - 1]
    return 60 if qid.startswith("5.") else 30


def source_text(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def code_blocks(markdown):
    return [m[1] for m in re.findall(r"(```|~~~)(?:python|py)?[ \t]*\r?\n(.*?)\1", markdown, re.S | re.I)]


def parsed_cells(notebook):
    for index, cell in enumerate(notebook.get("cells", []), 1):
        if cell.get("cell_type") != "code":
            continue
        text = source_text(cell)
        try:
            yield index, text, ast.parse(text)
        except SyntaxError:
            continue


def placeholders(notebook):
    # Only identifier placeholders count; underscores in comments and column names do not.
    count = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        import io
        import tokenize
        try:
            count += sum(t.type == tokenize.NAME and bool(re.fullmatch(r"_{5,}", t.string))
                         for t in tokenize.generate_tokens(io.StringIO(source_text(cell)).readline))
        except (tokenize.TokenError, IndentationError):
            count += 1
    return count


class Normalize(ast.NodeTransformer):
    def __init__(self, aliases):
        self.aliases = aliases

    def visit_Name(self, node):
        name = self.aliases.get(node.id, node.id)
        if "." in name:
            return ast.copy_location(ast.parse(name, mode="eval").body, node)
        return ast.copy_location(ast.Name(id=name, ctx=ast.Load()), node)

    def visit_Subscript(self, node):
        self.generic_visit(node)
        node.ctx = ast.Load()
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "head" and len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and node.args[0].value == 5:
                node.args = []
            if node.func.attr == "astype" and node.args and isinstance(node.args[0], ast.Constant):
                names = {"int": "int", "int64": "int", "float": "float", "float64": "float", "str": "str"}
                if node.args[0].value in names:
                    node.args[0] = ast.Name(id=names[node.args[0].value], ctx=ast.Load())
            if node.func.attr == "isna":
                node.func.attr = "isnull"
        node.keywords.sort(key=lambda k: k.arg or "")
        return node


def aliases_for(trees):
    aliases = {}
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for item in node.names:
                    aliases[item.asname or item.name] = item.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                for item in node.names:
                    aliases[item.asname or item.name] = node.module + "." + item.name
    return aliases


def node_key(node, aliases):
    return ast.dump(Normalize(aliases).visit(deepcopy(node)), include_attributes=False)


def meaningful_nodes(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            if isinstance(node.value, (ast.Call, ast.BinOp, ast.Subscript, ast.Compare, ast.ListComp, ast.IfExp, ast.Dict)):
                yield node
            if isinstance(node.value, (ast.BinOp, ast.Subscript, ast.Compare, ast.ListComp, ast.IfExp)):
                yield node.value
        elif isinstance(node, (ast.Expr, ast.Return)) and isinstance(node.value, (ast.BinOp, ast.Subscript, ast.Compare, ast.ListComp, ast.IfExp)):
            yield node.value
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func)
            if name not in {"print", "len", "range", "str", "int", "float", "list", "set", "tuple", "enumerate", "zip"} and not name.endswith((".set_title", ".set_xlabel", ".set_ylabel", ".show", ".tight_layout", ".figure", ".subplots")):
                yield node


@lru_cache(maxsize=64)
def reference_rules(qid):
    path = ANSWERS / f"{qid}_答案.md"
    if qid not in QIDS or not path.exists():
        return [], {}
    blocks = code_blocks(path.read_text(encoding="utf-8-sig"))
    # Vision answers contain a fill-in list followed by a standalone reference.
    if qid.startswith("3.2."):
        blocks = blocks[-1:]
    trees = []
    for block in blocks:
        try:
            trees.append(ast.parse(block))
        except SyntaxError:
            continue
    starter = SOURCE / qid / f"{qid}.ipynb"
    imports = list(trees)
    if starter.exists():
        imports += [tree for _, _, tree in parsed_cells(json.loads(starter.read_text(encoding="utf-8")))]
    aliases = aliases_for(imports)
    rules, seen = [], set()
    for tree in trees:
        for node in meaningful_nodes(tree):
            key = node_key(node, aliases)
            if key in seen or any(isinstance(child, ast.Name) and re.fullmatch(r"_{5,}", child.id) for child in ast.walk(node)):
                continue
            seen.add(key)
            rules.append(node)
    return rules, aliases


def structure_checks(qid, notebook):
    expected, reference_aliases = reference_rules(qid)
    parsed = list(parsed_cells(notebook))
    aliases = aliases_for([tree for _, _, tree in parsed])
    candidates = []
    for cell, text, tree in parsed:
        for node in meaningful_nodes(tree):
            candidates.append((node_key(node, aliases), cell, node, ast.get_source_segment(text, node) or ""))
    keys = {item[0] for item in candidates}
    checks = []
    for node in expected:
        ok = node_key(node, reference_aliases) in keys
        code = ast.unparse(node)
        label = "赋值：" + ", ".join(ast.unparse(t) for t in node.targets) if isinstance(node, ast.Assign) else "调用：" + (ast.unparse(node.func) if isinstance(node, ast.Call) else code[:60])
        item = {"label": label, "ok": ok, "kind": "structure"}
        if not ok:
            matches = [c for c in candidates if isinstance(node, ast.Assign) and isinstance(c[2], ast.Assign)
                       and [node_key(t, aliases) for t in c[2].targets] == [node_key(t, reference_aliases) for t in node.targets]]
            item.update(expected=code, actual=matches[-1][3] if matches else "未找到对应的运算语句",
                        cell=matches[-1][1] if matches else None, line=matches[-1][2].lineno if matches else None,
                        hint="此项为框架参考写法比对；等价实现以实际结果验收为准，不因 import、注释或字符串中出现名称而通过。")
        checks.append(item)
    return checks


# The probe runs only after the submitted cells, and never changes their saved source.
PROBE_SOURCE = r'''
import json as _tg_json
import numpy as _tg_np
import pandas as _tg_pd
def _tg_pack(v):
    if isinstance(v, (_tg_pd.DataFrame, _tg_pd.Series)):
        f = v.to_frame() if isinstance(v, _tg_pd.Series) else v
        if len(f) > 5000 or len(f.columns) > 80:
            f = f.head(5000)
        return {"table": f.to_json(orient="split", date_format="iso"), "series": isinstance(v, _tg_pd.Series)}
    if isinstance(v, (list,tuple)) and v and isinstance(v[0],_tg_np.ndarray):
        v=v[0]
    if isinstance(v, _tg_np.ndarray) and v.dtype.kind in 'biufUSO':
        values=v.reshape(-1)[:5000].tolist()
        if v.dtype.kind=='O' and not all(x is None or isinstance(x,(str,int,float,bool)) for x in values):
            return None
        values=[None if isinstance(x,(int,float)) and not _tg_np.isfinite(x) else x for x in values]
        return {"shape": list(v.shape), "values": values, "finite": bool(_tg_np.isfinite(v).all()) if v.dtype.kind in 'biuf' else True}
    if isinstance(v,list) and v and len(v)<=100 and all(isinstance(x,dict) for x in v):
        return _tg_pack(_tg_pd.DataFrame(v))
    if isinstance(v, (int, float, bool, _tg_np.number)):
        return float(v) if _tg_np.isfinite(v) else None
    if isinstance(v, (list, tuple)) and len(v) <= 100 and all(isinstance(x,(int,float,str,_tg_np.number)) for x in v):
        return [None if isinstance(x,(int,float,_tg_np.number)) and not _tg_np.isfinite(x) else x.item() if isinstance(x,_tg_np.number) else x for x in v]
    return None
_tg_result = {}
for _tg_name, _tg_value in list(globals().items()):
    if _tg_name.startswith('_') or _tg_name in ('In','Out') or any(x in _tg_name.lower() for x in ('key','secret','token','password','prompt','url','base')):
        continue
    try:
        _tg_packed = _tg_pack(_tg_value)
        if _tg_packed is not None: _tg_result[_tg_name] = _tg_packed
    except Exception:
        pass
_tg_models = {}
for _tg_name in ('model','clf','pipe','best','km','kmeans','w2v','session','ort_session'):
    _tg_obj = globals().get(_tg_name)
    if _tg_obj is None: continue
    _tg_type = type(_tg_obj)
    _tg_info = {'type':_tg_type.__module__+'.'+_tg_type.__name__}
    if _tg_type.__module__.startswith('sklearn'):
        try:
            from sklearn.utils.validation import check_is_fitted as _tg_fitted
            _tg_fitted(_tg_obj); _tg_info['fitted'] = True
            for _tg_x in ('X_test_scaled','X_test','Xte'):
                if _tg_x in globals():
                    try:
                        _tg_pred = _tg_obj.predict(globals()[_tg_x])
                        _tg_info['prediction'] = _tg_pack(_tg_np.asarray(_tg_pred)); break
                    except Exception: pass
        except Exception: _tg_info['fitted'] = False
    if _tg_type.__module__.startswith(('torch','__main__')) and hasattr(_tg_obj,'parameters'):
        try: _tg_info['parameters'] = sum(p.numel() for p in _tg_obj.parameters())
        except Exception: pass
    if _tg_type.__module__.startswith('gensim') and hasattr(_tg_obj,'wv'):
        try:
            _tg_info['vector_size']=_tg_obj.wv.vector_size
            _tg_info['vocabulary']=len(_tg_obj.wv)
            _tg_info['finite']=bool(_tg_np.isfinite(_tg_obj.wv.vectors).all())
        except Exception: pass
    _tg_models[_tg_name] = _tg_info
_tg_result['models'] = _tg_models
if '_tg_training_steps' in globals():
    _tg_result['training_steps'] = _tg_training_steps
    _tg_result['parameters_changed'] = _tg_parameters_changed
try:
    _tg_y = _tg_np.asarray(globals().get('y_test',globals().get('yte'))).reshape(-1)
    _tg_p = _tg_np.asarray(globals().get('y_pred',globals().get('pred'))).reshape(-1)
    if len(_tg_y)==len(_tg_p) and len(_tg_y):
        _tg_result['computed_accuracy'] = float((_tg_y==_tg_p).mean())
        if _tg_y.dtype.kind in 'biuf' and _tg_p.dtype.kind in 'biuf':
            _tg_result['computed_mse'] = float(((_tg_y-_tg_p)**2).mean())
            if ((_tg_y-_tg_y.mean())**2).sum()>0:
                _tg_result['computed_r2'] = float(1-((_tg_y-_tg_p)**2).sum()/((_tg_y-_tg_y.mean())**2).sum())
except Exception: pass
print('__TRAINER_RESULT__'+_tg_json.dumps(_tg_result,ensure_ascii=True,allow_nan=False))
'''

TRAINING_PROBE = r'''
import torch as _tg_torch
_tg_training_steps = 0
_tg_parameters_changed = False
def _tg_wrap_step(original):
    def step(self, *args, **kwargs):
        global _tg_training_steps, _tg_parameters_changed
        params=[p for g in self.param_groups for p in g['params'] if p.grad is not None]
        before=[p.detach().clone() for p in params]
        result=original(self,*args,**kwargs)
        _tg_training_steps += 1
        _tg_parameters_changed |= any(not _tg_torch.equal(p.detach(),old) for p,old in zip(params,before))
        return result
    return step
for _tg_class in (_tg_torch.optim.Adam,_tg_torch.optim.SGD,_tg_torch.optim.AdamW,_tg_torch.optim.RMSprop):
    _tg_class.step=_tg_wrap_step(_tg_class.step)
'''


def extract_snapshot(cell):
    for output in cell.get("outputs", []):
        text = output.get("text", "")
        text = "".join(text) if isinstance(text, list) else text
        for line in str(text).splitlines():
            if line.startswith("__TRAINER_RESULT__"):
                return json.loads(line[len("__TRAINER_RESULT__"):])
    return {}


def result_checks(qid, workspace, snapshot):
    import io
    import numpy as np
    import pandas as pd

    checks = []

    def check(label, ok, expected, actual):
        checks.append({"label": label, "ok": bool(ok), "kind": "result", "expected": str(expected),
                       "actual": str(actual), "hint": "依据本次重新运行的结果验收，不读取 Notebook 中旧输出作为得分依据。"})

    def value(name):
        v = snapshot.get(name)
        if isinstance(v, dict) and "table" in v:
            frame = pd.read_json(io.StringIO(v["table"]), orient="split")
            return frame.iloc[:, 0] if v.get("series") else frame
        if isinstance(v, dict) and "values" in v:
            return np.asarray(v["values"])
        return v

    def compare(name, expected, label=None):
        actual = value(name)
        ok = False
        try:
            if isinstance(expected, (pd.DataFrame, pd.Series)):
                if isinstance(expected, pd.Series):
                    actual, expected = actual.copy(), expected.copy()
                    actual.index = pd.Index([str(x) for x in actual.index])
                    expected.index = pd.Index([str(x) for x in expected.index])
                    pd.testing.assert_series_equal(actual.sort_index(), expected.sort_index(), check_dtype=False, check_names=False, check_categorical=False, rtol=1e-6)
                else:
                    if not isinstance(expected.index, pd.RangeIndex):
                        if [str(x) for x in actual.index] != [str(x) for x in expected.index]:
                            raise AssertionError("分组索引不一致")
                    pd.testing.assert_frame_equal(actual[expected.columns].reset_index(drop=True), expected.reset_index(drop=True), check_dtype=False, check_names=False, check_categorical=False, rtol=1e-6)
                ok = True
            else:
                ok = actual is not None and bool(np.allclose(actual, expected, rtol=1e-5, equal_nan=True))
        except (AssertionError, TypeError, ValueError, KeyError, AttributeError):
            pass
        check(label or f"运行结果：{name}", ok, str(expected)[:800], str(actual)[:800])

    def csv(filename, expected=None):
        path = workspace / filename
        try:
            frame = pd.read_csv(path)
            ok = len(frame) > 0
            if expected is not None:
                pd.testing.assert_frame_equal(frame.reset_index(drop=True), expected.reset_index(drop=True), check_dtype=False, check_categorical=False, rtol=1e-6)
            check(f"导出内容：{filename}", ok, "本次运行生成、非空、列与数据符合要求", f"{len(frame)} 行，列：{list(frame.columns)}")
            return frame
        except Exception as exc:
            check(f"导出内容：{filename}", False, "本次运行生成且内容正确", f"{type(exc).__name__}: {str(exc)[:400]}")
            return None

    def artifact(filename):
        path = workspace / filename
        ok = path.is_file() and path.stat().st_size > 0
        try:
            if ok and path.suffix in {".png", ".jpg"}:
                from PIL import Image
                with Image.open(path) as image:
                    image.verify()
            elif ok and path.suffix == ".json":
                ok = isinstance(json.loads(path.read_text(encoding="utf-8")), (dict, list))
            elif ok and path.suffix == ".xlsx":
                ok = not pd.read_excel(path).empty
            elif ok and path.suffix in {".md", ".txt"}:
                ok = len(path.read_text(encoding="utf-8").strip()) >= 20
        except Exception:
            ok = False
        check(f"本次交付文件：{filename}", ok, "本次运行新生成且格式有效的文件", "格式有效" if ok else "缺失、空文件或格式不正确")

    if not snapshot:
        check("运行结果采集", False, "成功执行后可读取实际结果", "没有采集到结果，无法验证正确性")
        return checks

    if qid.startswith("1.1."):
        files = {"1.1.1": "patient_data.csv", "1.1.2": "sensor_data.csv", "1.1.3": "credit_data.csv",
                 "1.1.4": "user_behavior_data.csv", "1.1.5": "vehicle_traffic_data.csv"}
        data = pd.read_csv(workspace / files[qid])
        if qid == "1.1.1":
            data["RiskLevel"] = np.where(data.DaysInHospital > 7, "高风险患者", "低风险患者")
            counts = data.RiskLevel.value_counts()
            compare("risk_counts", counts)
            compare("high_risk_ratio", counts.get("高风险患者", 0) / len(data), "高风险占比：人数 / 总人数")
            compare("low_risk_ratio", counts.get("低风险患者", 0) / len(data), "低风险占比：人数 / 总人数")
            for name, col, bins in [("bmi", "BMI", [0, 18.5, 24, 28, np.inf]), ("age", "Age", [0, 26, 36, 46, 56, 66, np.inf])]:
                labels = ["偏瘦", "正常", "超重", "肥胖"] if name == "bmi" else ["≤25岁", "26-35岁", "36-45岁", "46-55岁", "56-65岁", "＞65岁"]
                groups = pd.cut(data[col], bins, labels=labels, right=False)
                compare(name + "_risk_rate", data.groupby(groups, observed=False).RiskLevel.apply(lambda x: (x == "高风险患者").mean()))
                compare(name + "_patient_count", groups.value_counts())
        elif qid == "1.1.2":
            compare("sensor_stats", data.groupby("SensorType").Value.agg(["count", "mean"]))
            compare("location_stats", data[data.SensorType.isin(["Temperature", "Humidity"])].groupby(["Location", "SensorType"]).Value.mean().unstack())
            data["Value"] = data.Value.ffill().bfill()
            csv("cleaned_sensor_data.csv", data)
        elif qid == "1.1.3":
            compare("missing_values", data.isnull().sum())
            compare("duplicate_values", data.duplicated().sum())
            mask = data.Age.between(18, 70) & (data.Income > 2000) & (data.LoanAmount < data.Income * 5) & data.CreditScore.between(300, 850)
            csv("cleaned_credit_data.csv", data[mask])
        else:
            data = data.dropna().copy()
            ranges = {"Age": (18, 70), "ReviewScore": (1, 5)} if qid == "1.1.4" else {"Age": (18, 70), "Speed": (0, 200), "TravelDistance": (1, 1000), "TravelTime": (1, 1440)}
            for col in ranges:
                data[col] = data[col].astype(int if col in {"Age", "ReviewScore"} else float)
            if qid == "1.1.4":
                data["PurchaseAmount"] = data.PurchaseAmount.astype(float)
                data = data[data.PurchaseAmount > 0]
            for col, bounds in ranges.items():
                data = data[data[col].between(*bounds)]
            data = data.copy()
            if qid == "1.1.4":
                for col in ("PurchaseAmount", "ReviewScore"):
                    data[col] = (data[col] - data[col].mean()) / data[col].std()
                compare("purchase_category_counts", data.PurchaseCategory.value_counts())
                compare("gender_purchase_amount_mean", data.groupby("Gender").PurchaseAmount.mean())
                compare("data", data, "最终评价评分与购买金额标准化结果")
                csv("cleaned_user_behavior_data.csv", data)
            else:
                compare("traffic_event_counts", data.TrafficEvent.value_counts())
                compare("gender_stats", data.groupby("Gender")[["Speed", "TravelDistance", "TravelTime"]].mean())
                csv("cleaned_vehicle_traffic_data.csv", data)
            groups = pd.cut(data.Age, [18, 26, 36, 46, 56, 66, np.inf], labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"], right=False)
            compare("age_group_counts", groups.value_counts().sort_index())
    elif qid.startswith("2.1."):
        frame = csv(qid + "_cleaned_data.csv")
        if frame is not None:
            check("清洗结果完整性", not frame.isna().any().any(), "无缺失值", f"缺失值 {int(frame.isna().sum().sum())}")
            numeric = frame.select_dtypes(include="number")
            if qid == "2.1.1":
                required = ["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model year", "origin"]
                ok = all(c in numeric for c in required) and bool(np.allclose(numeric[required].mean(), 0, atol=1e-6)) and bool(np.allclose(numeric[required].std(ddof=0), 1, atol=.01))
                check("实际 Z-score 标准化", ok, "8 个数值列均值约 0、标准差约 1", str(numeric.describe().loc[["mean", "std"]])[:800])
            elif qid == "2.1.2":
                cols = [c for c in numeric if c not in {"序号", "低碳行为积极性"}]
                ok = bool(cols) and np.allclose(numeric[cols].mean(), 0, atol=1e-5)
                check("特征实际标准化", ok, "特征均值约 0，排除序号和目标列", str(numeric.mean())[:800])
            else:
                cols = {"2.1.3": [c for c in numeric if c not in {"SeriousDlqin2yrs", "IncomeToDebtRatio", "MonthlyIncomeLevel"}],
                        "2.1.4": ["年龄", "体重", "身高"],
                        "2.1.5": [c for c in numeric if c.endswith("_normalized")]}.get(qid, [])
                ok = bool(cols) and all(c in numeric and numeric[c].between(-1e-6, 1 + 1e-6).all() for c in cols)
                check("实际 Min-Max 归一化", ok, "指定特征在 [0,1]，且不能全部为常数", str(numeric.agg(["min", "max"]))[:800])
                check("归一化特征非退化", bool(cols) and any(numeric[c].nunique() > 1 for c in cols if c in numeric), "至少一个有效非恒定特征", str(cols))
            for name in ("X_train", "X_test", "y_train", "y_test"):
                item = value(name)
                check("数据划分：" + name, item is not None and len(item) > 0, "实际生成非空训练与测试数据", "存在" if item is not None else "缺失")
    elif qid.startswith("2.2.") or qid in {"6.2.2", "6.2.3", "6.2.4", "6.4.1", "6.4.2", "6.5.2"}:
        models = snapshot.get("models", {})
        fitted = [m for m in models.values() if m.get("fitted") and m.get("prediction")]
        check("实际模型训练与预测", bool(fitted), "已拟合 sklearn 模型，能在本次测试集上预测", str({n: m.get("type") for n, m in models.items()}))
        truth = value("y_test") if "y_test" in snapshot else value("yte")
        pred = value("y_pred") if "y_pred" in snapshot else value("pred")
        if pred is None and fitted:
            pred = np.asarray(fitted[0]["prediction"]["values"])
        if truth is not None and pred is not None:
            truth, pred = np.asarray(truth).reshape(-1), np.asarray(pred).reshape(-1)
            check("预测长度与真实标签一致", len(truth) == len(pred) and len(pred) > 0, "同一测试集、非空预测", f"真实 {len(truth)}，预测 {len(pred)}")
            matching = any(np.array_equal(np.asarray(m["prediction"]["values"]), pred) for m in fitted)
            check("预测结果来自实际模型", matching, "提交预测等于本次模型对测试集的预测", "一致" if matching else "缺失或不一致")
            if len(truth) == len(pred) and len(truth) and np.issubdtype(pred.dtype, np.number):
                if "mse" in snapshot and "computed_mse" in snapshot: compare("mse", snapshot["computed_mse"], "MSE 指标与真实预测一致")
                if "rmse" in snapshot and "computed_mse" in snapshot: compare("rmse", snapshot["computed_mse"] ** .5, "RMSE 指标与真实预测一致")
                if "r2" in snapshot and "computed_r2" in snapshot: compare("r2", snapshot["computed_r2"], "R2 指标与真实预测一致")
                if "accuracy" in snapshot and "computed_accuracy" in snapshot: compare("accuracy", snapshot["computed_accuracy"], "准确率与真实预测一致")
        else:
            check("实际预测与标签", False, "本次运行产生真实标签和预测结果", "缺失")
        if qid.startswith("2.2."):
            for suffix in ("_model.pkl", "_results.txt", "_report.txt"):
                artifact(qid + suffix)
    elif qid.startswith("3.2."):
        models = snapshot.get("models", {})
        check("实际 ONNX 推理会话", any(m.get("type", "").startswith("onnxruntime.") for m in models.values()), "实际的 ONNX Runtime 会话", str(models))
        name = "ort_outs" if "ort_outs" in snapshot else "output" if "output" in snapshot else "boxes"
        actual = snapshot.get(name)
        # Lists of ONNX tensors are packed separately by the probe below.
        check("实际推理输出", isinstance(actual, dict) and actual.get("finite", False) and bool(actual.get("values")), "本次推理产生非空有限数值", str(actual)[:500])
        for key in ("probabilities", "accuracy"):
            if key in snapshot:
                v = np.asarray(value(key))
                check("分类概率归一化", len(v) > 0 and (v >= 0).all() and (v <= 1).all() and np.isclose(v.sum(), 1, atol=1e-5), "概率在 [0,1] 且和为 1", str(v)[:500])
        scores = value("probabilities") if "probabilities" in snapshot else value("accuracy") if "accuracy" in snapshot else value(name)
        if scores is not None and len(np.asarray(scores).reshape(-1)):
            scores = np.asarray(scores).reshape(-1)
            if qid == "3.2.1":
                compare("top5_idx", scores.argsort()[-5:][::-1], "Top-5 索引与实际概率一致")
            elif qid in {"3.2.2", "3.2.3", "3.2.4"}:
                target = {"3.2.2":"predicted_class", "3.2.3":"predicted_label", "3.2.4":"predicted_idx"}[qid]
                compare(target, int(scores.argmax()), "预测类别等于实际输出的 argmax")
    elif qid == "5.1.1":
        images = list((workspace / "aug_face_output").glob("*"))
        inputs = [p for p in (workspace / "attendance_face").glob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        check("增强后的实际图片数量", bool(inputs) and len(images) == 2 * len(inputs), "图片总数为原始数据的两倍", f"原始 {len(inputs)}，输出 {len(images)}")
    elif qid == "5.1.2":
        labels = value("labels_2d")
        check("图像分割输出", labels is not None and len(np.unique(labels)) == 2, "两个有效分割类别", str(np.unique(labels)) if labels is not None else "缺失")
        dist = value("cluster_dist")
        check("新闻主题聚类", dist is not None and len(dist) == 12 and (dist > 0).all(), "12 个非空主题簇", str(dist)[:600])
    elif qid in {"5.1.3", "6.3.1", "6.3.2", "6.3.3"}:
        models = snapshot.get("models", {})
        check("实际神经网络参数", any(m.get("parameters", 0) > 0 for m in models.values()), "已构建且有参数的神经网络", str(models))
        check("实际优化步骤与权重更新", snapshot.get("training_steps",0)>0 and snapshot.get("parameters_changed") is True,
              "本次运行发生优化器更新，至少一个模型权重实际改变", f"优化步骤 {snapshot.get('training_steps',0)}，权重改变 {snapshot.get('parameters_changed',False)}")
        if qid != "5.1.3":
            filename = {"6.3.1": "training_history.csv", "6.3.2": "flower_history.csv", "6.3.3": "transfer_history.csv"}[qid]
            frame = value("history")
            if not isinstance(frame, pd.DataFrame):
                frame = csv(filename)
            check("实际训练记录", frame is not None and len(frame) >= 2 and any("loss" in c.lower() for c in frame.columns), "至少两轮训练的损失记录；仅构建或保存未训练模型不算完成", "有效训练记录" if frame is not None else "未找到训练记录")
        else:
            check("训练与测试样本", value("train") is not None and value("test") is not None, "实际构造训练与测试数组", "已构造" if value("train") is not None else "缺失")
            check("实际训练与测试记录", bool(re.search(r"Accuracy:\s*\d+/\d+", snapshot.get("execution_text", ""))), "本次运行的 CNN 测试准确率输出", snapshot.get("execution_text", "")[-600:])
    else:
        artifacts = {
            "5.1.4": ["word2vec.model"], "5.1.5": ["图书出版数据.xlsx", "图书出版年份分布.png", "图书出版数据分析报告.md"],
            "6.1.1": ["basic_processing.csv", "filter_comparison.png"],
            "6.1.2": ["detection_summary.csv"], "6.1.3": ["defect_report.csv"],
            "6.1.4": ["color_detection.csv"], "6.1.5": ["template_detection.csv"],
            "6.2.1": ["customer_clusters.csv", "k_selection.csv", "best_cluster_model.pkl"],
            "6.2.5": ["cluster_comparison.csv", "cluster_results.csv", "pca_tsne.png"],
            "6.2.6": ["portrait_predictions.csv", "best_gender_svc.pkl", "gender_prediction.png"],
            "6.3.4": ["detection_metrics.json", "detection_preview.png"],
            "6.3.5": ["segmentation_metrics.json", "segmentation_preview.png", "gan_samples.png"],
            "6.3.6": ["face_multitask.pt", "multitask_predictions.csv", "age_gender_prediction.png"],
            "6.4.3": ["topics.json", "recommendations.json", "topic_result.csv"],
            "6.4.4": ["ner_results.csv", "translation_results.csv"],
            "6.4.5": ["generation_results.csv", "rouge_report.json"],
            "6.5.1": ["orders_clean.xlsx", "dashboard.png", "business_report.md"],
            "6.5.3": ["rag_results.csv", "rag_evaluation.md"],
            "6.5.4": ["lora_metrics.json", "benchmark.csv", "lora_adapter/adapter_config.json"],
            "6.5.5": ["app.py", "README.md", "demo_script.md", "benchmark.csv", "evaluation_results.csv"],
        }
        for filename in artifacts.get(qid, []):
            if filename.endswith(".csv"):
                csv(filename)
            else:
                artifact(filename)
        if qid.startswith("6.1."):
            import cv2
            records = []
            if qid == "6.1.1":
                for fp in sorted((workspace / "input_images").glob("*.jpg")):
                    img = cv2.imread(str(fp))
                    h0, w0 = img.shape[:2]
                    resized = cv2.resize(img, (320, 240))
                    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
                    records.append(dict(
                        file=fp.name,
                        original_width=w0,
                        original_height=h0,
                        resized_width=320,
                        resized_height=240,
                        gray_mean=float(gray.mean()),
                        hue_mean=float(hsv[:, :, 0].mean()),
                    ))
                    stem = fp.stem
                    border = cv2.imread(str(workspace / "processed" / f"{stem}_border.jpg"))
                    mean_img = cv2.imread(str(workspace / "processed" / f"{stem}_mean.jpg"), cv2.IMREAD_GRAYSCALE)
                    gaussian_img = cv2.imread(str(workspace / "processed" / f"{stem}_gaussian.jpg"), cv2.IMREAD_GRAYSCALE)
                    median_img = cv2.imread(str(workspace / "processed" / f"{stem}_median.jpg"), cv2.IMREAD_GRAYSCALE)
                    check("边界填充尺寸：" + fp.name,
                          border is not None and border.shape[:2] == (280, 380),
                          "缩放后 320×240，上下各 20、左右各 30，输出为 380×280",
                          "有效" if border is not None else "缺失")
                    check("三种滤波输出：" + fp.name,
                          all(x is not None and x.shape == (240, 320)
                              for x in (mean_img, gaussian_img, median_img)),
                          "均值/高斯/中值滤波均生成 320×240 灰度结果",
                          "有效" if all(x is not None for x in (mean_img, gaussian_img, median_img)) else "缺失")
                csv("basic_processing.csv", pd.DataFrame(records))
            elif qid == "6.1.2":
                for fp in sorted((workspace / "road_images").glob("*.jpg")):
                    img = cv2.resize(cv2.imread(str(fp)), (640, 360))
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
                    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5)), iterations=2)
                    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    kept = [cv2.boundingRect(c) for c in contours]
                    kept = [(x,y,w,h) for x,y,w,h in kept if w*h >= 1200 and 1.2 <= w/max(h,1) <= 5]
                    records.append(dict(file=fp.name, candidates=len(kept), area_ratio=sum(w*h for x,y,w,h in kept)/(640*360)))
                    image = cv2.imread(str(workspace / "visualized" / fp.name))
                    binary_image = cv2.imread(str(workspace / "binary" / fp.name), cv2.IMREAD_GRAYSCALE)
                    edge_image = cv2.imread(str(workspace / "edges" / fp.name), cv2.IMREAD_GRAYSCALE)
                    check("可视化图像：" + fp.name, image is not None and image.shape[:2] == (360,640), "640×360 的输出图", "有效" if image is not None else "缺失")
                    check("阈值与边缘中间结果：" + fp.name,
                          binary_image is not None and edge_image is not None and binary_image.shape == (360,640) and edge_image.shape == (360,640),
                          "同时生成 640×360 的 Otsu 二值图和 Canny 边缘图",
                          "有效" if binary_image is not None and edge_image is not None else "缺失")
                csv("detection_summary.csv", pd.DataFrame(records))
            elif qid == "6.1.3":
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                for fp in sorted((workspace / "defect_images").glob("*.png")):
                    gray = cv2.imread(str(fp), cv2.IMREAD_GRAYSCALE)
                    enhanced = clahe.apply(gray)
                    bright = cv2.threshold(enhanced,180,255,cv2.THRESH_BINARY)[1]
                    dark = cv2.threshold(enhanced,70,255,cv2.THRESH_BINARY_INV)[1]
                    mask = cv2.bitwise_or(bright,dark)
                    kernel = np.ones((3,3),np.uint8)
                    mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
                    mask = cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel,iterations=2)
                    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask,8)
                    areas = [int(stats[i,cv2.CC_STAT_AREA]) for i in range(1,n) if stats[i,cv2.CC_STAT_AREA] >= 40]
                    total = sum(areas); ratio = total / mask.size
                    records.append(dict(file=fp.name,defect_count=len(areas),defect_area=total,ratio=ratio,level="正常" if ratio<.002 else "轻微" if ratio<.01 else "严重"))
                    artifact("masks/" + fp.name)
                csv("defect_report.csv", pd.DataFrame(records))
        if qid == "6.1.4":
            frame = pd.read_csv(workspace / "color_detection.csv")
            inputs = list((workspace / "color_images").glob("*.jpg"))
            ok = len(frame) == len(inputs) and len(frame) > 0 and {"file","red_objects","red_pixels"}.issubset(frame.columns)
            if ok:
                ok = (frame.red_objects > 0).all() and (frame.red_pixels > 0).all()
            check("HSV 红色目标检测结果", ok, "每张输入图都有非空红色目标与像素统计", str(frame.head())[:800])
        if qid == "6.1.5":
            frame = pd.read_csv(workspace / "template_detection.csv")
            truth = pd.read_csv(workspace / "ground_truth.csv")
            ok = len(frame) == len(truth) and {"score","center_error"}.issubset(frame.columns)
            if ok:
                ok = np.isfinite(frame.score).all() and np.isfinite(frame.center_error).all() and frame.center_error.mean() <= 2
            check("模板匹配定位结果", ok, "全部场景完成定位，平均中心误差不超过 2 像素", str(frame.head())[:800])
        if qid == "6.2.5":
            comp = pd.read_csv(workspace / "cluster_comparison.csv")
            result = pd.read_csv(workspace / "cluster_results.csv")
            names = set(comp.model.astype(str))
            ok = {"KMeans","Agglomerative","DBSCAN","GMM"}.issubset(names)
            ok = ok and {"pca_x","pca_y","tsne_x","tsne_y","kmeans","dbscan"}.issubset(result.columns)
            ok = ok and np.isfinite(result[["pca_x","pca_y","tsne_x","tsne_y"]].to_numpy()).all()
            check("多聚类与降维结果", ok, "包含四种聚类算法，以及有效的 PCA/t-SNE 二维坐标", str(comp)[:800])
        if qid == "6.2.6":
            frame = pd.read_csv(workspace / "portrait_predictions.csv")
            ok = len(frame) > 0 and {"true","pred","confidence"}.issubset(frame.columns)
            if ok:
                ok = frame.confidence.between(0,1).all() and set(frame.pred.astype(str)).issubset({"female","male"})
            check("人像二分类概率预测", ok, "测试集预测完整，类别合法且概率位于 [0,1]", str(frame.head())[:800])
        if qid == "6.3.4":
            metrics = json.loads((workspace / "detection_metrics.json").read_text(encoding="utf-8"))
            yolo = list((workspace / "yolo_labels").glob("*.txt"))
            ok = len(yolo) == len(list((workspace / "detection_images").glob("*.png"))) and len(yolo) > 0
            ok = ok and 0 <= float(metrics.get("AP50",-1)) <= 1 and 0 <= float(metrics.get("mean_iou",-1)) <= 1
            ok = ok and np.isfinite(float(metrics.get("training_loss", np.nan))) and float(metrics.get("training_loss",0)) > 0
            check("YOLO 标注与 Faster R-CNN 检测指标", ok, "YOLO 标注齐全，训练损失有效，IoU/AP50 位于 [0,1]", str(metrics))
        if qid == "6.3.5":
            metrics = json.loads((workspace / "segmentation_metrics.json").read_text(encoding="utf-8"))
            shape = metrics.get("deeplab_output_shape")
            ok = 0 <= float(metrics.get("mean_iou",-1)) <= 1 and shape == [1,2,64,64]
            check("U-Net/DeepLab 分割结果", ok, "IoU 位于 [0,1] 且 DeepLab 输出为 [1,2,64,64]", str(metrics))
        if qid == "6.3.6":
            frame = pd.read_csv(workspace / "multitask_predictions.csv")
            needed={"gender_true","gender_pred","gender_confidence","age_true","age_pred","age_confidence"}
            ok = len(frame) > 0 and needed.issubset(frame.columns)
            if ok:
                ok = frame.gender_confidence.between(0,1).all() and frame.age_confidence.between(0,1).all()
                ok = ok and set(frame.gender_pred.astype(str)).issubset({"Female","Male"})
                ok = ok and set(frame.age_pred.astype(str)).issubset({"Young","Adult","Senior"})
            check("人像多任务概率预测", ok, "性别/年龄段预测完整，两项概率均位于 [0,1]", str(frame.head())[:800])
        if qid == "6.4.4":
            ner = pd.read_csv(workspace / "ner_results.csv")
            trans = pd.read_csv(workspace / "translation_results.csv")
            ok = len(ner) == len(pd.read_csv(workspace / "ner_texts.csv")) and len(trans) == len(pd.read_csv(workspace / "translation_pairs.csv"))
            ok = ok and {"entities"}.issubset(ner.columns) and {"prediction","bleu2"}.issubset(trans.columns)
            ok = ok and trans.bleu2.between(0,1).all()
            check("NER 与 Transformer/BLEU 输出", ok, "实体结果完整，逐句 BLEU-2 位于 [0,1]", str(trans.head())[:800])
        if qid == "6.4.5":
            frame = pd.read_csv(workspace / "generation_results.csv")
            report = json.loads((workspace / "rouge_report.json").read_text(encoding="utf-8"))
            ok = len(frame) == len(pd.read_csv(workspace / "generation_tasks.csv")) and frame.rouge_l.between(0,1).all()
            ok = ok and 0 <= float(report.get("average_rouge_l",-1)) <= 1
            check("GPT 生成与 ROUGE-L 结果", ok, "所有生成任务均有结果且 ROUGE-L 位于 [0,1]", str(report))
        if qid == "6.5.4":
            metrics = json.loads((workspace / "lora_metrics.json").read_text(encoding="utf-8"))
            bench = pd.read_csv(workspace / "benchmark.csv")
            ok = 0 <= float(metrics.get("accuracy",-1)) <= 1 and 0 < float(metrics.get("trainable_ratio",0)) < 1
            ok = ok and set(bench.batch.astype(int)) == {1,8,32} and (bench.latency_ms > 0).all() and (bench.throughput > 0).all()
            check("LoRA/PEFT 与性能评测", ok, "微调指标有效，batch 1/8/32 均有正的延迟和吞吐量", str(metrics))
        if qid == "6.5.5":
            bench = pd.read_csv(workspace / "benchmark.csv")
            result = pd.read_csv(workspace / "evaluation_results.csv")
            ok = len(result) == len(pd.read_csv(workspace / "eval_questions.csv")) and {"correct","latency_ms"}.issubset(result.columns)
            ok = ok and len(bench) == 1 and 0 <= float(bench.iloc[0].accuracy) <= 1
            ok = ok and float(bench.iloc[0].avg_latency_ms) >= 0 and float(bench.iloc[0].throughput_qps) > 0
            check("创新原型功能与性能评测", ok, "评测题完整，准确率合法，延迟/吞吐量有效", str(bench))
        if qid == "6.2.1":
            selection = pd.read_csv(workspace / "k_selection.csv")
            clusters = pd.read_csv(workspace / "customer_clusters.csv")
            best_k = int(selection.loc[selection.silhouette.idxmax(), "k"])
            check("最佳 K 与实际聚类一致", selection.silhouette.between(-1,1).all() and clusters.cluster.nunique() == best_k,
                  f"最大轮廓系数对应 {best_k} 个簇", f"实际 {clusters.cluster.nunique()} 个簇")
            check("聚类模型已拟合", any(m.get("fitted") for m in snapshot.get("models", {}).values()), "已拟合的 KMeans 模型", str(snapshot.get("models", {}))[:800])
        if qid == "6.4.3":
            topics = json.loads((workspace / "topics.json").read_text(encoding="utf-8"))
            recs = json.loads((workspace / "recommendations.json").read_text(encoding="utf-8"))
            check("主题关键词数量", len(topics)==5 and all(isinstance(v,list) and len(v)==10 for v in topics.values()), "5 个主题，每主题 10 个关键词", str(topics)[:800])
            rec = recs.get("similar", [])
            check("推荐排除自身且不重复", len(rec)==5 and len(set(rec))==5 and recs.get("target") not in rec, "5 个不同的其他文档", str(recs))
        if qid == "5.1.4":
            models = snapshot.get("models", {})
            check("实际词向量模型", any(m.get("vector_size")==100 and m.get("vocabulary",0)>0 and m.get("finite") for m in models.values()), "100 维、非空、数值有效的 Word2Vec 词向量", str(models))
        if qid == "5.1.5":
            frame = pd.read_excel(workspace / "图书出版数据.xlsx")
            books = json.loads((workspace / "book_data.json").read_text(encoding="utf-8"))
            check("图书清洗数据与源数据一致", len(frame)==len(books) and {"出版年份", "评分", "定价"}.issubset(frame), f"{len(books)} 条图书及数值字段", f"{len(frame)} 条，列：{list(frame.columns)}")
        if qid == "6.5.3":
            frame = pd.read_csv(workspace / "rag_results.csv")
            questions = pd.read_csv(workspace / "questions.csv")
            valid = len(frame)==len(questions) and {"question","answer","sources","score","latency"}.issubset(frame)
            if valid:
                expected = [sum(k in str(a) for k in str(keys).split(','))/len(str(keys).split(',')) for a,keys in zip(frame.answer,questions.expected_keywords)]
                valid = np.allclose(frame.score,expected) and frame.sources.notna().all() and (frame.latency>=0).all()
            check("RAG 覆盖率与实际回答一致", valid, "逐题重新计算关键词覆盖率，来源非空，耗时有效", str(frame.head())[:800])
        if qid == "6.5.1":
            frame = value("df")
            if isinstance(frame, pd.DataFrame) and {"price", "qty", "sales"}.issubset(frame):
                check("销售额等于单价乘数量", np.allclose(frame.sales, frame.price * frame.qty), "sales = price * qty", str(frame[["price", "qty", "sales"]].head()))
                compare("aov", frame.sales.sum() / frame.order_id.nunique(), "实际客单价")
                compare("repeat_rate", float((frame.groupby("customer_id").order_id.nunique() > 1).mean()), "实际复购率")
            else:
                check("订单经营指标", False, "完整订单及销售额数据", "缺失")
    additional = {"6.2.2": ["best_churn_model.pkl", "predictions.csv", "metrics.json"],
                  "6.2.3": ["model_comparison.csv", "best_house_model.pkl", "test_predictions.csv"],
                  "6.2.4": ["classifier_comparison.csv"],
                  "6.3.1": ["shape_cnn.pt"], "6.3.3": ["best_resnet18.pt"],
                  "6.4.1": ["class_keywords.json", "news_classifier.pkl"],
                  "6.4.2": ["reviews_word2vec.model"],
                  "6.5.2": ["complaint_results.xlsx", "ai_actions.json"]}
    for filename in additional.get(qid, []):
        csv(filename) if filename.endswith(".csv") else artifact(filename)
    if qid == "6.5.2":
        frame = pd.read_excel(workspace / "complaint_results.xlsx")
        negative = ["生气","差","破损","未处理","不回复"]
        expected = (frame.amount>2000).astype(int)+frame.text.apply(lambda s:any(w in str(s) for w in negative)).astype(int)+frame.pred_category.isin(["退款","质量"]).astype(int)
        check("优先级分数与投诉数据一致", np.array_equal(frame.priority_score,expected), "金额、负面词和类别三个条件相加", str(frame[["priority_score"]].head()))
    if not checks:
        check("结果验收规则", False, "配置对应题目的结果验收", "未配置，不能计为通过")
    return checks
