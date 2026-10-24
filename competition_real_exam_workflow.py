#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""为 6.x 竞赛强化题补充更接近真实样题的完整任务链。

该模块只负责给生成的 Notebook 追加“输入核验 -> 数据质量记录 -> matplotlib 可视化 ->
结果交付”训练，不改变各题原有核心算法 TODO。这样可以在 25 道题中重复训练比赛必考的
文件读取、数据检查、结果展示和保存能力。
"""

from __future__ import annotations

INPUT_SPECS = {
    "6.1.1": ("image", "input_images", "*.jpg", "输入图像"),
    "6.1.2": ("image", "road_images", "*.jpg", "道路图像"),
    "6.1.3": ("image", "defect_images", "*.png", "缺陷图像"),
    "6.1.4": ("image", "color_images", "*.jpg", "颜色目标图像"),
    "6.1.5": ("csv", "ground_truth.csv", "", "模板定位真值"),
    "6.2.1": ("csv", "customer_behavior.csv", "", "客户行为数据"),
    "6.2.2": ("csv", "telecom_churn.csv", "", "客户流失数据"),
    "6.2.3": ("csv", "housing.csv", "", "房价数据"),
    "6.2.4": ("csv", "classification.csv", "", "二分类数据"),
    "6.2.5": ("csv", "cluster_features.csv", "", "聚类特征数据"),
    "6.3.1": ("imagefolder", "shape_images", "", "三类图形数据集"),
    "6.3.2": ("imagefolder", "flower_images", "", "四类花卉数据集"),
    "6.3.3": ("imagefolder", "scene_images", "", "四类场景数据集"),
    "6.3.4": ("csv", "annotations.csv", "", "目标检测标注"),
    "6.3.5": ("image", "seg_images", "*.png", "分割图像"),
    "6.4.1": ("csv", "news_train.csv", "", "新闻分类语料"),
    "6.4.2": ("csv", "reviews.csv", "", "商品评论数据"),
    "6.4.3": ("csv", "corpus_news.csv", "", "新闻主题语料"),
    "6.4.4": ("csv", "translation_pairs.csv", "", "翻译语料"),
    "6.4.5": ("csv", "generation_tasks.csv", "", "文本生成任务"),
    "6.5.1": ("json", "orders.json", "", "订单 JSON"),
    "6.5.2": ("csv", "complaints.csv", "", "投诉数据"),
    "6.5.3": ("csv", "questions.csv", "", "RAG 评测问题"),
    "6.5.4": ("npz", "lora_train.npz", "", "LoRA 训练数组"),
    "6.5.5": ("csv", "eval_questions.csv", "", "原型评测问题"),
}

PLOT_SPECS = {
    "6.1.1": ("csv_bar", "basic_processing.csv", "file", "gray_mean", "灰度均值统计", "灰度均值", "basic_processing_chart.png"),
    "6.1.2": ("csv_bar", "detection_summary.csv", "file", "candidates", "车辆候选区域数量", "候选数量", "detection_summary_chart.png"),
    "6.1.3": ("csv_bar", "defect_report.csv", "file", "defect_area", "缺陷总面积统计", "缺陷面积", "defect_area_chart.png"),
    "6.1.4": ("csv_bar", "color_detection.csv", "file", "red_objects", "红色目标数量统计", "目标数量", "red_object_chart.png"),
    "6.1.5": ("csv_bar", "template_detection.csv", "file", "center_error", "模板匹配定位误差", "中心误差", "template_error_chart.png"),
    "6.2.1": ("csv_line", "k_selection.csv", "k", "silhouette", "不同 K 的轮廓系数", "Silhouette Score", "k_selection_chart.png"),
    "6.2.2": ("json_bar", "metrics.json", "", "", "客户流失分类指标", "Score", "churn_metrics_chart.png"),
    "6.2.3": ("csv_bar", "model_comparison.csv", "model", "RMSE", "回归模型 RMSE 对比", "RMSE", "house_model_chart.png"),
    "6.2.4": ("csv_bar", "classifier_comparison.csv", "model", "f1", "分类器 F1 对比", "F1", "classifier_f1_chart.png"),
    "6.2.5": ("csv_bar", "cluster_comparison.csv", "model", "silhouette", "聚类算法轮廓系数对比", "Silhouette Score", "cluster_score_chart.png"),
    "6.3.1": ("csv_line", "training_history.csv", "epoch", "loss", "CNN 训练损失曲线", "Loss", "cnn_loss_chart.png"),
    "6.3.2": ("dataset_size", "", "", "", "花卉训练/验证样本量", "Samples", "flower_split_chart.png"),
    "6.3.3": ("dataset_size", "", "", "", "场景训练/验证样本量", "Samples", "scene_split_chart.png"),
    "6.3.4": ("json_detection", "detection_metrics.json", "", "", "目标检测指标", "Score", "detection_metrics_chart.png"),
    "6.3.5": ("json_iou", "segmentation_metrics.json", "", "", "语义分割 IoU", "IoU", "segmentation_iou_chart.png"),
    "6.4.1": ("input_count", "", "label", "", "新闻类别样本分布", "Samples", "news_class_chart.png"),
    "6.4.2": ("input_count", "", "label", "", "评论情感标签分布", "Samples", "review_label_chart.png"),
    "6.4.3": ("csv_count", "topic_result.csv", "dominant_topic", "", "LDA 主主题分布", "Documents", "topic_distribution_chart.png"),
    "6.4.4": ("csv_bar_index", "translation_results.csv", "source", "bleu2", "翻译 BLEU-2 结果", "BLEU-2", "bleu_chart.png"),
    "6.4.5": ("csv_group", "generation_results.csv", "task", "rouge_l", "各生成任务平均 ROUGE-L", "ROUGE-L", "rouge_chart.png"),
    "6.5.1": ("input_count", "", "category", "", "订单品类分布", "Orders", "order_category_chart.png"),
    "6.5.2": ("core_count", "", "priority", "", "投诉优先级分布", "Complaints", "complaint_priority_chart.png"),
    "6.5.3": ("csv_bar_index", "rag_results.csv", "question", "score", "RAG 关键词覆盖率", "Score", "rag_score_chart.png"),
    "6.5.4": ("csv_line", "benchmark.csv", "batch", "throughput", "LoRA 推理吞吐量", "Samples/s", "lora_throughput_chart.png"),
    "6.5.5": ("csv_bar_index", "evaluation_results.csv", "question", "correct", "智慧校园原型评测结果", "Correct", "prototype_eval_chart.png"),
}


def enhance_task(qid: str, task: str) -> str:
    kind, path, pattern, label = INPUT_SPECS[qid]
    _pkind, _source, _x, _y, plot_title, _ylabel, plot_file = PLOT_SPECS[qid]
    if kind == "image":
        read_note = f"枚举 {path}/{pattern}，读取首个样本并检查数量、shape、dtype"
    elif kind == "imagefolder":
        read_note = f"使用 ImageFolder 重新读取 {path}，核对类别名称、类别数量和样本数量"
    elif kind == "npz":
        read_note = f"重新读取 {path}，核对数组键、shape 和 dtype"
    else:
        read_note = f"重新读取 {path}，检查 shape、字段类型、缺失值和前几行数据"
    return (
        task
        + "\n\n## 竞赛化完整任务链"
        + f"\n1. **输入核验**：{read_note}。"
        + "\n2. **核心处理**：按前述 TODO 完成清洗、预处理、建模/算法处理与指标计算，不跳过中间结果检查。"
        + f"\n3. **结果可视化**：使用 matplotlib 完成“{plot_title}”，必须设置标题、坐标轴标签，并保存图片。"
        + f"\n4. **交付核验**：额外生成 data_quality_check.csv 和 {plot_file}，确认关键结果文件可重新读取。"
        + "\n5. **操作要求**：按 Notebook 从上到下运行全部单元格，保存后再提交，不能只填写算法函数而跳过读取、检查和输出步骤。"
    )


def _input_block(qid: str):
    kind, path, pattern, label = INPUT_SPECS[qid]
    if kind in {"csv", "json"}:
        reader = f'pd.read_csv("{path}")' if kind == "csv" else f'pd.read_json("{path}")'
        code = f'''import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# TODO 9-1：重新读取{label}，用于交付前的数据质量核验
audit_df = _____________
print("shape =", audit_df.shape)
print("dtypes =")
print(audit_df.dtypes)
print("missing =")
print(audit_df.isna().sum())

# TODO 9-2：删除完全重复记录，保留独立清洗副本
audit_clean = _____________
quality = pd.DataFrame({{
    "column": audit_clean.columns.astype(str),
    "dtype": audit_clean.dtypes.astype(str).to_numpy(),
    "missing": audit_clean.isna().sum().to_numpy(),
}})
# TODO 9-3：将字段类型和缺失值统计保存为 UTF-8-SIG CSV
_____________'''
        answers = [reader, 'audit_df.drop_duplicates().copy()',
                   'quality.to_csv("data_quality_check.csv",index=False,encoding="utf-8-sig")']
        return code, answers

    if kind == "image":
        code = f'''import cv2
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

audit_files = sorted(Path("{path}").glob("{pattern}"))
assert audit_files, "未找到输入图像"
# TODO 9-1：使用 OpenCV 读取首个输入图像，保留原始通道信息
audit_image = _____________
print("images =", len(audit_files), "shape =", audit_image.shape, "dtype =", audit_image.dtype)

quality = pd.DataFrame([{{
    "file_count": len(audit_files),
    "height": audit_image.shape[0],
    "width": audit_image.shape[1],
    "channels": 1 if audit_image.ndim == 2 else audit_image.shape[2],
    "dtype": str(audit_image.dtype),
}}])
# TODO 9-2：保存图像输入核验结果
_____________'''
        answers = ['cv2.imread(str(audit_files[0]),cv2.IMREAD_UNCHANGED)',
                   'quality.to_csv("data_quality_check.csv",index=False,encoding="utf-8-sig")']
        return code, answers

    if kind == "imagefolder":
        code = f'''import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from torchvision.datasets import ImageFolder
from torchvision import transforms

# TODO 9-1：使用 ImageFolder 重新读取{label}
audit_dataset = _____________
class_counts = pd.Series([y for _, y in audit_dataset.samples]).value_counts().sort_index()
quality = pd.DataFrame({{
    "class_name": audit_dataset.classes,
    "samples": [int(class_counts.get(i, 0)) for i in range(len(audit_dataset.classes))],
}})
print("classes =", audit_dataset.classes)
print("samples =", len(audit_dataset))
# TODO 9-2：保存类别与样本数核验结果
_____________'''
        answers = [f'ImageFolder("{path}",transform=transforms.ToTensor())',
                   'quality.to_csv("data_quality_check.csv",index=False,encoding="utf-8-sig")']
        return code, answers

    if kind == "npz":
        code = f'''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# TODO 9-1：重新读取 NPZ 训练数据
audit_npz = _____________
quality = pd.DataFrame([{{
    "arrays": ",".join(audit_npz.files),
    "input_shape": str(audit_npz["input_ids"].shape),
    "label_shape": str(audit_npz["labels"].shape),
    "input_dtype": str(audit_npz["input_ids"].dtype),
    "label_dtype": str(audit_npz["labels"].dtype),
}}])
print(quality)
# TODO 9-2：保存数组结构核验结果
_____________'''
        answers = [f'np.load("{path}")',
                   'quality.to_csv("data_quality_check.csv",index=False,encoding="utf-8-sig")']
        return code, answers

    raise KeyError(qid)


def _plot_block(qid: str):
    kind, source, x, y, title, ylabel, output = PLOT_SPECS[qid]
    head = 'plt.figure(figsize=(9, 4.8))'
    if kind == "csv_bar":
        setup = f'plot_df=pd.read_csv("{source}")'
        expr = f'plt.bar(plot_df["{x}"].astype(str),plot_df["{y}"])'
    elif kind == "csv_line":
        setup = f'plot_df=pd.read_csv("{source}")'
        expr = f'plt.plot(plot_df["{x}"],plot_df["{y}"],marker="o")'
    elif kind == "csv_bar_index":
        setup = f'plot_df=pd.read_csv("{source}")'
        expr = f'(plt.bar(range(len(plot_df)),plot_df["{y}"]),plt.xticks(range(len(plot_df)),plot_df["{x}"].astype(str),rotation=45,ha="right"))'
    elif kind == "csv_group":
        setup = f'plot_df=pd.read_csv("{source}"); plot_group=plot_df.groupby("{x}")["{y}"].mean()'
        expr = 'plt.bar(plot_group.index.astype(str),plot_group.values)'
    elif kind == "csv_count":
        setup = f'plot_df=pd.read_csv("{source}"); plot_group=plot_df["{x}"].value_counts().sort_index()'
        expr = 'plt.bar(plot_group.index.astype(str),plot_group.values)'
    elif kind == "json_bar":
        setup = f'import json\nplot_data=json.load(open("{source}",encoding="utf-8"))\nplot_keys=["accuracy","precision","recall","f1"]'
        expr = 'plt.bar(plot_keys,[plot_data[k] for k in plot_keys])'
    elif kind == "json_detection":
        setup = f'import json\nplot_data=json.load(open("{source}",encoding="utf-8"))\nplot_keys=["AP50","mean_iou"]'
        expr = 'plt.bar(plot_keys,[plot_data[k] for k in plot_keys])'
    elif kind == "json_iou":
        setup = f'import json\nplot_data=json.load(open("{source}",encoding="utf-8"))'
        expr = 'plt.bar(["mean_iou"],[plot_data["mean_iou"]])'
    elif kind == "dataset_size":
        setup = ''
        expr = 'plt.bar(["train","val"],[len(train_ds),len(val_ds)])'
    elif kind == "input_count":
        setup = f'plot_group=audit_df["{x}"].value_counts().sort_index()'
        expr = 'plt.bar(plot_group.index.astype(str),plot_group.values)'
    elif kind == "core_count":
        setup = f'plot_group=df["{x}"].astype(str).value_counts().sort_index()'
        expr = 'plt.bar(plot_group.index.astype(str),plot_group.values)'
    else:
        raise KeyError((qid, kind))

    code = f'''{setup}
{head}
# TODO 10-1：使用 matplotlib 绘制指定结果图
_____________
plt.title("{title}")
plt.xlabel("{x or "Category"}")
plt.ylabel("{ylabel}")
plt.xticks(rotation=45,ha="right")
plt.tight_layout()
# TODO 10-2：以 150 dpi 保存可视化结果
_____________
plt.show()

assert Path("data_quality_check.csv").is_file()
assert Path("{output}").is_file()
print("交付核验通过：data_quality_check.csv, {output}")'''
    answers = [expr, f'plt.savefig("{output}",dpi=150,bbox_inches="tight")']
    return code, answers


def extra_workflow_code(qid: str) -> str:
    input_code, _ = _input_block(qid)
    plot_code, _ = _plot_block(qid)
    return input_code + "\n\n" + plot_code


def extra_workflow_answers(qid: str) -> list[str]:
    _, input_answers = _input_block(qid)
    _, plot_answers = _plot_block(qid)
    return input_answers + plot_answers
