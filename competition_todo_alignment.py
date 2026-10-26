#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""补齐 6.x 强化题题面 TODO 与 Notebook 实际练习点的对应关系。

历史生成器中不少题目把题面 TODO 3/4/5（训练、评价、保存、可视化）直接写成了完整代码。
本模块在核心题目单元之后追加对应的“任务复现”单元，使题面列出的每个 TODO 组都至少包含
一个真正需要学生填写的表达式，并保持参考答案可自动还原。
"""

from __future__ import annotations

EXPECTED_TODO_GROUPS = {
    **{f"6.{m}.{i}": tuple(range(0, 7)) for m in range(1, 6) for i in range(1, 6)},
    "6.2.6": tuple(range(0, 7)),
    "6.3.6": tuple(range(0, 7)),
    "6.5.1": tuple(range(0, 8)),
    "6.5.2": tuple(range(0, 8)),
    "6.5.3": tuple(range(0, 8)),
}

ALIGNMENT = {
"6.1.2": (r'''
# TODO 3-1：从闭运算结果重新提取外轮廓
audit_contours,_ = _____________
# TODO 3-2：按面积和宽高比筛选候选框
audit_boxes = _____________
# TODO 4-1：保存当前二值图、边缘图和绘框结果
save_flags = _____________
# TODO 5-1：由 records 构造汇总表
detection_summary = _____________
# TODO 5-2：保存 detection_summary.csv
_____________
''', [
'cv2.findContours(closed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)',
'[(x,y,w,h) for c in audit_contours for x,y,w,h in [cv2.boundingRect(c)] if w*h>=1200 and 1.2<=w/max(h,1)<=5.0]',
'(cv2.imwrite(str(BIN/fp.name),binary),cv2.imwrite(str(EDGE/fp.name),edges),cv2.imwrite(str(VIS/fp.name),img))',
'pd.DataFrame(records)',
'detection_summary.to_csv("detection_summary.csv",index=False)',
]),
"6.1.3": (r'''
# TODO 2-1：合并亮缺陷与暗缺陷掩膜
combined_mask = _____________
# TODO 3-1：对过滤后的缺陷掩膜执行连通域统计
component_result = _____________
# TODO 4-1：按缺陷面积占比重新判定当前样本等级
audit_level = _____________
# TODO 5-1：构造缺陷统计表
defect_table = _____________
# TODO 5-2：保存掩膜、可视化图和 defect_report.csv
_____________
''', [
'cv2.bitwise_or(bright,dark)',
'cv2.connectedComponentsWithStats(keep,8)',
'"正常" if ratio<0.002 else ("轻微" if ratio<0.01 else "严重")',
'pd.DataFrame(rows)',
'(cv2.imwrite(str(MASK/fp.name),keep),cv2.imwrite(str(VIS/fp.name),cv2.cvtColor(gray,cv2.COLOR_GRAY2BGR)),defect_table.to_csv("defect_report.csv",index=False,encoding="utf-8-sig"))',
]),
"6.1.4": (r'''
# TODO 3-1：从清理后的红色掩膜提取外轮廓
audit_contours,_ = _____________
# TODO 3-2：筛选面积不少于 500 的红色目标轮廓
large_contours = _____________
# TODO 4-1：保存红色掩膜和绘框结果
save_flags = _____________
# TODO 5-1：构造颜色检测统计表
color_table = _____________
# TODO 5-2：保存 color_detection.csv
_____________
''', [
'cv2.findContours(clean,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)',
'[c for c in audit_contours if cv2.contourArea(c)>=500]',
'(cv2.imwrite(str(MASK/fp.name),clean),cv2.imwrite(str(VIS/fp.name),img))',
'pd.DataFrame(rows)',
'color_table.to_csv("color_detection.csv",index=False)',
]),
"6.1.5": (r'''
# TODO 2-1：使用 TM_CCOEFF_NORMED 重新计算模板匹配结果
audit_match = _____________
# TODO 3-1：取得最大匹配分数和位置
_,audit_score,_,audit_loc = _____________
# TODO 4-1：复制当前场景图用于绘框
audit_vis = _____________
# TODO 4-2：绘制检测框并保存可视化图
_____________
# TODO 5-1：合并预测与 ground_truth
audit_eval = _____________
# TODO 5-2：计算中心点定位误差
audit_eval["center_error"] = _____________
# TODO 5-3：保存 template_detection.csv
_____________
''', [
'cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)',
'cv2.minMaxLoc(audit_match)',
'img.copy()',
'(cv2.rectangle(audit_vis,audit_loc,(audit_loc[0]+tw,audit_loc[1]+th),(0,255,0),2),cv2.imwrite(str(OUT/fp.name),audit_vis))',
'pred.merge(truth,on="file",suffixes=("_pred","_true"))',
'((audit_eval.x_pred-audit_eval.x_true)**2+(audit_eval.y_pred-audit_eval.y_true)**2)**0.5',
'audit_eval.to_csv("template_detection.csv",index=False)',
]),
"6.2.1": (r'''
# TODO 3-1：根据轮廓系数重新取得最佳 K
audit_best_k = _____________
# TODO 4-1：统计各聚类的样本数和数值特征均值
cluster_profile = _____________
# TODO 5-1：保存聚类结果、K 选择结果和最佳模型
_____________
''', [
'int(scores.loc[scores.silhouette.idxmax(),"k"])',
'df.groupby("cluster")[num].agg(["count","mean"])',
'(df.to_csv("customer_clusters.csv",index=False),scores.to_csv("k_selection.csv",index=False),joblib.dump((pre,best),"best_cluster_model.pkl"))',
]),
"6.2.2": (r'''
# TODO 3-1：使用调优后的模型预测测试集并计算四项分类指标
audit_pred = _____________
audit_metrics = _____________
# TODO 4-1：按题目网格重新建立以 F1 为评分的 GridSearchCV
audit_search = _____________
# TODO 5-1：保存最佳模型、预测结果和 metrics.json
_____________
''', [
'search.predict(X_test)',
'{"accuracy":accuracy_score(y_test,audit_pred),"precision":precision_score(y_test,audit_pred,zero_division=0),"recall":recall_score(y_test,audit_pred,zero_division=0),"f1":f1_score(y_test,audit_pred,zero_division=0)}',
'GridSearchCV(pipe,grid,scoring="f1",cv=4,n_jobs=-1)',
'(joblib.dump(search.best_estimator_,"best_churn_model.pkl"),pd.DataFrame({"y_true":y_test,"y_pred":audit_pred}).to_csv("predictions.csv",index=False),open("metrics.json","w",encoding="utf-8").write(json.dumps(audit_metrics,ensure_ascii=False,indent=2)))',
]),
"6.2.3": (r'''
# TODO 3-1：建立三种回归模型字典
audit_models = _____________
# TODO 4-1：整理 RMSE 与 R² 对比结果
audit_comparison = _____________
# TODO 5-1：按 RMSE 选出最佳模型
audit_best_name = _____________
# TODO 5-2：保存最佳模型和测试集预测
_____________
''', [
'{"LinearRegression":LinearRegression(),"DecisionTree":DecisionTreeRegressor(max_depth=8,random_state=42),"RandomForest":RandomForestRegressor(n_estimators=180,random_state=42)}',
'result[["model","RMSE","R2"]].sort_values("RMSE")',
'audit_comparison.iloc[0]["model"]',
'(joblib.dump(fitted[audit_best_name],"best_house_model.pkl"),pd.DataFrame({"actual":y_test,"pred":fitted[audit_best_name].predict(X_test)}).to_csv("test_predictions.csv",index=False),audit_comparison.to_csv("model_comparison.csv",index=False))',
]),
"6.2.4": (r'''
# TODO 3-1：使用 StandardScaler + 当前分类器建立 Pipeline
audit_pipe = _____________
# TODO 4-1：整理当前模型 accuracy、recall、F1 和混淆矩阵
audit_metrics = _____________
# TODO 5-1：保存 classifier_comparison.csv
_____________
''', [
'Pipeline([("scaler",StandardScaler()),("model",model)])',
'{"accuracy":accuracy_score(y_test,pred),"recall":recall_score(y_test,pred),"f1":f1_score(y_test,pred),"confusion_matrix":confusion_matrix(y_test,pred).tolist()}',
'result.to_csv("classifier_comparison.csv",index=False)',
]),
"6.2.5": (r'''
# TODO 3-1：整理各聚类算法的簇数、噪声数和轮廓系数
audit_cluster_stats = _____________
# TODO 4-1：使用 PCA 将标准化特征降到二维
audit_pca = _____________
# TODO 4-2：使用 t-SNE 将标准化特征降到二维
audit_tsne = _____________
# TODO 5-1：保存聚类比较、降维结果和当前可视化图
_____________
''', [
'comparison[["model","clusters","silhouette","noise"]].copy()',
'PCA(n_components=2).fit_transform(X)',
'TSNE(n_components=2,random_state=42,perplexity=30,init="pca",learning_rate="auto").fit_transform(X)',
'(comparison.to_csv("cluster_comparison.csv",index=False),out.to_csv("cluster_results.csv",index=False),plt.savefig("pca_tsne.png",dpi=150,bbox_inches="tight"))',
]),
"6.3.1": (r'''
# TODO 3-1：写出两次池化后的全连接输入特征数
audit_feature_dim = _____________
# TODO 4-1：重新定义交叉熵损失
audit_criterion = _____________
# TODO 4-2：重新建立 Adam 优化器
audit_optimizer = _____________
model.eval()
val_correct=0; val_total=0
with torch.no_grad():
    for x,y in val_loader:
        # TODO 5-1：得到验证集类别预测
        audit_pred = _____________
        val_correct += (audit_pred==y).sum().item()
        val_total += len(y)
# TODO 5-2：计算验证准确率
val_accuracy = _____________
# TODO 5-3：保存权重和训练历史
_____________
''', [
'32*16*16',
'nn.CrossEntropyLoss()',
'torch.optim.Adam(model.parameters(),lr=1e-3)',
'model(x).argmax(1)',
'val_correct/max(val_total,1)',
'(torch.save(model.state_dict(),"shape_cnn.pt"),pd.DataFrame(history).to_csv("training_history.csv",index=False))',
]),
"6.3.2": (r'''
# TODO 3-1：确认网络同时包含 BatchNorm2d 和 Dropout
architecture_ok = _____________
history=[]
best_acc=-1.0; best_state=None
for epoch in range(5):
    model.train(); total=correct=0; loss_sum=0.0
    for x,y in train_loader:
        opt.zero_grad()
        # TODO 4-1：前向计算并计算交叉熵损失
        out = _____________
        loss = _____________
        loss.backward(); opt.step()
        loss_sum += loss.item()*len(y); correct += (out.argmax(1)==y).sum().item(); total += len(y)
    model.eval(); val_total=val_correct=0; val_loss_sum=0.0; all_true=[]; all_pred=[]
    with torch.no_grad():
        for x,y in val_loader:
            vout=model(x); vloss=criterion(vout,y)
            val_loss_sum += vloss.item()*len(y); val_correct += (vout.argmax(1)==y).sum().item(); val_total += len(y)
            all_true.extend(y.tolist()); all_pred.extend(vout.argmax(1).tolist())
    row={"epoch":epoch+1,"train_loss":loss_sum/max(total,1),"train_acc":correct/max(total,1),
         "val_loss":val_loss_sum/max(val_total,1),"val_acc":val_correct/max(val_total,1)}
    history.append(row)
    if row["val_acc"]>best_acc:
        best_acc=row["val_acc"]; best_state=copy.deepcopy(model.state_dict())

# TODO 4-2：保存最佳权重
_____________
hist=pd.DataFrame(history)
fig,ax=plt.subplots(1,2,figsize=(10,4))
# TODO 5-1：绘制 loss 与 accuracy 训练曲线
_____________
plt.tight_layout()
# TODO 5-2：保存 training_curve.png
_____________
from sklearn.metrics import confusion_matrix
# TODO 5-3：输出最终验证混淆矩阵
final_confusion = _____________
final_confusion
''', [
'any(isinstance(m,nn.BatchNorm2d) for m in model.modules()) and any(isinstance(m,nn.Dropout) for m in model.modules())',
'model(x)',
'criterion(out,y)',
'torch.save(best_state,"best_flower_cnn.pt")',
'(ax[0].plot(hist.epoch,hist.train_loss,label="train"),ax[0].plot(hist.epoch,hist.val_loss,label="val"),ax[0].legend(),ax[0].set_title("Loss"),ax[1].plot(hist.epoch,hist.train_acc,label="train"),ax[1].plot(hist.epoch,hist.val_acc,label="val"),ax[1].legend(),ax[1].set_title("Accuracy"))',
'plt.savefig("training_curve.png",dpi=150,bbox_inches="tight")',
'confusion_matrix(all_true,all_pred)',
]),
"6.3.3": (r'''
from sklearn.metrics import confusion_matrix

# TODO 3-1：确认 layer4 已解冻
layer4_trainable = _____________
# TODO 3-2：使用当前较小学习率对一个训练批次执行第二阶段微调
x_batch,y_batch=next(iter(train_loader))
opt.zero_grad(); out=model(x_batch); loss=criterion(out,y_batch)
_____________
# TODO 4-1：保存当前模型权重
_____________
# TODO 4-2：重新创建同结构 ResNet18 并加载权重
reloaded = models.resnet18(weights=None)
reloaded.fc = nn.Linear(reloaded.fc.in_features,4)
_____________
reloaded.eval(); model.eval()

def collect_predictions(net):
    ys=[]; ps=[]
    with torch.no_grad():
        for x,y in val_loader:
            ys.extend(y.tolist()); ps.extend(net(x).argmax(1).tolist())
    return ys,ps

true_y,pred_before=collect_predictions(model)
_,pred_after=collect_predictions(reloaded)
# TODO 5-1：计算验证准确率
val_accuracy = _____________
# TODO 5-2：计算验证混淆矩阵
val_confusion = _____________
# TODO 5-3：确认加载前后预测一致
reload_consistent = _____________
''', [
'all(p.requires_grad for p in model.layer4.parameters())',
'(loss.backward(),opt.step())',
'torch.save(model.state_dict(),"best_resnet18.pt")',
'reloaded.load_state_dict(torch.load("best_resnet18.pt",map_location="cpu"))',
'sum(a==b for a,b in zip(true_y,pred_before))/max(len(true_y),1)',
'confusion_matrix(true_y,pred_before)',
'pred_before==pred_after',
]),
"6.3.4": (r'''
# TODO 3-1：完成一次检测损失反向传播与优化更新
audit_train_step = _____________
# TODO 4-1：根据 IoU>=0.5 重新计算 AP50
audit_ap50 = _____________
# TODO 5-1：保存 detection_metrics.json 和 detection_preview.png
_____________
''', [
'float(loss.detach())',
'float((m.iou>=0.5).mean())',
'(open("detection_metrics.json","w",encoding="utf-8").write(json.dumps(metrics,indent=2)),cv2.imwrite("detection_preview.png",vis))',
]),
"6.3.5": (r'''
# TODO 3-1：重新计算预测掩膜与真值的 IoU
audit_iou = _____________
# TODO 4-1：整理 GAN 最终生成器与判别器损失
gan_metrics = _____________
# TODO 5-1：保存分割指标和两类预览图
_____________
''', [
'inter/max(union,1)',
'{"G_loss":float(gl.detach()),"D_loss":float(dl.detach())}',
'(json.dump({"mean_iou":audit_iou,"deeplab_output_shape":deeplab_shape},open("segmentation_metrics.json","w"),indent=2),plt.figure(),plt.imshow(samples[0],cmap="gray"),plt.axis("off"),plt.savefig("gan_samples.png",dpi=150,bbox_inches="tight"))',
]),
"6.4.1": (r'''
from pathlib import Path

# TODO 3-1：生成测试集 classification_report 文本
news_report = _____________
# TODO 4-1：重新整理每个类别权重最高的 10 个关键词
audit_keywords = _____________
# TODO 5-1：保存分类器、评价报告和关键词 JSON
_____________
''', [
'classification_report(y_test,pred)',
'{c:features[model.coef_[i].argsort()[-10:][::-1]].tolist() for i,c in enumerate(model.classes_)}',
'(joblib.dump((vec,model),"news_classifier.pkl"),Path("news_metrics.txt").write_text(news_report,encoding="utf-8"),open("class_keywords.json","w",encoding="utf-8").write(json.dumps(audit_keywords,ensure_ascii=False,indent=2)))',
]),
"6.4.2": (r'''
# TODO 3-1：将首条评论转换为 100 维平均词向量
audit_vector = _____________
# TODO 4-1：计算测试集 F1 与混淆矩阵
audit_eval = _____________
# TODO 5-1：查询“满意”的 Top-5 相似词
audit_similar = _____________
# TODO 5-2：导出预测错误样本 error_cases.csv
error_cases = _____________
_____________
''', [
'sentence_vector(tokens[0])',
'{"f1":f1_score(yte,pred),"confusion_matrix":confusion_matrix(yte,pred).tolist()}',
'w2v.wv.most_similar("满意",topn=5)',
'pd.DataFrame({"y_true":yte,"y_pred":pred})[lambda x:x.y_true!=x.y_pred]',
'error_cases.to_csv("error_cases.csv",index=False)',
]),
"6.4.3": (r'''
# TODO 3-1：重新整理每个主题的 Top-10 关键词
audit_topics = _____________
# TODO 4-1：建立 TF-IDF 特征并计算文章余弦相似度
audit_similarity = _____________
# TODO 5-1：排除自身后找最相似的 5 篇
audit_idx = _____________
# TODO 5-2：保存 topic_result.csv 与 recommendations.json
_____________
''', [
'{str(i):words[comp.argsort()[-10:][::-1]].tolist() for i,comp in enumerate(lda.components_)}',
'cosine_similarity(TfidfVectorizer(max_features=1500).fit_transform(df["cut"]))',
'audit_similarity[target].argsort()[::-1][1:6]',
'(df.to_csv("topic_result.csv",index=False),open("recommendations.json","w",encoding="utf-8").write(json.dumps({"target":int(target),"similar":[int(x) for x in audit_idx]},ensure_ascii=False,indent=2)))',
]),
"6.4.4": (r'''
# TODO 4-1：计算全部翻译结果的平均 BLEU-2
mean_bleu2 = _____________
# TODO 5-1：保存 NER 与翻译结果
_____________
''', [
'float(out.bleu2.mean())',
'(ner.to_csv("ner_results.csv",index=False),out.to_csv("translation_results.csv",index=False))',
]),
"6.4.5": (r'''
# TODO 3-1：使用最长公共子序列函数计算一个示例
audit_lcs = _____________
# TODO 4-1：使用 rouge_l 计算一个示例 ROUGE-L
audit_rouge = _____________
# TODO 5-1：保存生成结果和 ROUGE 汇总报告
_____________
''', [
'lcs(str(df.iloc[0].reference),str(df.iloc[0].reference))',
'rouge_l(str(df.iloc[0].reference),str(df.iloc[0].reference))',
'(out.to_csv("generation_results.csv",index=False),open("rouge_report.json","w",encoding="utf-8").write(json.dumps(report,ensure_ascii=False,indent=2)))',
]),
"6.5.1": (r'''
from pathlib import Path

# TODO 4-1：构造包含现状、问题、原因、建议四部分要求的 Prompt
audit_prompt = _____________
# TODO 5-1：构造 OpenAI 兼容 chat/completions 请求体
api_payload = _____________
# TODO 6-1：保存最终 Markdown 经营报告
_____________
''', [
'f"请根据 GMV={gmv:.2f}、订单数={orders}、客单价={aov:.2f}、复购率={repeat_rate:.2%}，按现状、问题、原因、建议四部分输出 Markdown 报告。"',
'{"model":MODEL,"messages":[{"role":"user","content":audit_prompt}],"temperature":0.2}',
'Path("business_report.md").write_text(report,encoding="utf-8")',
]),
"6.5.2": (r'''
from pathlib import Path

sample_row=df.sort_values("priority_score",ascending=False).iloc[0]
# TODO 4-1：为高优先级投诉构造严格 JSON 输出 Prompt
audit_prompt = _____________
# TODO 5-1：筛选成功解析且包含 result 的 AI 处置记录
valid_actions = _____________
# TODO 6-1：保存投诉结果和 AI 动作 JSON
_____________
''', [
'f"请针对投诉输出严格 JSON，字段 summary/risk/action/reply：{sample_row.text}"',
'[x for x in actions if x.get("error") is None and "result" in x]',
'(df.to_excel("complaint_results.xlsx",index=False),Path("ai_actions.json").write_text(json.dumps(actions,ensure_ascii=False,indent=2),encoding="utf-8"))',
]),
"6.5.3": (r'''
from pathlib import Path

# TODO 4-1：读取评测问题并确认批量问答数量
audit_questions = _____________
# TODO 5-1：计算所有问题的平均关键词覆盖率
mean_keyword_score = _____________
# TODO 6-1：保存 RAG 明细与 Markdown 评测报告
_____________
''', [
'pd.read_csv("questions.csv")',
'float(out.score.mean())',
'(out.to_csv("rag_results.csv",index=False),Path("rag_evaluation.md").write_text(f"# RAG 自动评测\\n\\n平均关键词覆盖率：{mean_keyword_score:.2%}\\n",encoding="utf-8"))',
]),
"6.5.4": (r'''
from pathlib import Path

# TODO 3-1：计算 LoRA 可训练参数比例
audit_trainable_ratio = _____________
# TODO 4-1：整理准确率、参数量和可训练参数比例
audit_metrics = _____________
# TODO 5-1：评测 batch=1/8/32 并保存 benchmark.csv 与 lora_metrics.json
audit_bench = _____________
_____________
''', [
'trainable/total',
'{"accuracy":acc,"trainable_params":trainable,"total_params":total,"trainable_ratio":audit_trainable_ratio}',
'pd.DataFrame([benchmark(1),benchmark(8),benchmark(32)])',
'(audit_bench.to_csv("benchmark.csv",index=False),Path("lora_metrics.json").write_text(json.dumps(audit_metrics,indent=2),encoding="utf-8"))',
]),
"6.5.5": (r'''
# TODO 3-1：计算原型问答准确率
audit_accuracy = _____________
# TODO 4-1：根据总耗时计算查询吞吐量
audit_throughput = _____________
# TODO 5-1：保存 app.py、benchmark.csv 和 evaluation_results.csv，并核对 README/demo 文档存在
_____________
''', [
'float(result.correct.mean())',
'len(result)/(result.latency_ms.sum()/1000)',
'(Path("app.py").write_text(APP,encoding="utf-8"),pd.DataFrame([{"accuracy":audit_accuracy,"avg_latency_ms":result.latency_ms.mean(),"throughput_qps":audit_throughput}]).to_csv("benchmark.csv",index=False),result.to_csv("evaluation_results.csv",index=False),Path("README.md").is_file(),Path("demo_script.md").is_file())',
]),
}


def alignment_code(qid: str) -> str:
    return ALIGNMENT.get(qid, ("", []))[0].strip()


def alignment_answers(qid: str) -> list[str]:
    return list(ALIGNMENT.get(qid, ("", []))[1])
