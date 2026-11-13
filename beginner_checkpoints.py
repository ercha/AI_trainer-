"""30 节零基础 Notebook 的可执行练习检查点（本地运行，无代码执行 HTTP 接口）。"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent
GRADE_DIR = ROOT / "_beginner_grades"
CHECKPOINTS = {
  "A1": [
    "创建 3×3 的全零 uint8 数组，赋给 answer_a1。",
    "isinstance(v,np.ndarray) and v.shape==(3,3) and v.dtype==np.uint8 and np.all(v==0)",
    "应为 shape=(3,3)、uint8 的全零数组"
  ],
  "A2": [
    "生成 60×80 纯色图，保存为含「练习」的中文 PNG 文件，路径赋给 answer_a2。",
    "Path(v).is_file() and Path(v).suffix.lower()=='.png' and '练习' in Path(v).name and Path(v).stat().st_size>0",
    "确保图片已保存到磁盘，文件名应包含『练习』"
  ],
  "A3": [
    "将 100×200 的彩色数组缩放为宽 50、高 25，结果赋给 answer_a3。",
    "isinstance(v,np.ndarray) and v.shape==(25,50,3)",
    "cv2.resize 接受 (宽,高)，而 shape 是 (高,宽,通道)"
  ],
  "A4": [
    "对本课 img 使用 3×3 高斯核、sigmaX=0 滤波，结果赋给 answer_a4。",
    "isinstance(v,np.ndarray) and v.shape==(60,60) and np.array_equal(v,__import__('cv2').GaussianBlur(g['img'],(3,3),0))",
    "重新用 cv2.GaussianBlur 执行 3×3 高斯滤波"
  ],
  "A5": [
    "用 3×3 核对示例 mask 做闭运算，结果赋给 answer_a5。",
    "isinstance(v,np.ndarray) and v.shape==(100,100) and np.array_equal(v,__import__('cv2').morphologyEx(g['mask'],__import__('cv2').MORPH_CLOSE,np.ones((3,3),np.uint8)))",
    "应使用 MORPH_CLOSE 而不是 MORPH_OPEN"
  ],
  "A6": [
    "计算本课最大轮廓面积，把数值赋给 answer_a6。",
    "np.isscalar(v) and abs(float(v)-2500)<1e-6",
    "示例正方形边长 50，轮廓面积 2500"
  ],
  "B1": [
    "统计 df['通过'] 各类别数量，将结果赋给 answer_b1。",
    "hasattr(v,'to_dict') and v.to_dict()=={0:1,1:2}",
    "使用 value_counts() 统计 0 和 1"
  ],
  "B2": [
    "使用已 fit 的 imp、scaler 处理 [[3.0]]，结果赋给 answer_b2。",
    "isinstance(v,np.ndarray) and v.shape==(1,1) and np.isfinite(v).all() and np.allclose(v,g['scaler'].transform(g['imp'].transform([[3.0]])))",
    "只能 transform 新数据，不要 fit 新数据"
  ],
  "B3": [
    "训练 KNeighborsClassifier(n_neighbors=5)，将模型赋给 answer_b3。",
    "type(v).__name__=='KNeighborsClassifier' and v.n_neighbors==5 and len(v.predict(g['Xte']))==len(g['yte'])",
    "模型需要先 fit(Xtr,ytr)"
  ],
  "B4": [
    "将 LogisticRegression(max_iter=300) 加入 Pipeline，训练后赋给 answer_b4。",
    "type(v).__name__=='Pipeline' and type(v.steps[-1][1]).__name__=='LogisticRegression' and len(v.predict(g['Xte']))==len(g['yte'])",
    "Pipeline 最后应为训练好的 LogisticRegression"
  ],
  "B5": [
    "训练 RandomForestRegressor(n_estimators=100,random_state=42)，赋给 answer_b5。",
    "type(v).__name__=='RandomForestRegressor' and v.n_estimators==100 and len(v.predict(g['Xte']))==len(g['yte'])",
    "模型必须 fit(Xtr,ytr) 后才能预测"
  ],
  "B6": [
    "用 k=2、3、4 分别计算 silhouette_score，存为字典 answer_b6。",
    "isinstance(v,dict) and set(v)=={2,3,4} and all(np.isfinite(float(x)) and -1<=float(x)<=1 for x in v.values())",
    "字典键必须为 2、3、4，值为轮廓系数"
  ],
  "C1": [
    "创建 (2,3) 的全零 Tensor，移到本课 device，赋给 answer_c1。",
    "tuple(v.shape)==(2,3) and str(v.device)==str(g['device']) and bool((v==0).all())",
    "检查 shape 和 device"
  ],
  "C2": [
    "创建 3→16→2 的 Sequential 网络，赋给 answer_c2。",
    "type(v).__name__=='Sequential' and [x.out_features for x in v.modules() if type(x).__name__=='Linear']==[16,2]",
    "中间隐藏层输出 16 维，最后输出 2 类"
  ],
  "C3": [
    "完成 200 次训练后把最终 MSE 损失数值赋给 answer_c3。",
    "np.isscalar(v) and np.isfinite(float(v)) and 0<=float(v)<0.2",
    "检查 zero_grad、backward、step 是否正常执行"
  ],
  "C4": [
    "把本课 CNN 的 batch 改为 5，输出赋给 answer_c4。",
    "tuple(v.shape)==(5,10)",
    "输出应是 (5,10)"
  ],
  "C5": [
    "比较保存前后模型对相同输入的预测是否一致，布尔值赋给 answer_c5。",
    "isinstance(v,(bool,np.bool_)) and bool(v)",
    "可用 torch.allclose(net(x),loaded(x))"
  ],
  "C6": [
    "让检测框完全重合，把 IoU 数值赋给 answer_c6。",
    "np.isscalar(v) and abs(float(v)-1)<1e-6",
    "完全重合时 IoU=1"
  ],
  "D1": [
    "使用 jieba 精确分词『机器学习与图像处理』，列表赋给 answer_d1。",
    "isinstance(v,list) and len(v)>1 and ''.join(v)=='机器学习与图像处理'",
    "分词列表拼接后应和原句一样"
  ],
  "D2": [
    "添加一条『科技 计算机 算法』，重新向量化 4 条文本，矩阵赋给 answer_d2。",
    "hasattr(v,'shape') and v.shape[0]==4 and v.shape[1]>=5",
    "TF-IDF 矩阵应有 4 行"
  ],
  "D3": [
    "预测『科技 软件』的标签，结果赋给 answer_d3。",
    "np.asarray(v).shape==(1,) and int(np.asarray(v)[0])==1",
    "调用 pipe.predict(['科技 软件'])，结果应为 1"
  ],
  "D4": [
    "计算第一篇文本的两个主题概率，向量赋给 answer_d4。",
    "np.asarray(v).shape==(2,) and np.isfinite(v).all() and abs(float(np.sum(v))-1)<1e-5",
    "主题概率应是长度 2 的一维数组，求和为 1"
  ],
  "D5": [
    "用概率 [0.2,0.3,0.5] 采样十次，结果赋给 answer_d5。",
    "np.asarray(v).shape==(10,) and np.isin(v,[0,1,2]).all()",
    "np.random.choice 的 size=10、p 为一维概率"
  ],
  "D6": [
    "把本课 BLEU-2 和 ROUGE-L F1 两个数放入 answer_d6 元组。",
    "isinstance(v,(tuple,list)) and len(v)==2 and all(np.isfinite(float(x)) and 0<=float(x)<=1 for x in v) and abs(float(v[0])-float(g['bleu2']))<1e-6 and abs(float(v[1])-float(g['rouge_l']))<1e-6",
    "应使用本课真实计算出的 bleu2 和 rouge_l"
  ],
  "E1": [
    "在交付清单中增加 predictions.csv，列表赋给 answer_e1。",
    "isinstance(v,list) and all(x in v for x in ['cleaned.csv','chart.png','report.md','predictions.csv'])",
    "要保留原有文件名并加 predictions.csv"
  ],
  "E2": [
    "导出 UTF-8-SIG 的 cleaned.csv 且 index=False，路径赋给 answer_e2。",
    "Path(v).is_file() and Path(v).read_bytes()[:3]==bytes([239,187,191]) and '销售额' in Path(v).read_text(encoding='utf-8-sig').splitlines()[0] and not Path(v).read_text(encoding='utf-8-sig').splitlines()[0].startswith(',')",
    "to_csv(...,index=False,encoding='utf-8-sig')"
  ],
  "E3": [
    "将折线图保存为 output/line.png，路径赋给 answer_e3。",
    "Path(v).is_file() and Path(v).name=='line.png' and Path(v).stat().st_size>100",
    "必须真实生成 output/line.png 文件"
  ],
  "E4": [
    "编写 answer_e4(url) 函数，判断 http/https 链接是否合法。",
    "callable(v) and bool(v('https://example.com')) and bool(v('http://127.0.0.1:8000')) and not bool(v('ftp://example.com')) and not bool(v(''))",
    "应支持 http/https，拒绝 ftp、空字符串"
  ],
  "E5": [
    "检索『需要预约实验室吗』，把最相关段落赋给 answer_e5。",
    "isinstance(v,str) and v=='实验室需预约'",
    "重新构建 query 向量并计算相似度"
  ],
  "E6": [
    "用 answer_e6 字典记录 README.md、output/chart.png、output/line.png 是否存在。",
    "isinstance(v,dict) and set(v)=={'README.md','output/chart.png','output/line.png'} and all(v[k]==Path(k).exists() for k in v)",
    "字典每个值应是 Path(k).exists()"
  ]
}


def check_lesson(lesson_id: str, namespace: dict, *, save: bool = True) -> dict:
    if lesson_id not in CHECKPOINTS:
        raise ValueError(f"未知课程编号：{lesson_id}")
    task, expression, hint = CHECKPOINTS[lesson_id]
    name = "answer_" + lesson_id.lower()
    if name not in namespace:
        raise AssertionError(f"{lesson_id} 尚未提交：请定义 {name}。任务：{task}")
    v = namespace[name]
    try:
        # 表达式固定写在项目源码中；本函数只能从用户本机的 Jupyter 主动调用。
        scope = {
            "np": np, "Path": Path, "__import__": __import__, "bytes": bytes,
            "isinstance": isinstance, "hasattr": hasattr, "bool": bool,
            "str": str, "len": len, "float": float, "int": int,
            "set": set, "all": all, "type": type, "tuple": tuple,
            "list": list, "callable": callable, "abs": abs,
            "v": v, "g": namespace,
        }
        # Generator/comprehension expressions must also see submitted variables.
        passed = bool(eval(expression, scope, scope))
    except Exception as exc:
        raise AssertionError(f"{lesson_id} 检查异常：{type(exc).__name__}: {exc}。提示：{hint}") from exc
    if not passed:
        raise AssertionError(f"{lesson_id} 未通过。提示：{hint}")
    report = {"lesson_id": lesson_id, "passed": True, "version": 1,
              "checked_at": datetime.now(timezone.utc).isoformat()}
    if save:
        GRADE_DIR.mkdir(parents=True, exist_ok=True)
        (GRADE_DIR / f"{lesson_id}.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"PASS {lesson_id}：自动检查通过。回到课程页面同步 Notebook 检查结果。")
    return report
