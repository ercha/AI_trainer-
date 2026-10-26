window.COMPETITION_GUIDANCE={
  overview:{
    title:'竞赛五模块学习指导',
    subtitle:'按“任务链 → 高频 API → 完整交付”训练，不背大段代码。第一次允许看指导，第二次只看题面，第三次限时完成。',
    principles:[
      '先读交付要求，再拆成数据/输入、处理、模型或算法、评价、保存五类任务',
      '每完成一步就检查变量形状、数据类型、文件路径和关键中间结果，避免最后集中排错',
      '大型模型题重点掌握数据格式、模型加载、训练/推理、指标和结果后处理，不要求从底层手写完整网络',
      '交卷前按题面逐项核对输出文件名、目录、字段和图片是否真实生成'
    ]
  },
  modules:{
    '6.1':{
      code:'A',name:'图像处理技术',score:20,days:'第 1～2 天',
      goal:'不查资料能独立写出读取 → 缩放 → 颜色转换 → 滤波 → 阈值/Canny → 形态学 → 轮廓/框选 → 保存的完整 OpenCV 流水线。',
      workflow:['读取并检查图像','统一尺寸与颜色空间','去噪或增强','阈值/边缘/颜色掩膜','形态学清理','轮廓/连通域/模板定位','统计、绘框并保存结果'],
      apiGroups:[
        {title:'基础处理',items:['cv2.imread','cv2.imwrite','cv2.resize','cv2.cvtColor','cv2.copyMakeBorder']},
        {title:'滤波与分割',items:['cv2.blur','cv2.GaussianBlur','cv2.medianBlur','cv2.threshold','cv2.Canny','cv2.inRange']},
        {title:'目标提取',items:['cv2.morphologyEx','cv2.findContours','cv2.boundingRect','cv2.connectedComponentsWithStats','cv2.matchTemplate','cv2.minMaxLoc']}
      ],
      must:['6.1.1','6.1.2','6.1.4'],strengthen:['6.1.3','6.1.5'],
      checkpoints:['imread 后先确认图像不是 None','牢记 OpenCV 默认 BGR，显示/保存前不要混淆 RGB','threshold 返回两个值，findContours 返回轮廓列表','形态学核和二值掩膜通常使用 uint8','保存前确保目录存在，并核对题目要求的文件名'],
      exam:'先把主流程跑通并生成所有要求文件，再补可视化和统计。遇到检测效果不理想时，优先检查阈值、核大小和面积过滤条件。'
    },
    '6.2':{
      code:'B',name:'机器学习算法应用',score:20,days:'第 3～5 天',
      goal:'形成“读数据 → 清洗/特征 → 划分 → 预处理 → fit → predict → 指标 → 保存”的固定模板，并能在分类、回归、聚类之间快速切换。',
      workflow:['读取并检查数据','区分特征与目标','缺失值/编码/标准化','训练测试划分','建立模型或 Pipeline','fit/predict 或 fit_predict','计算指标并比较模型','保存模型、预测和报告'],
      apiGroups:[
        {title:'数据与预处理',items:['train_test_split','SimpleImputer','StandardScaler','OneHotEncoder','ColumnTransformer','Pipeline']},
        {title:'分类/回归',items:['LogisticRegression','SVC','KNeighborsClassifier','RandomForestClassifier','LinearRegression','DecisionTreeRegressor','RandomForestRegressor']},
        {title:'聚类/降维/调参',items:['KMeans','DBSCAN','AgglomerativeClustering','GaussianMixture','silhouette_score','GridSearchCV','PCA','TSNE']}
      ],
      must:['6.2.4','6.2.3','6.2.1','6.2.5'],strengthen:['6.2.2','6.2.6'],
      checkpoints:['先 split 再对训练集 fit 预处理器，避免数据泄漏','分类任务尽量使用 stratify=y','测试集只能 transform，不能再次 fit_transform','分类看 Accuracy/Recall/F1，回归看 RMSE/R²','聚类没有真实标签时重点看簇数、噪声与 silhouette_score'],
      exam:'把预处理和模型放入 Pipeline 能显著减少漏步骤。模型比较题先统一数据划分和评价口径，再循环训练，避免不同模型使用了不同测试集。'
    },
    '6.3':{
      code:'C',name:'深度学习技术应用',score:15,days:'第 6～8 天',
      goal:'CNN 训练循环能够独立写；迁移学习会冻结/解冻；检测与分割题能根据既有框架补全数据格式、训练/推理、指标和结果保存。',
      workflow:['准备 Dataset/DataLoader','确认输入 Tensor 形状','构建或加载模型','选择 loss/optimizer/device','train 模式前向反向更新','eval + no_grad 验证','计算准确率/IoU/AP 等指标','保存权重、曲线和可视化'],
      apiGroups:[
        {title:'训练基础',items:['Dataset','DataLoader','nn.Conv2d','nn.CrossEntropyLoss','torch.optim.Adam','model.train()','model.eval()','torch.no_grad()']},
        {title:'迁移学习',items:['torchvision.models.resnet18','requires_grad','state_dict','load_state_dict']},
        {title:'检测/分割',items:['FasterRCNN','boxes/labels target','IoU/AP50','BCEWithLogitsLoss','DeepLabV3','U-Net skip connection']}
      ],
      must:['6.3.1','6.3.2','6.3.3'],strengthen:['6.3.4','6.3.5','6.3.6'],
      checkpoints:['先检查 batch 的 NCHW 形状和标签 dtype','训练阶段 model.train()，验证阶段 model.eval() + no_grad()','CrossEntropyLoss 输入 logits，不要提前 softmax','冻结层后确认真正可训练参数只包含预期层','检测框坐标格式要统一，分割预测 sigmoid/阈值后再计算 IoU'],
      exam:'先保证一个最小训练循环可运行，再补增强、冻结、指标和图片。深度学习题最常见失分不是网络复杂度，而是 shape、dtype、train/eval 状态和输出文件漏交。'
    },
    '6.4':{
      code:'D',name:'自然语言处理应用开发',score:15,days:'第 9～10 天',
      goal:'会把文本预处理、向量化/编码、模型、生成或预测、评价指标和结果保存串成完整流程；掌握 TF-IDF、NER、Transformer、BLEU、GPT API 与 ROUGE。',
      workflow:['读取文本与标签','清洗/分词/停用词','构造 TF-IDF/词向量/Token','训练分类/主题/序列模型','预测、检索或生成文本','计算 F1/BLEU/ROUGE 等指标','保存模型与结构化结果'],
      apiGroups:[
        {title:'传统 NLP',items:['jieba','TfidfVectorizer','CountVectorizer','LogisticRegression','Word2Vec','LatentDirichletAllocation','cosine_similarity']},
        {title:'序列与翻译',items:['Transformer encoder-decoder','teacher forcing','greedy decoding','BLEU']},
        {title:'生成评价',items:['chat/completions','JSON/文本解析','LCS','ROUGE-L']}
      ],
      must:['6.4.1','6.4.4','6.4.5'],strengthen:['6.4.2','6.4.3'],
      checkpoints:['训练和预测必须使用同一个向量器/词表','中文分词后再做 TF-IDF/词袋，不要直接把整句当英文空格文本处理','NER 注意实体标签或词性到人名/地名/机构名的映射','翻译任务明确 BOS/EOS、padding 和解码终止条件','API 题必须处理请求失败和返回格式异常，不能让批处理直接崩溃'],
      exam:'传统文本分类优先用稳定模板拿分；Transformer/GPT 题先把数据格式、调用和评价跑通，再追求生成质量。输出结果要可复现、可批量评测。'
    },
    '6.5':{
      code:'E',name:'人工智能创新项目实战开发',score:30,days:'第 11～13 天',
      goal:'能够从需求分析一直做到数据、模型/API、后处理、性能测试、简单界面和 README/演示脚本，形成可运行、可展示、可交付的小型 AI 项目。',
      workflow:['读需求并列出交付物','数据采集/清洗/统计','实现本地模型或 API/RAG','结构化后处理与异常兜底','功能准确率测试','延迟/吞吐量等性能测试','制作简单交互界面','输出 README、报告和演示材料'],
      apiGroups:[
        {title:'数据与展示',items:['pandas','json','matplotlib','openpyxl/Excel 输出']},
        {title:'AI 集成',items:['OpenAI 兼容 chat/completions','TF-IDF Top-K RAG','JSON 结构化输出','LoRA/PEFT']},
        {title:'工程交付',items:['time.perf_counter','batch benchmark','Tkinter','README.md','demo_script.md']}
      ],
      must:['6.5.1','6.5.3','6.5.4','6.5.5'],strengthen:['6.5.2'],
      checkpoints:['开工先写出全部交付文件清单，防止代码做完却漏文件','BASE_URL/API_KEY/MODEL 等配置不能硬编码到业务逻辑','API/RAG 必须有失败兜底和可离线运行路径','性能测试明确 batch、次数、延迟和吞吐量口径','界面不是重点，但必须能操作；README 要说明启动、依赖、输入输出和演示步骤'],
      exam:'E 模块分值最高，优先保证“能跑、能测、能展示、文件齐”。如果时间不足，先完成核心功能和交付闭环，再做界面美化或模型效果优化。'
    }
  }
};
