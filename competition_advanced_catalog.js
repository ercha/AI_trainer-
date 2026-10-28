window.ADVANCED_UNITS=[
{id:'6.1',name:'竞赛强化 A·图像处理技术',count:5},
{id:'6.2',name:'竞赛强化 B·机器学习',count:6},
{id:'6.3',name:'竞赛强化 C·深度学习',count:6},
{id:'6.4',name:'竞赛强化 D·自然语言处理',count:5},
{id:'6.5',name:'竞赛强化 E·AI创新项目',count:5}
];

window.ADVANCED_DETAILS={
'6.1.1':{
 title:'图像基础处理、颜色空间与三种滤波',
 tags:['OpenCV','颜色空间','边界填充','resize','均值/高斯/中值滤波'],
 taskText:'围绕竞赛模块 A 的基础高频 API，完成图像读取、尺寸统一、灰度/HSV 颜色空间转换、边界填充以及均值滤波、高斯滤波、中值滤波，并保存处理结果和对比图。',
 req:[
  'TODO 1：统一缩放到 320×240（OpenCV 参数顺序是宽、高）；BGR 转灰度；BGR 转 HSV',
  'TODO 2：上下 20、左右 30 像素白色常量边框',
  'TODO 3：5×5 均值滤波；对灰度图使用 5×5 高斯滤波，sigmaX=0（由 OpenCV 自动计算）；核大小 5 的中值滤波',
  'TODO 4：将处理结果写入 processed/{stem}_resized.jpg；将处理结果写入 processed/{stem}_gray.jpg；将处理结果写入 processed/{stem}_border.jpg；将处理结果写入 processed/{stem}_mean.jpg；将处理结果写入 processed/{stem}_gaussian.jpg；将处理结果写入 processed/{stem}_median.jpg；输出 basic_processing.csv（index=False，encoding=utf-8-sig）',
  'TODO 5：选取首张输入图像；组织原图、缩放图、灰度图、边框图和三种滤波结果；创建 2×4 子图用于对比预览；显示图像并设置标题；以 150 dpi 将对比预览保存为 filter_comparison.png（bbox_inches=tight）'
 ]
},
'6.1.2':{
 title:'道路车辆边缘、阈值、轮廓与目标区域提取',
 tags:['OpenCV','Canny','Otsu','轮廓','ROI'],
 taskText:'为道路车辆检测准备输入数据。完成统一尺寸、灰度化、高斯去噪、Otsu 阈值分割、Canny 边缘检测、形态学连接、轮廓筛选与目标区域裁剪，并输出候选区域统计。',
 req:[
  'TODO 1：统一尺寸为 640×360；对灰度图使用 5×5 高斯滤波（sigmaX=0）；Otsu 自动阈值二值化；Canny(50,150)',
  'TODO 2：用已有 9×5 矩形核做闭运算，iterations=2，以连接边缘',
  'TODO 3：从闭运算结果重新提取外轮廓；筛选矩形面积 w*h≥1200 且宽高比 1.2～5.0 的候选框',
  'TODO 4：将二值图、边缘图和绘框图按原文件名分别保存到 binary/、edges/、visualized/',
  'TODO 5：由 records 构造汇总表；保存 detection_summary.csv'
 ]
},
'6.1.3':{
 title:'工业表面缺陷增强、分割与统计',
 tags:['OpenCV','CLAHE','阈值分割','连通域','缺陷检测'],
 taskText:'某工业质检线采集了金属表面灰度图。请增强局部对比度，分割亮斑/暗斑缺陷，利用形态学与连通域去噪，并按缺陷总面积将样本划分为正常、轻微和严重。',
 req:[
  'TODO 1：CLAHE 增强；检测亮缺陷 >180；检测暗缺陷 <70；对 3×3 核先做开运算，再做闭运算（iterations=2）',
  'TODO 2：合并亮缺陷与暗缺陷掩膜',
  'TODO 3：对过滤后的缺陷掩膜执行连通域统计',
  'TODO 4：按缺陷面积占比重新分级：<0.002 为正常，0.002～<0.01 为轻微，其余为严重',
  'TODO 5：构造缺陷统计表；保存 masks/ 掩膜、defect_vis/ 可视化图（原文件名），导出 defect_report.csv（index=False，utf-8-sig）'
 ]
},
'6.2.1':{
 title:'用户画像聚类与最佳 K 自动选择',
 tags:['pandas','ColumnTransformer','KMeans','silhouette_score'],
 taskText:'根据用户消费、活跃度和会员属性构建用户画像。数据包含缺失值、数值特征和类别特征，需要完成预处理，并通过轮廓系数自动选择最佳聚类数。',
 req:[
  'TODO 1：在数值 Pipeline 中使用 SimpleImputer(strategy=median) 和 StandardScaler()；在类别 Pipeline 中使用 SimpleImputer(strategy=most_frequent) 和 OneHotEncoder(handle_unknown=ignore)',
  'TODO 2：计算轮廓系数；使用最佳簇数 best_k，random_state=42、n_init=10 训练 KMeans',
  'TODO 3：根据轮廓系数重新取得最佳 K',
  'TODO 4：统计各聚类的样本数和数值特征均值',
  'TODO 5：导出 customer_clusters.csv、k_selection.csv（均 index=False），并用 joblib 保存 best_cluster_model.pkl（预处理器与 KMeans）'
 ]
},
'6.2.2':{
 title:'客户流失随机森林分类与参数调优',
 tags:['RandomForest','GridSearchCV','F1','混淆矩阵','joblib'],
 taskText:'基于电信客户数据预测客户是否流失。要求从清洗、特征预处理、训练测试划分、基础模型评估一直做到网格搜索和最佳模型保存。',
 req:[
  'TODO 1：使用 train_test_split 按 8:2 分层划分，random_state=42，stratify=y',
  'TODO 2：计算 accuracy、precision、recall、f1，precision/recall/f1 的 zero_division=0；根据给定 grid 创建 GridSearchCV（scoring=f1，cv=4，n_jobs=-1）',
  'TODO 3：使用 search.predict(X_test) 预测，并计算 accuracy、precision、recall、f1（零除时得 0）',
  'TODO 4：复用题目 grid，按 scoring=f1、cv=4、n_jobs=-1 建立 GridSearchCV',
  'TODO 5：保存 best_churn_model.pkl、predictions.csv（y_true/y_pred，不写索引）和 metrics.json（accuracy/precision/recall/f1）'
 ]
},
'6.2.3':{
 title:'房价线性回归、决策树与随机森林对比',
 tags:['LinearRegression','DecisionTree','RandomForest','RMSE','R2'],
 taskText:'根据房屋面积、房龄、区域、学区评分等信息预测成交价。要求构造新特征，对比线性回归、决策树回归和随机森林回归，并根据 RMSE 自动选择最佳模型。',
 req:[
  'TODO 1：以 2026 年为计算基准，根据 BuildYear 构造 HouseAge；使用 Area/Rooms 构造 AreaPerRoom',
  'TODO 2：依据 y_test 与 pred 计算均方误差并开平方得到 RMSE；计算 R²',
  'TODO 3：构造 LinearRegression、DecisionTreeRegressor(max_depth=8,random_state=42)、RandomForestRegressor(n_estimators=180,random_state=42) 的模型字典',
  'TODO 4：整理 RMSE 与 R² 对比结果',
  'TODO 5：按 RMSE 选出最佳模型；保存 best_house_model.pkl、test_predictions.csv（actual/pred），同时输出 model_comparison.csv（不写索引）'
 ]
},
'6.3.1':{
 title:'三类图形 CNN 分类完整训练流程',
 tags:['PyTorch','Dataset','DataLoader','CNN','CrossEntropyLoss'],
 taskText:'使用本地生成的圆形、方形、三角形图片训练三分类 CNN。要求自行完成 Dataset、数据划分、网络结构、训练验证、模型保存和测试评估。',
 req:[
  'TODO 1：使用 ImageFolder 读取 shape_images；按 8:2 划分训练/验证集，使用 torch.Generator().manual_seed(42) 固定划分',
  'TODO 2：网络输出 32 通道、空间尺寸 16×16，建立 nn.Linear(32*16*16,3)；定义 nn.CrossEntropyLoss()，以及学习率 lr=1e-3 的 Adam 优化器',
  'TODO 3：卷积层输出 32 个通道、64×64 两次池化后为 16×16，写出 32*16*16',
  'TODO 4：重新定义交叉熵损失；使用 model.parameters() 和 lr=1e-3 重新建立 Adam 优化器',
  'TODO 5：得到验证集类别预测；计算验证准确率；保存 shape_cnn.pt 模型权重与 training_history.csv 训练历史（不写索引）'
 ]
},
'6.3.2':{
 title:'四类花卉 CNN：增强、BatchNorm 与 Dropout',
 tags:['PyTorch','torchvision','数据增强','BatchNorm','Dropout'],
 taskText:'在基础 CNN 上加入训练时数据增强、BatchNorm 和 Dropout，完成四类花卉图像分类，并比较训练集与验证集指标以判断过拟合。',
 req:[
  'TODO 1：依次使用 RandomHorizontalFlip(p=0.5)、RandomRotation(15)、ColorJitter(brightness=0.2, contrast=0.2)、ToTensor()',
  'TODO 2：在 24 通道卷积层后加入 nn.BatchNorm2d(24)；加入 Dropout(0.4)',
  'TODO 3：确认网络同时包含 BatchNorm2d 和 Dropout',
  'TODO 4：用 model(x) 获得四类 logits，再用 criterion(out, y) 计算交叉熵损失；将验证准确率最高时保存的 best_state 写入 best_flower_cnn.pt',
  'TODO 5：左图绘制 train_loss/val_loss，右图绘制 train_acc/val_acc；两图均添加图例和标题；以 150 dpi 保存 training_curve.png，bbox_inches="tight"；用最后一轮收集的 all_true 与 all_pred 计算验证集混淆矩阵'
 ]
},
'6.3.3':{
 title:'ResNet18 骨干冻结、微调与模型复载验证',
 tags:['PyTorch','ResNet18','迁移学习','冻结层','混淆矩阵'],
 taskText:'模拟迁移学习竞赛任务：使用本地四类场景图像和 ResNet18 结构，冻结大部分骨干层，仅训练分类头，再解冻最后一个残差阶段进行微调，最后重新加载模型验证推理一致性。',
 req:[
  'TODO 1：使用 models.resnet18(weights=None) 创建离线 ResNet18；冻结所有参数；替换 fc 为 4 类输出，并保持可训练',
  'TODO 2：解冻 layer4；使用 Adam 仅优化 requires_grad=True 的 layer4 + fc，学习率 lr=1e-4',
  'TODO 3：确认 layer4 已解冻；使用当前较小学习率对一个训练批次执行第二阶段微调',
  'TODO 4：使用 torch.save(model.state_dict()) 将当前权重保存为 best_resnet18.pt；使用 weights=None 重新创建同结构 ResNet18，将 fc 改为 4 类，加载 best_resnet18.pt（map_location=cpu）',
  'TODO 5：计算验证准确率；计算验证混淆矩阵；确认加载前后预测一致'
 ]
},
'6.4.1':{
 title:'中文新闻 TF-IDF 分类与关键词解释',
 tags:['jieba','TF-IDF','LogisticRegression','关键词','文本分类'],
 taskText:'对科技、体育、财经、娱乐四类中文新闻进行分词、停用词过滤和 TF-IDF 表示，训练分类器，并输出每个类别最具代表性的关键词。',
 req:[
  'TODO 1：jieba 精确分词并过滤停用词；TF-IDF，最大 2000 特征，1-2 gram',
  'TODO 2：创建 LogisticRegression(max_iter=1000) 并训练；取该类别系数最大的 10 个词',
  'TODO 3：生成测试集 classification_report 文本',
  'TODO 4：重新整理每个类别权重最高的 10 个关键词',
  'TODO 5：保存 news_classifier.pkl、news_metrics.txt（UTF-8）、class_keywords.json（UTF-8，保留中文）'
 ]
},
'6.4.2':{
 title:'商品评论 Word2Vec 句向量与情感分类',
 tags:['jieba','Word2Vec','句向量','LogisticRegression','情感分析'],
 taskText:'训练商品评论 Word2Vec 词向量，将每条评论表示为词向量平均值，再训练情感分类器，并完成相似词查询和错误样本分析。',
 req:[
  'TODO 1：完成分词并过滤停用词；使用 Word2Vec：vector_size=100、window=5、min_count=1、workers=2、seed=42',
  'TODO 2：返回平均词向量；无有效词返回全零；查询“满意”最相似的 5 个词',
  'TODO 3：将首条评论转换为 100 维平均词向量',
  'TODO 4：计算测试集 F1 与混淆矩阵',
  'TODO 5：查询“满意”的 Top-5 相似词；导出预测错误样本 error_cases.csv'
 ]
},
'6.4.3':{
 title:'新闻 LDA 主题发现与相似文章推荐',
 tags:['CountVectorizer','LDA','主题模型','cosine_similarity'],
 taskText:'在没有人工主题标签的新闻语料上完成主题发现：构建词袋、训练 LDA、解释主题关键词、给每篇文章分配主主题，并基于 TF-IDF 余弦相似度完成相似文章推荐。',
 req:[
  'TODO 1：构建 CountVectorizer，max_features=1500；训练 LatentDirichletAllocation(n_components=5,random_state=42)',
  'TODO 2：每主题 Top-10 关键词；排除自身，找最相似 5 篇',
  'TODO 3：重新整理每个主题的 Top-10 关键词',
  'TODO 4：用 TfidfVectorizer(max_features=1500) 建立文本特征，再计算文章间余弦相似度矩阵',
  'TODO 5：排除自身后找最相似的 5 篇；保存 topic_result.csv 与 recommendations.json'
 ]
},
'6.5.1':{
 title:'电商经营数据分析与 AI 经营报告',
 tags:['JSON','pandas','matplotlib','OpenAI兼容接口','Markdown'],
 taskText:'将订单 JSON 清洗为结构化数据，计算 GMV、客单价、复购率和品类表现，绘制图表，并把分析结果组织成 Prompt 调用 OpenAI 兼容接口生成经营诊断报告。',
 req:[
  'TODO 1：日期转 datetime；计算 sales=price*qty',
  'TODO 2：计算客单价；计算复购率（订单数>1客户占比）',
  'TODO 3：从 OPENAI_BASE_URL、OPENAI_API_KEY、OPENAI_MODEL 读取 BASE_URL、API_KEY、MODEL（缺省空字符串）；用 requests.post 调用 BASE_URL/v1/chat/completions，使用 Bearer Key、MODEL、prompt、temperature=0.2，timeout=60',
  'TODO 4：构造包含现状、问题、原因、建议四部分要求的 Prompt',
  'TODO 5：使用 MODEL、user 消息 audit_prompt、temperature=0.2 构造 OpenAI 兼容 chat/completions 请求体',
  'TODO 6：将最终经营报告按 UTF-8 编码保存为 business_report.md'
 ]
},
'6.5.2':{
 title:'客户投诉分类、优先级预测与 AI 处置建议',
 tags:['文本分类','优先级','OpenAI兼容接口','JSON结构化输出'],
 taskText:'对客户投诉数据进行清洗与分类，训练本地投诉类别模型，结合金额、情绪和关键词生成优先级，再要求大模型以 JSON 输出处置建议。',
 req:[
  'TODO 1：创建 TF-IDF(max_features=2000) + LogisticRegression(max_iter=1000) 的 Pipeline',
  'TODO 2：金额>2000、包含任一负面词、预测类别为退款或质量各记 1 分，相加为 priority_score',
  'TODO 3：请求 /v1/chat/completions：Bearer Key，response_format=json_object，timeout=60；提取 message.content 作为 JSON 文本',
  'TODO 4：针对高优先级投诉创建要求返回 summary、risk、action、reply 四字段的严格 JSON Prompt',
  'TODO 5：筛选成功解析且包含 result 的 AI 处置记录',
  'TODO 6：保存 complaint_results.xlsx（不写索引）和 ai_actions.json（UTF-8，保留中文）'
 ]
},
'6.5.3':{
 title:'企业知识库检索增强问答与自动评测',
 tags:['RAG','TF-IDF','Top-K','Prompt','自动评测'],
 taskText:'使用本地企业制度文档实现一个轻量级 RAG：切分文档、TF-IDF 建库、Top-K 检索、拼接上下文调用 OpenAI 兼容接口，并利用标准答案关键词进行自动评测。',
 req:[
  'TODO 1：使用 TfidfVectorizer(analyzer=char,ngram_range=(2,4)) 建立中文字符级 TF-IDF 检索库；取相似度最高的 top_k',
  'TODO 2：向 BASE/v1/chat/completions 发送 Bearer Key、MODEL、user prompt，temperature=0.1、timeout=60',
  'TODO 3：按 expected_keywords 中逗号分隔的关键词计算覆盖率（命中数 / 关键词总数）',
  'TODO 4：用 pd.read_csv 读取 questions.csv，核对批量评测问题数量',
  'TODO 5：计算所有问题的平均关键词覆盖率',
  'TODO 6：保存 rag_results.csv（不写索引）与 rag_evaluation.md（UTF-8，含平均关键词覆盖率）'
 ]
},
'6.1.4':{
 title:'HSV 颜色目标提取与形态学检测',
 tags:['HSV','inRange','形态学','轮廓'],
 taskText:'使用 HSV 颜色空间提取红色目标，完成掩膜去噪、轮廓检测、目标框绘制与数量统计。',
 req:[
  'TODO 1：BGR 转 HSV；提取低色相红色区域；提取高色相红色区域并合并',
  'TODO 2：先开运算去噪，再闭运算连接',
  'TODO 3：从清理后的红色掩膜提取外轮廓；筛选面积不少于 500 的红色目标轮廓',
  'TODO 4：分别按原文件名写入 masks/ 红色掩膜和 visualized/ 绘框图',
  'TODO 5：构造颜色检测统计表；保存 color_detection.csv'
 ]
},
'6.1.5':{
 title:'OpenCV 模板匹配目标检测',
 tags:['matchTemplate','minMaxLoc','目标检测'],
 taskText:'使用模板匹配在复杂背景中定位指定目标，输出匹配分数、目标框与定位误差。',
 req:[
  'TODO 1：使用 TM_CCOEFF_NORMED 做模板匹配；取得最大匹配分数和位置',
  'TODO 2：使用 TM_CCOEFF_NORMED 重新计算模板匹配结果',
  'TODO 3：取得最大匹配分数和位置',
  'TODO 4：复制当前场景图用于绘框；以绿色线宽 2 绘制模板匹配框，并按原文件名保存到检测输出目录 OUT',
  'TODO 5：合并预测与 ground_truth；计算中心点定位误差；保存 template_detection.csv'
 ]
},
'6.2.4':{
 title:'逻辑回归、SVM 与 KNN 分类器对比',
 tags:['LogisticRegression','SVC','KNN','Accuracy','Recall','F1'],
 taskText:'对同一二分类数据完成标准化、训练、预测，并用准确率、召回率、F1 和混淆矩阵比较三种分类器。',
 req:[
  'TODO 1：建立逻辑回归、SVM、KNN 三个分类器',
  'TODO 2：准确率；召回率；F1',
  'TODO 3：使用 StandardScaler + 当前分类器建立 Pipeline',
  'TODO 4：整理当前模型 accuracy、recall、F1 和混淆矩阵',
  'TODO 5：保存 classifier_comparison.csv'
 ]
},
'6.2.5':{
 title:'多聚类算法与 PCA/t-SNE 可视化',
 tags:['KMeans','Agglomerative','DBSCAN','GMM','PCA','t-SNE'],
 taskText:'比较 K-Means、层次聚类、DBSCAN、高斯混合模型，并使用 PCA 与 t-SNE 对高维样本进行二维可视化。',
 req:[
  'TODO 1：标准化；建立四种聚类算法',
  'TODO 2：PCA 降到二维；t-SNE 降到二维',
  'TODO 3：整理各聚类算法的簇数、噪声数和轮廓系数',
  'TODO 4：使用 PCA 将标准化特征降到二维；使用 TSNE(n_components=2, random_state=42, perplexity=30, init=pca, learning_rate=auto) 将标准化特征降到二维',
  'TODO 5：保存 cluster_comparison.csv、cluster_results.csv（均不写索引）及 pca_tsne.png（150 dpi）'
 ]
},
'6.3.4':{
 title:'YOLO 标注、Faster R-CNN 目标检测与 AP50',
 tags:['YOLO','Faster R-CNN','IoU','AP50','torchvision'],
 taskText:'掌握 YOLO 归一化标注与 xyxy 转换，并使用 torchvision Faster R-CNN 完成检测模型构建、训练更新、IoU、AP50 和可视化。',
 req:[
  'TODO 1：将 YOLO 归一化 cx,cy,w,h 转为像素 xyxy；创建不下载预训练权重的 Faster R-CNN，两类（背景+目标）；SGD 优化器；合计检测损失',
  'TODO 2：交集面积',
  'TODO 3：完成一次检测损失反向传播与优化更新',
  'TODO 4：按 IoU≥0.5 的样本命中比例计算题目中的简化 AP50（非严格检测 AP）',
  'TODO 5：保存 detection_metrics.json 和 detection_preview.png'
 ]
},
'6.3.5':{
 title:'U-Net/DeepLab 语义分割与轻量 GAN 图像生成',
 tags:['U-Net','DeepLab','语义分割','IoU','GAN'],
 taskText:'在本地合成数据上完成 U-Net 跳跃连接与 IoU 评估，掌握 DeepLabV3 离线调用，并训练轻量 GAN 生成掩膜样本。',
 req:[
  'TODO 1：2 倍上采样 32→16；跳跃连接；二值分割损失；创建不下载权重的 DeepLabV3（二分类）',
  'TODO 2：GAN 二分类损失',
  'TODO 3：重新计算预测掩膜与真值的 IoU',
  'TODO 4：整理 GAN 最终生成器与判别器损失',
  'TODO 5：将 mean_iou、deeplab_output_shape 保存到 segmentation_metrics.json，并保存 GAN 样本预览 gan_samples.png（150 dpi）'
 ]
},
'6.4.4':{
 title:'命名实体识别与 Transformer 翻译/BLEU',
 tags:['NER','jieba','Transformer','BLEU'],
 taskText:'使用 jieba 词性完成中文实体提取，并构建 encoder-decoder Transformer，通过 teacher forcing 训练、greedy decoding 完成中英短句翻译与 BLEU-2 评估。',
 req:[
  'TODO 1：jieba 词性标注',
  'TODO 2：创建 encoder-decoder Transformer，4 个注意力头；交叉熵损失，忽略 PAD',
  'TODO 3：计算 BLEU-2',
  'TODO 4：计算全部翻译结果的平均 BLEU-2',
  'TODO 5：将命名实体识别结果保存为 ner_results.csv，将翻译和 BLEU 指标保存为 translation_results.csv（均不写索引）'
 ]
},
'6.4.5':{
 title:'GPT 文本摘要、对话/诗歌生成与 ROUGE',
 tags:['GPT','OpenAI兼容接口','摘要','对话','ROUGE'],
 taskText:'调用 OpenAI 兼容 GPT 接口完成摘要、对话回复和诗歌生成，并实现 ROUGE-L 自动评价；未配置 API 时保留离线基线。',
 req:[
  'TODO 1：调用 OpenAI 兼容 chat/completions；提取生成文本',
  'TODO 2：ROUGE-L F1',
  'TODO 3：使用最长公共子序列函数计算一个示例',
  'TODO 4：使用 rouge_l 计算一个示例 ROUGE-L',
  'TODO 5：保存 generation_results.csv（不写索引）和 rouge_report.json（UTF-8，保留中文）'
 ]
},
'6.5.4':{
 title:'LoRA/PEFT 微调与推理性能评测',
 tags:['Transformers','LoRA','PEFT','Latency','Throughput'],
 taskText:'使用本地随机初始化的小型 BERT 完成 LoRA/PEFT 参数高效微调，统计可训练参数比例、准确率、延迟与吞吐量，全程无需下载模型。',
 req:[
  'TODO 1：LoRA 配置，分类任务，r=4，作用于 query/value；包装为 PEFT 模型',
  'TODO 2：吞吐量 samples/s',
  'TODO 3：计算 LoRA 可训练参数比例',
  'TODO 4：整理准确率、参数量和可训练参数比例',
  'TODO 5：评测 batch=1/8/32 并保存 benchmark.csv 与 lora_metrics.json'
 ]
},
'6.5.5':{
 title:'智慧校园 AI 原型：需求、检索、界面、性能与交付',
 tags:['工程化','RAG','Tkinter','测试','文档'],
 taskText:'完成一个可复现的智慧校园制度问答原型：本地知识检索、自动评测、响应时间/吞吐量统计、Tkinter 界面和 README 交付文档。',
 req:[
  'TODO 1：建立 TF-IDF 检索矩阵；按相似度取 Top-K',
  'TODO 2：每秒可处理查询数',
  'TODO 3：计算原型问答准确率',
  'TODO 4：根据总耗时计算查询吞吐量',
  'TODO 5：保存 app.py、benchmark.csv 和 evaluation_results.csv，并核对 README/demo 文档存在'
 ]
},
'6.2.6':{
 title:'合成人像二分类、预测概率与 Matplotlib 标注',
 tags:['SVC','predict_proba','图像分类','概率','matplotlib'],
 taskText:'使用本地生成的合成人像完成二分类训练与概率预测。重点练习图像读取/缩放/展平、SVC(probability=True)、predict_proba，以及在结果图标题中写出预测类别和概率。',
 req:[
  'TODO 1：统一缩放到 32×32；转为 0~1 的一维特征',
  'TODO 2：按 3:1 分层划分训练/测试索引',
  'TODO 3：训练 SVC 概率分类模型',
  'TODO 4：按训练时相同方式构造待预测特征；预测类别；取得预测类别的最大概率',
  'TODO 5：创建 Matplotlib 画布；标题写出预测类别和概率；保存预测结果图'
 ]
},
'6.3.6':{
 title:'合成人像年龄段/性别多任务 CNN 与概率可视化',
 tags:['PyTorch','CNN','多任务学习','Softmax','概率可视化'],
 taskText:'使用本地生成的合成人像训练双输出 CNN，同时预测性别标签与年龄段标签，并把女性合成人像、两项预测结果及各自概率显示在 Matplotlib 标题中。',
 req:[
  'TODO 1：将 gender 字符串映射为类别编号；将 age 字符串映射为类别编号',
  'TODO 2：固定随机种子完成 8:2 划分；建立 batch_size=16 的训练 DataLoader',
  'TODO 3：分别输出性别 logits 和年龄段 logits；两个分类损失相加作为总损失',
  'TODO 4：Softmax 得到两个任务的概率；取得预测类别编号',
  'TODO 5：标题同时写出性别、年龄段及两项概率；保存最终预测可视化'
 ]
}
};

const REAL_EXAM_INPUTS={
'6.1.1':'input_images/*.jpg','6.1.2':'road_images/*.jpg','6.1.3':'defect_images/*.png','6.1.4':'color_images/*.jpg','6.1.5':'ground_truth.csv',
'6.2.1':'customer_behavior.csv','6.2.2':'telecom_churn.csv','6.2.3':'housing.csv','6.2.4':'classification.csv','6.2.5':'cluster_features.csv','6.2.6':'portrait_images/',
'6.3.1':'shape_images/','6.3.2':'flower_images/','6.3.3':'scene_images/','6.3.4':'annotations.csv','6.3.5':'seg_images/*.png','6.3.6':'face_attributes/',
'6.4.1':'news_train.csv','6.4.2':'reviews.csv','6.4.3':'corpus_news.csv','6.4.4':'translation_pairs.csv','6.4.5':'generation_tasks.csv',
'6.5.1':'orders.json','6.5.2':'complaints.csv','6.5.3':'questions.csv','6.5.4':'lora_train.npz','6.5.5':'eval_questions.csv'
};
const REAL_EXAM_PLOTS={
'6.1.1':'basic_processing_chart.png','6.1.2':'detection_summary_chart.png','6.1.3':'defect_area_chart.png','6.1.4':'red_object_chart.png','6.1.5':'template_error_chart.png',
'6.2.1':'k_selection_chart.png','6.2.2':'churn_metrics_chart.png','6.2.3':'house_model_chart.png','6.2.4':'classifier_f1_chart.png','6.2.5':'cluster_score_chart.png','6.2.6':'portrait_confidence_chart.png',
'6.3.1':'cnn_loss_chart.png','6.3.2':'flower_split_chart.png','6.3.3':'scene_split_chart.png','6.3.4':'detection_metrics_chart.png','6.3.5':'segmentation_iou_chart.png','6.3.6':'face_multitask_confidence_chart.png',
'6.4.1':'news_class_chart.png','6.4.2':'review_label_chart.png','6.4.3':'topic_distribution_chart.png','6.4.4':'bleu_chart.png','6.4.5':'rouge_chart.png',
'6.5.1':'order_category_chart.png','6.5.2':'complaint_priority_chart.png','6.5.3':'rag_score_chart.png','6.5.4':'lora_throughput_chart.png','6.5.5':'prototype_eval_chart.png'
};
const FINAL_TODO_GROUPS={'6.5.1':7,'6.5.2':7,'6.5.3':7};
const MODULE_DATA_RULE={
'1':'图像任务需先枚举输入文件，使用 OpenCV/PIL 实际读取样本，检查数量、尺寸、通道和 dtype；处理后既要保存中间图像，也要用 matplotlib 展示关键处理结果。',
'2':'机器学习任务需从原始表格开始，检查 shape、字段类型、缺失值和类别分布；再完成填补/编码/标准化、数据划分、建模、评价、模型或预测结果保存。',
'3':'深度学习任务需检查数据集类别与样本量，明确训练/验证划分；训练过程或关键评价结果必须用 matplotlib 展示，并保存权重、指标或图像结果。',
'4':'NLP 任务需从语料读取开始，检查文本、标签和缺失值；完成清洗/分词/向量化、建模评价，并用 matplotlib 展示类别、主题或评价指标。',
'5':'AI 项目任务需覆盖多格式数据读取、清洗、指标计算、接口/检索/模型流程、matplotlib 业务可视化及 CSV/Excel/JSON/Markdown 等交付文件。'
};
Object.entries(window.ADVANCED_DETAILS).forEach(([qid,item])=>{
  const module=qid.split('.')[1];
  item.tags=[...new Set([...item.tags,'数据读取','数据预处理','matplotlib','结果保存'])];
  item.taskText += ' 本题按真实竞赛任务链训练，不能只补模型 API，还必须完成输入核验、数据质量检查、结果可视化与交付文件验证。';
  const finalTodo=FINAL_TODO_GROUPS[qid]||6;
  item.req=[
    `TODO 0：从 ${REAL_EXAM_INPUTS[qid]} 独立读取原始输入，检查数据/文件数量、shape、字段类型或 dtype，并完成数据质量核验，保存 data_quality_check.csv`,
    MODULE_DATA_RULE[module],
    ...item.req,
    `TODO ${finalTodo}：使用 matplotlib 对本题关键结果进行可视化，设置标题、坐标轴标签和必要刻度，保存为 ${REAL_EXAM_PLOTS[qid]}，提交前检查关键输出文件`
  ];
});

