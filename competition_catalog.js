window.COMPETITION_DETAILS={
'5.1.1':{
  title:'模块A 人脸图像离线数据增强',
  tags:['PIL','图像增强','数据集扩充'],
  importRequired:true,
  taskText:'根据竞赛任务书完成园区人脸门禁训练数据的离线增强。原始样本位于 attendance_face，需要保留原图、随机水平翻转部分样本，并将最终数据集扩充到原始数量的 2 倍。',
  req:[
    '补全 PIL.Image 导入、attendance_face 输入目录、输出目录创建、PNG 后缀与空数据判断',
    '逐张复制原始图片到 aug_face_output；RGBA 图片保存前转换为 RGB',
    '随机抽取约 20% 原图做水平翻转，并按“原文件名_flip.后缀”保存',
    '统计当前输出数量，从原图随机补齐到原始数量的 2 倍，并按“原文件名_copy_序号.后缀”保存',
    '按顺序运行全部 Notebook 单元格，确认复制、翻转和最终数量验证均通过'
  ]
},
'5.1.2':{
  title:'模块B K-Means 图像分割与新闻主题聚类',
  tags:['KMeans','TF-IDF','图像分割','文本聚类'],
  importRequired:true,
  taskText:'使用 K-Means 完成两项无监督学习任务：对商品模特图片按像素进行前景/背景聚类分割；对中文新闻进行 TF-IDF 向量化后完成 12 类主题聚类。',
  req:[
    '将 timg.jpg 转为每行一个 RGB 像素的特征数组 pixels',
    '使用 KMeans(n_clusters=2, random_state=0) 聚类像素并生成 labels',
    '将 labels 还原为原图尺寸，用聚类中心颜色生成 uint8 分割图并与原图并排显示',
    '读取新闻语料和停用词，使用 TfidfVectorizer(stop_words=stop_words, min_df=0.01, max_df=0.5, max_features=500) 生成 news_vectors',
    '使用 KMeans(n_clusters=12, random_state=0, n_init=10) 聚类新闻，并把标签写入 news["labels"]'
  ]
},
'5.1.3':{
  title:'模块C CNN 手写数字识别',
  tags:['PyTorch','CNN','OpenCV','MNIST'],
  importRequired:true,
  taskText:'基于提供的 digits.png 手写数字大图，完成 5000 个数字单元切分、训练/测试数据构造、卷积神经网络搭建、训练以及测试准确率计算。',
  req:[
    '使用 cv2.imdecode 将字节缓冲区解码为灰度图像',
    '按 50 行×100 列切分为 5000 个 20×20 数字单元，得到形状 (50,100,20,20) 的数组',
    '每行前 50 列作为训练集、后 50 列作为测试集，构造浮点型 1×20×20 样本与每类 250 个标签',
    '在第一层卷积后补全 2×2 最大池化；训练时使用 NLL 分类损失',
    '测试时取输出最大类别作为预测并累计正确数，完成 10 轮训练与准确率评估'
  ]
},
'5.1.4':{
  title:'模块D 影评 Word2Vec 词向量训练与语义分析',
  tags:['jieba','Word2Vec','NLP','词向量'],
  importRequired:true,
  taskText:'对豆瓣影评语料进行中文分词和停用词过滤，训练 Word2Vec 词向量模型，并完成模型保存、重新加载、相似词查询和指定词向量查看。',
  req:[
    '以 UTF-8 读取 stopwords.dic，去除空白并构建停用词集合',
    '逐行读取 corpus.txt，使用 jieba.cut(..., cut_all=False) 精确分词并过滤空白词和停用词',
    '使用 Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4) 训练模型',
    '将模型保存为 word2vec.model，并重新加载验证',
    '查询与“经典”最相近的 5 个词及相似度，并输出“精彩”词向量的前 10 维'
  ]
},
'5.1.5':{
  title:'模块E 图书出版数据分析与 AI 智能报告',
  tags:['pandas','matplotlib','OpenAI兼容接口','数据分析'],
  importRequired:true,
  taskText:'基于 500 条图书出版 JSON 数据完成结构化清洗、出版年份统计与可视化，并调用 OpenAI 兼容大模型接口生成四段式市场分析 Markdown 报告；同时完成项目开发流程与工程化交付相关简答分析。',
  req:[
    '读取 book_data.json，将出版年份转 int、评分和定价转 float，异常值按要求填充并导出“图书出版数据.xlsx”',
    '计算图书数量、最早/最晚/平均出版年份，并统计 2010 年以前、2010-2019、2020 年以后三个区间',
    '绘制带标题、坐标轴标签和柱顶数值的出版年份分布柱状图，保存“图书出版年份分布.png”',
    '构造包含“数据解读、出版时间分布规律、市场商业结论、选题策划优化建议”四板块的提示词',
    '实现 OpenAI 兼容 chat/completions 调用并提取 choices[0].message.content，生成“图书出版数据分析报告.md”',
    '简答：说明 AI 创新项目完整开发流程、工程化与交付要求，以及生成式 AI/低代码/可视化工具如何辅助开发'
  ]
}
};
