window.ADVANCED_UNITS=[
{id:'6.1',name:'竞赛强化 A·计算机视觉',count:3},
{id:'6.2',name:'竞赛强化 B·机器学习',count:3},
{id:'6.3',name:'竞赛强化 C·深度学习',count:3},
{id:'6.4',name:'竞赛强化 D·自然语言处理',count:3},
{id:'6.5',name:'竞赛强化 E·AI创新项目',count:3}
];

window.ADVANCED_DETAILS={
'6.1.1':{
 title:'商品图片质量检测与多策略数据增强',
 tags:['OpenCV','PIL','清晰度','亮度','数据增强'],
 taskText:'某电商平台需要扩充商品识别训练集。请批量检测原始商品图片的清晰度与亮度，剔除质量不合格图片，再对合格样本实施水平翻转、旋转和亮度扰动，形成质量可控的增强数据集。',
 req:[
  'TODO 1：遍历 input_images，读取图片并计算 Laplacian 方差作为清晰度指标、灰度均值作为亮度指标',
  'TODO 2：按给定阈值标记“过暗/过亮/模糊/合格”，保存 image_quality.csv',
  'TODO 3：仅对合格图片执行水平翻转、±15°旋转和随机亮度增强，并统一保存为 JPEG',
  'TODO 4：统计原始、合格、增强后的数量以及各类质量问题数量，打印并保存 summary.json',
  'TODO 5：随机抽取 6 张增强结果绘制 2×3 预览图，保存 augmentation_preview.png'
 ]
},
'6.1.2':{
 title:'道路车辆图像预处理与目标区域提取',
 tags:['OpenCV','Canny','形态学','轮廓','ROI'],
 taskText:'为道路车辆检测模型准备输入数据。需要完成统一尺寸、灰度化、降噪、边缘检测、形态学连接、候选轮廓筛选与目标区域裁剪，并输出每张图片的候选区域统计。',
 req:[
  'TODO 1：批量读取 road_images 并统一缩放到 640×360',
  'TODO 2：完成灰度化、GaussianBlur 和 Canny 边缘检测',
  'TODO 3：使用闭运算连接车辆边缘，并通过轮廓面积和宽高比筛选候选区域',
  'TODO 4：在原图绘制候选框，同时裁剪候选 ROI 保存到 roi_output',
  'TODO 5：汇总每张图候选数量和面积占比，保存 detection_summary.csv'
 ]
},
'6.1.3':{
 title:'工业表面缺陷增强、分割与统计',
 tags:['OpenCV','CLAHE','阈值分割','连通域','缺陷检测'],
 taskText:'某工业质检线采集了金属表面灰度图。请增强局部对比度，分割亮斑/暗斑缺陷，利用形态学与连通域去噪，并按缺陷总面积将样本划分为正常、轻微和严重。',
 req:[
  'TODO 1：读取 defect_images，转灰度并使用 CLAHE 增强局部对比度',
  'TODO 2：分别检测过亮与过暗区域，并合并为二值缺陷掩膜',
  'TODO 3：使用开/闭运算去噪，connectedComponentsWithStats 过滤小区域',
  'TODO 4：计算缺陷数量、总面积和面积占比，按阈值给出等级',
  'TODO 5：保存 mask、可视化结果及 defect_report.csv'
 ]
},
'6.2.1':{
 title:'用户画像聚类与最佳 K 自动选择',
 tags:['pandas','ColumnTransformer','KMeans','silhouette_score'],
 taskText:'根据用户消费、活跃度和会员属性构建用户画像。数据包含缺失值、数值特征和类别特征，需要完成预处理，并通过轮廓系数自动选择最佳聚类数。',
 req:[
  'TODO 1：读取 customer_behavior.csv，检查缺失值并区分数值/类别特征',
  'TODO 2：用 ColumnTransformer 完成中位数填补、StandardScaler 和 OneHotEncoder',
  'TODO 3：分别训练 K=2~6 的 KMeans，计算 silhouette_score 并选择最佳 K',
  'TODO 4：将最佳聚类标签写回原表，输出各簇人数和关键数值均值',
  'TODO 5：保存 customer_clusters.csv、k_selection.csv 和最佳模型'
 ]
},
'6.2.2':{
 title:'客户流失随机森林分类与参数调优',
 tags:['RandomForest','GridSearchCV','F1','混淆矩阵','joblib'],
 taskText:'基于电信客户数据预测客户是否流失。要求从清洗、特征预处理、训练测试划分、基础模型评估一直做到网格搜索和最佳模型保存。',
 req:[
  'TODO 1：处理 telecom_churn.csv 的缺失值和类别特征，目标列为 Churn',
  'TODO 2：按 8:2 分层划分训练/测试集，建立预处理+RandomForest Pipeline',
  'TODO 3：输出 accuracy、precision、recall、F1 和 confusion_matrix',
  'TODO 4：使用 GridSearchCV 搜索 n_estimators、max_depth、min_samples_split，以 F1 为评分',
  'TODO 5：保存 best_churn_model.pkl、metrics.json 和 predictions.csv'
 ]
},
'6.2.3':{
 title:'房价回归特征工程与多模型比较',
 tags:['回归','特征工程','RandomForest','GradientBoosting','RMSE','R2'],
 taskText:'根据房屋面积、房龄、区域、学区评分等信息预测成交价。要求构造新特征、比较两种回归模型，并根据 RMSE 自动选择和保存最佳模型。',
 req:[
  'TODO 1：读取 housing.csv，构造 HouseAge 和 AreaPerRoom 两个新特征',
  'TODO 2：完成缺失值处理、类别编码和训练测试划分',
  'TODO 3：训练 RandomForestRegressor 与 GradientBoostingRegressor',
  'TODO 4：分别计算 RMSE 与 R²，生成 model_comparison.csv',
  'TODO 5：按 RMSE 选择最佳模型，保存 best_house_model.pkl 与 test_predictions.csv'
 ]
},
'6.3.1':{
 title:'三类图形 CNN 分类完整训练流程',
 tags:['PyTorch','Dataset','DataLoader','CNN','CrossEntropyLoss'],
 taskText:'使用本地生成的圆形、方形、三角形图片训练三分类 CNN。要求自行完成 Dataset、数据划分、网络结构、训练验证、模型保存和测试评估。',
 req:[
  'TODO 1：实现自定义 Dataset，读取 shape_images 下三类图片并转换 Tensor',
  'TODO 2：按 8:2 划分训练/验证集，构造 DataLoader',
  'TODO 3：搭建两层 Conv-ReLU-MaxPool CNN，并正确计算全连接层输入尺寸',
  'TODO 4：使用 CrossEntropyLoss + Adam 完成训练，记录每轮 loss/accuracy',
  'TODO 5：保存 shape_cnn.pt、training_history.csv，并输出验证准确率'
 ]
},
'6.3.2':{
 title:'四类花卉 CNN：增强、BatchNorm 与 Dropout',
 tags:['PyTorch','torchvision','数据增强','BatchNorm','Dropout'],
 taskText:'在基础 CNN 上加入训练时数据增强、BatchNorm 和 Dropout，完成四类花卉图像分类，并比较训练集与验证集指标以判断过拟合。',
 req:[
  'TODO 1：建立训练/验证不同 transform，训练侧包含翻转、旋转和 ColorJitter',
  'TODO 2：使用 ImageFolder 与 random_split 构造数据加载器',
  'TODO 3：CNN 中加入 BatchNorm2d 和 Dropout',
  'TODO 4：每轮记录 train_loss、train_acc、val_loss、val_acc，并保存最佳权重',
  'TODO 5：绘制训练曲线 training_curve.png，并输出最终验证混淆矩阵'
 ]
},
'6.3.3':{
 title:'ResNet18 骨干冻结、微调与模型复载验证',
 tags:['PyTorch','ResNet18','迁移学习','冻结层','混淆矩阵'],
 taskText:'模拟迁移学习竞赛任务：使用本地四类场景图像和 ResNet18 结构，冻结大部分骨干层，仅训练分类头，再解冻最后一个残差阶段进行微调，最后重新加载模型验证推理一致性。',
 req:[
  'TODO 1：创建 ResNet18(weights=None)，替换 fc 为 4 类输出',
  'TODO 2：冻结 backbone，仅保持 fc 可训练，完成第一阶段训练',
  'TODO 3：解冻 layer4，降低学习率完成第二阶段微调',
  'TODO 4：保存 best_resnet18.pt 并重新创建模型加载权重',
  'TODO 5：在验证集计算准确率与 confusion_matrix，确认加载前后预测一致'
 ]
},
'6.4.1':{
 title:'中文新闻 TF-IDF 分类与关键词解释',
 tags:['jieba','TF-IDF','LogisticRegression','关键词','文本分类'],
 taskText:'对科技、体育、财经、娱乐四类中文新闻进行分词、停用词过滤和 TF-IDF 表示，训练分类器，并输出每个类别最具代表性的关键词。',
 req:[
  'TODO 1：读取 news_train.csv 与 stopwords.txt，使用 jieba 精确分词',
  'TODO 2：使用 TfidfVectorizer 构造文本特征并按 8:2 分层划分',
  'TODO 3：训练 LogisticRegression 并输出 classification_report',
  'TODO 4：根据模型系数提取每个类别权重最高的 10 个关键词',
  'TODO 5：保存 news_classifier.pkl、news_metrics.txt 和 class_keywords.json'
 ]
},
'6.4.2':{
 title:'商品评论 Word2Vec 句向量与情感分类',
 tags:['jieba','Word2Vec','句向量','LogisticRegression','情感分析'],
 taskText:'训练商品评论 Word2Vec 词向量，将每条评论表示为词向量平均值，再训练情感分类器，并完成相似词查询和错误样本分析。',
 req:[
  'TODO 1：对 reviews.csv 评论分词、停用词过滤',
  'TODO 2：训练 Word2Vec(vector_size=100, window=5, min_count=1) 并保存模型',
  'TODO 3：实现 sentence_vector，将一条评论转换为平均词向量',
  'TODO 4：训练 LogisticRegression 情感分类器并输出 F1、混淆矩阵',
  'TODO 5：查询“满意”的 Top-5 相似词，并导出预测错误样本 error_cases.csv'
 ]
},
'6.4.3':{
 title:'新闻 LDA 主题发现与相似文章推荐',
 tags:['CountVectorizer','LDA','主题模型','cosine_similarity'],
 taskText:'在没有人工主题标签的新闻语料上完成主题发现：构建词袋、训练 LDA、解释主题关键词、给每篇文章分配主主题，并基于 TF-IDF 余弦相似度完成相似文章推荐。',
 req:[
  'TODO 1：清洗 corpus_news.csv 并完成中文分词',
  'TODO 2：使用 CountVectorizer + LatentDirichletAllocation(n_components=5) 训练主题模型',
  'TODO 3：输出每个主题 Top-10 关键词，并给每篇文章添加 dominant_topic',
  'TODO 4：另建 TF-IDF 特征并计算 cosine_similarity',
  'TODO 5：为指定文章返回最相似的 5 篇文章，保存 topic_result.csv 与 recommendations.json'
 ]
},
'6.5.1':{
 title:'电商经营数据分析与 AI 经营报告',
 tags:['JSON','pandas','matplotlib','OpenAI兼容接口','Markdown'],
 taskText:'将订单 JSON 清洗为结构化数据，计算 GMV、客单价、复购率和品类表现，绘制图表，并把分析结果组织成 Prompt 调用 OpenAI 兼容接口生成经营诊断报告。',
 req:[
  'TODO 1：读取 orders.json，处理缺失/异常价格与日期，生成 orders_clean.xlsx',
  'TODO 2：计算 GMV、订单数、客单价、复购率以及品类/月份统计',
  'TODO 3：绘制月度 GMV 和品类销售额图表，保存 dashboard.png',
  'TODO 4：构造包含“现状、问题、原因、建议”四部分的 Prompt',
  'TODO 5：实现可配置 BASE_URL/API_KEY/MODEL 的 chat/completions 调用，失败时保留离线分析结果',
  'TODO 6：生成 business_report.md'
 ]
},
'6.5.2':{
 title:'客户投诉分类、优先级预测与 AI 处置建议',
 tags:['文本分类','优先级','OpenAI兼容接口','JSON结构化输出'],
 taskText:'对客户投诉数据进行清洗与分类，训练本地投诉类别模型，结合金额、情绪和关键词生成优先级，再要求大模型以 JSON 输出处置建议。',
 req:[
  'TODO 1：读取 complaints.csv，清洗文本、金额和缺失值',
  'TODO 2：使用 TF-IDF + LogisticRegression 训练投诉类别分类器并评估',
  'TODO 3：依据金额、负面关键词和投诉类别计算 priority_score 与 P1/P2/P3',
  'TODO 4：为高优先级投诉构造 Prompt，要求返回严格 JSON：summary/risk/action/reply',
  'TODO 5：解析并校验 JSON，失败时记录错误而不中断批处理',
  'TODO 6：保存 complaint_results.xlsx 和 ai_actions.json'
 ]
},
'6.5.3':{
 title:'企业知识库检索增强问答与自动评测',
 tags:['RAG','TF-IDF','Top-K','Prompt','自动评测'],
 taskText:'使用本地企业制度文档实现一个轻量级 RAG：切分文档、TF-IDF 建库、Top-K 检索、拼接上下文调用 OpenAI 兼容接口，并利用标准答案关键词进行自动评测。',
 req:[
  'TODO 1：遍历 knowledge_docs/*.txt，按段落切分并记录来源文件',
  'TODO 2：使用 TfidfVectorizer 建立检索矩阵，实现 retrieve(query, top_k=3)',
  'TODO 3：将 Top-K 文本和来源拼接为上下文，Prompt 明确要求“仅依据资料回答并引用来源”',
  'TODO 4：读取 questions.csv 批量问答，记录 answer、sources、latency',
  'TODO 5：根据 expected_keywords 计算关键词覆盖率和平均得分',
  'TODO 6：生成 rag_results.csv 与 rag_evaluation.md'
 ]
}
};
