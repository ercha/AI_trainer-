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
  'TODO 1：批量读取 input_images，统一缩放到 320×240，并完成 BGR→GRAY、BGR→HSV 转换',
  'TODO 2：使用 copyMakeBorder 为缩放图像增加上下 20、左右 30 像素的白色常量边框',
  'TODO 3：分别使用 5×5 均值滤波、5×5 高斯滤波和核大小 5 的中值滤波处理灰度图',
  'TODO 4：将缩放图、灰度图、边框图及三种滤波结果保存到 processed，并输出 basic_processing.csv',
  'TODO 5：选取首张图生成原图、缩放图、灰度图、边框图和三种滤波结果对比预览，保存 filter_comparison.png'
 ]
},
'6.1.2':{
 title:'道路车辆边缘、阈值、轮廓与目标区域提取',
 tags:['OpenCV','Canny','Otsu','轮廓','ROI'],
 taskText:'为道路车辆检测准备输入数据。完成统一尺寸、灰度化、高斯去噪、Otsu 阈值分割、Canny 边缘检测、形态学连接、轮廓筛选与目标区域裁剪，并输出候选区域统计。',
 req:[
  'TODO 1：批量读取 road_images 并统一缩放到 640×360，转换为灰度图',
  'TODO 2：完成 5×5 GaussianBlur、Otsu 二值化和 Canny(50,150) 边缘检测',
  'TODO 3：使用闭运算连接边缘，并通过 findContours、boundingRect、面积和宽高比筛选候选区域',
  'TODO 4：保存 binary/edges 中间结果，在原图绘制候选框并裁剪 ROI 保存到 roi_output',
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
 title:'房价线性回归、决策树与随机森林对比',
 tags:['LinearRegression','DecisionTree','RandomForest','RMSE','R2'],
 taskText:'根据房屋面积、房龄、区域、学区评分等信息预测成交价。要求构造新特征，对比线性回归、决策树回归和随机森林回归，并根据 RMSE 自动选择最佳模型。',
 req:[
  'TODO 1：读取 housing.csv，构造 HouseAge 和 AreaPerRoom 两个新特征',
  'TODO 2：完成缺失值处理、类别编码和训练测试划分',
  'TODO 3：训练 LinearRegression、DecisionTreeRegressor 与 RandomForestRegressor',
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
},
'6.1.4':{
 title:'HSV 颜色目标提取与形态学检测',
 tags:['HSV','inRange','形态学','轮廓'],
 taskText:'使用 HSV 颜色空间提取红色目标，完成掩膜去噪、轮廓检测、目标框绘制与数量统计。',
 req:[
  'TODO 1：BGR 转 HSV，并用两段红色色相范围生成掩膜',
  'TODO 2：使用开运算去噪、闭运算连接目标',
  'TODO 3：findContours 后按面积过滤并绘制目标框',
  'TODO 4：保存红色掩膜和可视化结果',
  'TODO 5：输出 color_detection.csv'
 ]
},
'6.1.5':{
 title:'OpenCV 模板匹配目标检测',
 tags:['matchTemplate','minMaxLoc','目标检测'],
 taskText:'使用模板匹配在复杂背景中定位指定目标，输出匹配分数、目标框与定位误差。',
 req:[
  'TODO 1：读取灰度模板与场景图片',
  'TODO 2：使用 TM_CCOEFF_NORMED 做 matchTemplate',
  'TODO 3：使用 minMaxLoc 得到最大匹配位置',
  'TODO 4：绘制检测框并保存可视化结果',
  'TODO 5：输出 template_detection.csv 并计算定位误差'
 ]
},
'6.2.4':{
 title:'逻辑回归、SVM 与 KNN 分类器对比',
 tags:['LogisticRegression','SVC','KNN','Accuracy','Recall','F1'],
 taskText:'对同一二分类数据完成标准化、训练、预测，并用准确率、召回率、F1 和混淆矩阵比较三种分类器。',
 req:[
  'TODO 1：按 8:2 分层划分训练/测试集',
  'TODO 2：建立 LogisticRegression、SVC、KNeighborsClassifier',
  'TODO 3：使用 StandardScaler + Pipeline 训练',
  'TODO 4：计算 accuracy、recall、F1 和 confusion_matrix',
  'TODO 5：保存 classifier_comparison.csv'
 ]
},
'6.2.5':{
 title:'多聚类算法与 PCA/t-SNE 可视化',
 tags:['KMeans','Agglomerative','DBSCAN','GMM','PCA','t-SNE'],
 taskText:'比较 K-Means、层次聚类、DBSCAN、高斯混合模型，并使用 PCA 与 t-SNE 对高维样本进行二维可视化。',
 req:[
  'TODO 1：标准化四维聚类特征',
  'TODO 2：训练 KMeans、AgglomerativeClustering、DBSCAN、GaussianMixture',
  'TODO 3：计算各算法簇数、噪声数和可用的 silhouette_score',
  'TODO 4：使用 PCA 与 t-SNE 降到二维',
  'TODO 5：保存 cluster_comparison.csv、cluster_results.csv 和 pca_tsne.png'
 ]
},
'6.3.4':{
 title:'YOLO 标注、Faster R-CNN 目标检测与 AP50',
 tags:['YOLO','Faster R-CNN','IoU','AP50','torchvision'],
 taskText:'掌握 YOLO 归一化标注与 xyxy 转换，并使用 torchvision Faster R-CNN 完成检测模型构建、训练更新、IoU、AP50 和可视化。',
 req:[
  'TODO 1：解析 YOLO 归一化标注并转换为像素 xyxy，同时构造不下载权重的 Faster R-CNN 两类模型',
  'TODO 2：准备图像 Tensor 与 boxes/labels target',
  'TODO 3：完成一次损失反传与优化器更新',
  'TODO 4：实现检测框 IoU 并计算 AP50',
  'TODO 5：保存 detection_metrics.json 和 detection_preview.png'
 ]
},
'6.3.5':{
 title:'U-Net/DeepLab 语义分割与轻量 GAN 图像生成',
 tags:['U-Net','DeepLab','语义分割','IoU','GAN'],
 taskText:'在本地合成数据上完成 U-Net 跳跃连接与 IoU 评估，掌握 DeepLabV3 离线调用，并训练轻量 GAN 生成掩膜样本。',
 req:[
  'TODO 1：完成 Tiny U-Net 上采样和跳跃连接',
  'TODO 2：使用 BCEWithLogitsLoss 训练分割网络',
  'TODO 3：计算分割 IoU，创建 DeepLabV3 并检查输出尺寸，生成预览图',
  'TODO 4：训练轻量 Generator/Discriminator',
  'TODO 5：保存 segmentation_metrics.json、segmentation_preview.png 和 gan_samples.png'
 ]
},
'6.4.4':{
 title:'命名实体识别与 Transformer 翻译/BLEU',
 tags:['NER','jieba','Transformer','BLEU'],
 taskText:'使用 jieba 词性完成中文实体提取，并构建 encoder-decoder Transformer，通过 teacher forcing 训练、greedy decoding 完成中英短句翻译与 BLEU-2 评估。',
 req:[
  'TODO 1：使用 jieba.posseg 提取人名、地名和机构名',
  'TODO 2：构建 encoder-decoder Transformer，使用 teacher forcing 训练并 greedy decoding',
  'TODO 3：训练小样本翻译映射模型',
  'TODO 4：生成英文预测并计算 BLEU-2',
  'TODO 5：保存 ner_results.csv 与 translation_results.csv'
 ]
},
'6.4.5':{
 title:'GPT 文本摘要、对话/诗歌生成与 ROUGE',
 tags:['GPT','OpenAI兼容接口','摘要','对话','ROUGE'],
 taskText:'调用 OpenAI 兼容 GPT 接口完成摘要、对话回复和诗歌生成，并实现 ROUGE-L 自动评价；未配置 API 时保留离线基线。',
 req:[
  'TODO 1：实现 OpenAI 兼容 chat/completions 调用',
  'TODO 2：完成摘要、客服回复和诗歌三类生成任务',
  'TODO 3：实现最长公共子序列 LCS',
  'TODO 4：计算 ROUGE-L F1',
  'TODO 5：保存 generation_results.csv 与 rouge_report.json'
 ]
},
'6.5.4':{
 title:'LoRA/PEFT 微调与推理性能评测',
 tags:['Transformers','LoRA','PEFT','Latency','Throughput'],
 taskText:'使用本地随机初始化的小型 BERT 完成 LoRA/PEFT 参数高效微调，统计可训练参数比例、准确率、延迟与吞吐量，全程无需下载模型。',
 req:[
  'TODO 1：创建小型 BertForSequenceClassification',
  'TODO 2：配置 LoraConfig 并用 get_peft_model 包装',
  'TODO 3：完成参数高效微调并保存 adapter',
  'TODO 4：统计准确率与可训练参数比例',
  'TODO 5：评测 batch=1/8/32 的延迟和吞吐量，保存 benchmark.csv'
 ]
},
'6.5.5':{
 title:'智慧校园 AI 原型：需求、检索、界面、性能与交付',
 tags:['工程化','RAG','Tkinter','测试','文档'],
 taskText:'完成一个可复现的智慧校园制度问答原型：本地知识检索、自动评测、响应时间/吞吐量统计、Tkinter 界面和 README 交付文档。',
 req:[
  'TODO 1：读取并切分制度文档，建立 TF-IDF 检索矩阵',
  'TODO 2：实现 Top-K 检索与问答',
  'TODO 3：基于标准答案做功能准确率测试',
  'TODO 4：统计响应时间与吞吐量',
  'TODO 5：生成 app.py、README.md、demo_script.md、benchmark.csv 与 evaluation_results.csv'
 ]
},
'6.2.6':{
 title:'合成人像二分类、预测概率与 Matplotlib 标注',
 tags:['SVC','predict_proba','图像分类','概率','matplotlib'],
 taskText:'使用本地生成的合成人像完成二分类训练与概率预测。重点练习图像读取/缩放/展平、SVC(probability=True)、predict_proba，以及在结果图标题中写出预测类别和概率。',
 req:[
  'TODO 1：批量读取 portrait_images 下两类合成人像，统一为 32×32 灰度图并展平归一化',
  'TODO 2：按 3:1 分层划分训练/测试集',
  'TODO 3：使用 StandardScaler + SVC(probability=True) 完成训练并评估准确率',
  'TODO 4：读取 predict_image.png，预测类别并取得最大预测概率',
  'TODO 5：用 matplotlib 显示待测女性合成人像，在标题中标注 Prediction 与 Probability，并保存 gender_prediction.png'
 ]
},
'6.3.6':{
 title:'合成人像年龄段/性别多任务 CNN 与概率可视化',
 tags:['PyTorch','CNN','多任务学习','Softmax','概率可视化'],
 taskText:'使用本地生成的合成人像训练双输出 CNN，同时预测性别标签与年龄段标签，并把女性合成人像、两项预测结果及各自概率显示在 Matplotlib 标题中。',
 req:[
  'TODO 1：从 face_attributes 目录解析 gender/age 标签并构造 Dataset',
  'TODO 2：固定随机种子按 8:2 划分数据并建立 DataLoader',
  'TODO 3：搭建共享卷积特征 + gender_head/age_head，两个交叉熵损失相加训练',
  'TODO 4：对 woman_preview.png 做 Softmax 概率预测，分别取得性别和年龄段预测类别',
  'TODO 5：用 matplotlib 显示女性合成人像，在标题中写出 Gender/Age 与两项概率，并保存 age_gender_prediction.png'
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

