// 仅覆盖竞赛 A-E 五个模块；每个知识点从概念、可运行代码到自测题。
window.BEGINNER_COURSE={
  "version": 1,
  "modules": [
    {
      "id": "A",
      "name": "图像处理技术",
      "intro": "从像素、数组和文件路径开始，逐步掌握 OpenCV 的读取、转换、滤波、分割、轮廓与保存。无需先懂图像算法。",
      "steps": [
        {
          "title": "认识 Python 变量与图像",
          "concept": "变量保存数据；print 输出；函数是可重复使用的操作。图像本质上是由像素组成的数组。先用最简单的 NumPy 数组理解灰度像素。",
          "code": "import numpy as np\npixels = np.array([[0, 128], [200, 255]], dtype=np.uint8)\nprint(pixels)\nprint(\"形状:\", pixels.shape)\nprint(\"数据类型:\", pixels.dtype)",
          "steps": [
            "np.array 把列表变成数组",
            "shape 的两个数是行数、列数",
            "uint8 表示像素通常位于 0~255"
          ],
          "challenge": "创建 3×3 的全黑灰度图，并打印形状。",
          "solution": "black = np.zeros((3, 3), dtype=np.uint8)\nprint(black.shape)",
          "quiz": {
            "question": "灰度图 shape=(20,30) 表示什么？",
            "options": [
              "20 列、30 行",
              "20 行、30 列",
              "20 张图"
            ],
            "answer": 1,
            "reason": "灰度图通常用 (高度, 宽度) 表示。"
          },
          "exam": "6.1.1",
          "minutes": 20,
          "id": "A1"
        },
        {
          "title": "读取与保存，处理中文路径",
          "concept": "OpenCV 读入彩色图默认为 BGR。cv2.imread 失败会返回 None；中文路径可使用 np.fromfile + cv2.imdecode，保存使用 cv2.imencode(...).tofile。",
          "code": "from pathlib import Path\nimport cv2, numpy as np\nsrc = Path(\"练习图片.png\")\nif src.exists():\n    img = cv2.imdecode(np.fromfile(str(src), dtype=np.uint8), cv2.IMREAD_COLOR)\n    if img is None:\n        raise ValueError(\"无法解码图片\")\n    ok, buf = cv2.imencode(\".png\", img)\n    if ok:\n        buf.tofile(\"保存结果.png\")\nelse:\n    print(\"先在当前目录放入练习图片.png\")",
          "steps": [
            "exists 先验证文件存在",
            "imdecode 负责解码图像字节",
            "imencode 得到可写入磁盘的图像字节"
          ],
          "challenge": "不使用现成图片，生成 60×80 的纯色图并用中文文件名保存。",
          "solution": "img = np.full((60, 80, 3), 180, dtype=np.uint8)\ncv2.imencode(\".png\", img)[1].tofile(\"输出图像.png\")",
          "quiz": {
            "question": "cv2.imread 找不到文件时通常返回？",
            "options": [
              "None",
              "空字典",
              "False 数字"
            ],
            "answer": 0,
            "reason": "要在图像处理前检查 img is None。"
          },
          "exam": "6.1.1",
          "minutes": 20,
          "id": "A2"
        },
        {
          "title": "图像缩放、边框和颜色空间",
          "concept": "resize 改变宽高；copyMakeBorder 扩展边缘；cvtColor 负责灰度、HSV、RGB 转换。与数组 shape 不同，resize 的尺寸参数是 (宽,高)。",
          "code": "import cv2, numpy as np\nimg = np.zeros((80, 120, 3), dtype=np.uint8)\nsmall = cv2.resize(img, (60, 40))\ngray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)\nframe = cv2.copyMakeBorder(gray, 5, 5, 5, 5, cv2.BORDER_REFLECT)\nprint(img.shape, small.shape, gray.shape, frame.shape)",
          "steps": [
            "图像数组 shape 常见为 (高,宽,通道)",
            "resize 的 dsize 则为 (宽,高)",
            "BGR2GRAY 后彩色通道维消失"
          ],
          "challenge": "将 100×200 的彩色数组缩放为宽 50、高 25，并打印 shape。",
          "solution": "result = cv2.resize(np.zeros((100, 200, 3), dtype=np.uint8), (50, 25))\nprint(result.shape)",
          "quiz": {
            "question": "cv2.resize(img, (80,40)) 的输出宽高是？",
            "options": [
              "宽40高80",
              "宽80高40",
              "都为80"
            ],
            "answer": 1,
            "reason": "dsize 顺序是宽度在前。"
          },
          "exam": "6.1.1",
          "minutes": 20,
          "id": "A3"
        },
        {
          "title": "均值、高斯与中值滤波",
          "concept": "滤波用于减少噪声。均值滤波取邻域均值；高斯滤波按距离加权；中值滤波抗椒盐噪声。常用核尺寸为奇数。",
          "code": "import numpy as np, cv2\nimg = np.full((60, 60), 120, dtype=np.uint8)\nimg[30, 30] = 255\nmean = cv2.blur(img, (5, 5))\ngauss = cv2.GaussianBlur(img, (5, 5), 0)\nmedian = cv2.medianBlur(img, 5)\nprint(mean[30,30], gauss[30,30], median[30,30])",
          "steps": [
            "blur 的核大小用元组",
            "GaussianBlur 第三个参数 0 表示自动计算 sigmaX",
            "medianBlur 第二个参数是奇数整数"
          ],
          "challenge": "把示例高斯核改为 (3,3)，并观察中心值变化。",
          "solution": "gauss3 = cv2.GaussianBlur(img, (3, 3), 0)\nprint(gauss3[30, 30])",
          "quiz": {
            "question": "去除椒盐噪声最常用哪种？",
            "options": [
              "中值滤波",
              "图像反色",
              "边框复制"
            ],
            "answer": 0,
            "reason": "中值能减少孤立的极端亮暗像素。"
          },
          "exam": "6.1.1",
          "minutes": 20,
          "id": "A4"
        },
        {
          "title": "阈值分割、Canny 与形态学",
          "concept": "阈值分割产生黑白掩膜；Canny 提取边缘；开运算去小噪点，闭运算填小孔洞。",
          "code": "import cv2, numpy as np\nimg = np.zeros((100, 100), dtype=np.uint8)\ncv2.rectangle(img, (20,20), (80,80), 230, -1)\n_, mask = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)\nedges = cv2.Canny(img, 80, 160)\nkernel = np.ones((3,3), np.uint8)\nclean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)\nprint(np.unique(clean), np.count_nonzero(edges))",
          "steps": [
            "threshold 返回 (阈值,结果图)",
            "Canny 的两级阈值控制边缘筛选",
            "morphologyEx 使用结构元素 kernel"
          ],
          "challenge": "给 mask 再执行一次闭运算，核尺寸为 3×3。",
          "solution": "closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)",
          "quiz": {
            "question": "threshold 通常返回几个值？",
            "options": [
              "1 个",
              "2 个",
              "3 个"
            ],
            "answer": 1,
            "reason": "常写成 _, binary = cv2.threshold(...)。"
          },
          "exam": "6.1.2",
          "minutes": 20,
          "id": "A5"
        },
        {
          "title": "轮廓统计、可视化与交付",
          "concept": "从掩膜提取轮廓后，可计算面积与外接框，并用 Matplotlib 比较处理前后。竞赛要核对实际文件是否保存成功。",
          "code": "import cv2, numpy as np\nimport matplotlib.pyplot as plt\nfrom pathlib import Path\nimg = np.zeros((80, 100), dtype=np.uint8)\ncv2.rectangle(img, (20, 10), (70, 60), 255, -1)\ncontours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)\nprint(\"轮廓数量:\", len(contours))\nprint(\"外接框:\", cv2.boundingRect(contours[0]))\nPath(\"output\").mkdir(exist_ok=True)\nplt.imshow(img, cmap=\"gray\"); plt.title(\"mask\"); plt.axis(\"off\")\nplt.savefig(\"output/preview.png\", dpi=150); plt.close()",
          "steps": [
            "findContours 需要单通道二值图",
            "boundingRect 结果为 (x,y,w,h)",
            "savefig 后检查文件路径"
          ],
          "challenge": "打印最大轮廓的面积，并确认 preview.png 存在。",
          "solution": "print(max(cv2.contourArea(c) for c in contours))\nprint(Path(\"output/preview.png\").exists())",
          "quiz": {
            "question": "绘制 OpenCV 灰度数组时，Matplotlib 常用什么参数？",
            "options": [
              "cmap='gray'",
              "linewidth=10",
              "alpha=0"
            ],
            "answer": 0,
            "reason": "imshow(cmap='gray') 用灰度色图显示单通道。"
          },
          "exam": "6.1.3",
          "minutes": 20,
          "id": "A6"
        }
      ]
    },
    {
      "id": "B",
      "name": "机器学习算法应用",
      "intro": "先理解数据表、特征、标签和训练测试集，再学习 sklearn 的分类、回归、聚类、调参和评价指标。",
      "steps": [
        {
          "title": "认识数据表、特征和标签",
          "concept": "一行是一个样本，一列是一个字段。X 表示用于预测的特征，y 表示标准答案/目标。DataFrame 是 Pandas 的二维表格。",
          "code": "import pandas as pd\ndf = pd.DataFrame({\"年龄\":[18,25,30],\"学习小时\":[2,5,8],\"通过\":[0,1,1]})\nprint(df.head())\nX = df[[\"年龄\",\"学习小时\"]]\ny = df[\"通过\"]\nprint(X.shape, y.shape)",
          "steps": [
            "双中括号取得二维特征表",
            "单中括号取得目标列",
            "先检查 head、shape、dtypes"
          ],
          "challenge": "打印 df 的列名，并统计“通过”列每个类别的数量。",
          "solution": "print(df.columns.tolist())\nprint(df[\"通过\"].value_counts())",
          "quiz": {
            "question": "监督学习中 y 一般表示？",
            "options": [
              "样本编号",
              "预测目标或标签",
              "绘图宽度"
            ],
            "answer": 1,
            "reason": "训练模型要比较预测值与目标标签。"
          },
          "exam": "6.2.4",
          "minutes": 20,
          "id": "B1"
        },
        {
          "title": "数据清洗、划分与数据泄漏",
          "concept": "训练前要处理缺失值、数值缩放和类别编码。通常先划分训练/测试，再只在训练集拟合预处理器，防止泄漏。",
          "code": "import numpy as np\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler\nX = np.array([[1.0],[2],[np.nan],[4],[5],[6],[7],[8],[9],[10]])\ny = [0,0,0,0,0,1,1,1,1,1]\nXtr, Xte, ytr, yte = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)\nimp = SimpleImputer(strategy=\"median\")\nscaler = StandardScaler()\nXtr = scaler.fit_transform(imp.fit_transform(Xtr))\nXte = scaler.transform(imp.transform(Xte))\nprint(Xtr.shape, Xte.shape)",
          "steps": [
            "test_size=0.2 表示留 20% 测试集",
            "imputer 根据训练数据计算填补值",
            "测试数据只能 transform"
          ],
          "challenge": "将 StandardScaler 改成使用训练数据拟合后变换全部测试数据，确认代码没有 test.fit。",
          "solution": "train_scaled = scaler.fit_transform(imp.fit_transform(Xtr))\ntest_scaled = scaler.transform(imp.transform(Xte))",
          "quiz": {
            "question": "哪种写法会造成数据泄漏？",
            "options": [
              "训练集 fit，测试集 transform",
              "训练和测试集都分别 fit_transform",
              "只对训练集 fit"
            ],
            "answer": 1,
            "reason": "不能用测试集学习预处理参数。"
          },
          "exam": "6.2.2",
          "minutes": 20,
          "id": "B2"
        },
        {
          "title": "分类：fit、predict 与准确率",
          "concept": "分类模型输出离散类别。先选模型，用 fit 训练，再用 predict 预测，用 accuracy_score 对照 y_test。",
          "code": "from sklearn.datasets import load_iris\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\nX, y = load_iris(return_X_y=True)\nXtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)\nmodel=LogisticRegression(max_iter=300)\nmodel.fit(Xtr,ytr)\npred=model.predict(Xte)\nprint(\"准确率:\",accuracy_score(yte,pred))",
          "steps": [
            "fit 接受 X_train、y_train",
            "predict 接受 X_test",
            "评价时必须使用测试标签 y_test"
          ],
          "challenge": "把分类器换成 KNeighborsClassifier(n_neighbors=5) 后重新计算准确率。",
          "solution": "from sklearn.neighbors import KNeighborsClassifier\nmodel=KNeighborsClassifier(n_neighbors=5).fit(Xtr,ytr)\nprint(accuracy_score(yte,model.predict(Xte)))",
          "quiz": {
            "question": "accuracy_score(yte,pred) 比较的是什么？",
            "options": [
              "训练耗时",
              "预测正确占比",
              "图片大小"
            ],
            "answer": 1,
            "reason": "准确率是预测正确样本的比例。"
          },
          "exam": "6.2.4",
          "minutes": 20,
          "id": "B3"
        },
        {
          "title": "Pipeline、ColumnTransformer 与 F1",
          "concept": "Pipeline 串联预处理和模型。ColumnTransformer 把不同列交给不同预处理流程。Precision 看预测为正的可靠性，Recall 看正例找回多少，F1 综合二者。",
          "code": "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.svm import SVC\nfrom sklearn.metrics import classification_report\nfrom sklearn.datasets import load_iris\nfrom sklearn.model_selection import train_test_split\nX,y=load_iris(return_X_y=True)\nXtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)\npipe=Pipeline([(\"scaler\",StandardScaler()),(\"model\",SVC())])\npipe.fit(Xtr,ytr)\nprint(classification_report(yte,pipe.predict(Xte),zero_division=0))",
          "steps": [
            "Pipeline 是按顺序执行的步骤组合",
            "scaler、model 是用户自定义的步骤名称",
            "classification_report 汇总 precision/recall/f1"
          ],
          "challenge": "把 SVC 替换为 LogisticRegression(max_iter=300)。",
          "solution": "from sklearn.linear_model import LogisticRegression\npipe=Pipeline([(\"scaler\",StandardScaler()),(\"model\",LogisticRegression(max_iter=300))])\npipe.fit(Xtr,ytr)",
          "quiz": {
            "question": "Pipeline 的 scaler 字符串表示？",
            "options": [
              "步骤名称",
              "文件名",
              "显卡名称"
            ],
            "answer": 0,
            "reason": "它是供访问和识别步骤用的自定义名字。"
          },
          "exam": "6.2.2",
          "minutes": 20,
          "id": "B4"
        },
        {
          "title": "回归：数值预测与误差",
          "concept": "回归预测连续数值。常见模型有线性回归、决策树和随机森林。RMSE 越小通常表示预测误差越小。",
          "code": "from sklearn.datasets import make_regression\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LinearRegression\nfrom sklearn.metrics import mean_squared_error, r2_score\nimport numpy as np\nX,y=make_regression(n_samples=120,n_features=3,noise=8,random_state=42)\nXtr,Xte,ytr,yte=train_test_split(X,y,random_state=42)\nmodel=LinearRegression().fit(Xtr,ytr)\npred=model.predict(Xte)\nprint(\"RMSE:\",np.sqrt(mean_squared_error(yte,pred)))\nprint(\"R2:\",r2_score(yte,pred))",
          "steps": [
            "回归预测值不是类别编号",
            "RMSE 是均方误差的平方根",
            "R² 越高通常拟合越好"
          ],
          "challenge": "换用 RandomForestRegressor(n_estimators=100,random_state=42) 对比 RMSE。",
          "solution": "from sklearn.ensemble import RandomForestRegressor\nrf=RandomForestRegressor(n_estimators=100,random_state=42).fit(Xtr,ytr)\nprint(np.sqrt(mean_squared_error(yte,rf.predict(Xte))))",
          "quiz": {
            "question": "房价预测属于？",
            "options": [
              "回归",
              "文本分类",
              "图像分割"
            ],
            "answer": 0,
            "reason": "目标是连续的房价数值。"
          },
          "exam": "6.2.3",
          "minutes": 20,
          "id": "B5"
        },
        {
          "title": "聚类、网格搜索与模型保存",
          "concept": "聚类是不依赖标准类别标签的分组。KMeans 需要设置簇数 k；轮廓系数衡量簇内紧密与簇间分离。joblib 可保存训练好的模型。",
          "code": "from sklearn.datasets import make_blobs\nfrom sklearn.cluster import KMeans\nfrom sklearn.metrics import silhouette_score\nimport joblib\nX,_=make_blobs(n_samples=100,centers=3,random_state=42)\nmodel=KMeans(n_clusters=3,random_state=42,n_init=10)\nlabels=model.fit_predict(X)\nprint(\"轮廓系数:\",silhouette_score(X,labels))\njoblib.dump(model,\"kmeans_model.pkl\")",
          "steps": [
            "fit_predict 会训练并给出聚类编号",
            "没有真实标签也能评价聚类结构",
            "保存 .pkl 方便后续加载"
          ],
          "challenge": "把 k 依次设为 2、3、4，找轮廓系数最大的一组。",
          "solution": "for k in [2,3,4]:\n    labels=KMeans(n_clusters=k,random_state=42,n_init=10).fit_predict(X)\n    print(k,silhouette_score(X,labels))",
          "quiz": {
            "question": "KMeans(n_clusters=3) 中 3 表示？",
            "options": [
              "3 个特征",
              "3 个聚类中心",
              "3 次训练"
            ],
            "answer": 1,
            "reason": "n_clusters 控制希望分成几个簇。"
          },
          "exam": "6.2.1",
          "minutes": 20,
          "id": "B6"
        }
      ]
    },
    {
      "id": "C",
      "name": "深度学习技术应用",
      "intro": "从 Tensor 开始，学会模型、损失、梯度、训练循环、CNN、迁移学习、检测分割。示例优先在 CPU 上运行。",
      "steps": [
        {
          "title": "Tensor 与 CPU/GPU 设备",
          "concept": "Tensor 类似 NumPy 数组，但支持自动求导与 GPU 运算。训练前用 torch.cuda.is_available 检查 NVIDIA CUDA；CPU 同样能完成基础练习。",
          "code": "import torch\ndevice=torch.device(\"cuda\" if torch.cuda.is_available() else \"cpu\")\nx=torch.tensor([[1.,2.],[3.,4.]],device=device)\nprint(\"设备:\",device)\nprint(\"形状:\",x.shape)\nprint(x.mean())",
          "steps": [
            "torch.tensor 创建张量",
            "device 决定张量在哪运行",
            "print(x.shape) 检查维度"
          ],
          "challenge": "创建形状为 (2,3) 的全零 Tensor，并移到 device。",
          "solution": "z=torch.zeros((2,3),device=device)\nprint(z.shape)",
          "quiz": {
            "question": "没有 NVIDIA CUDA 显卡能否学习 PyTorch 基础？",
            "options": [
              "不能",
              "可以，在 CPU 上运行",
              "只能使用网页"
            ],
            "answer": 1,
            "reason": "CPU 也可以运行大多数入门示例。"
          },
          "exam": "6.3.1",
          "minutes": 20,
          "id": "C1"
        },
        {
          "title": "神经网络、层、损失函数",
          "concept": "nn.Linear 表示线性层；前向传播给出预测值；loss 比较预测与真实目标。分类用 CrossEntropyLoss 时应输入 logits，不需要提前 softmax。",
          "code": "import torch\nfrom torch import nn\nx=torch.randn(4,3)\ny=torch.tensor([0,1,0,1])\nnet=nn.Sequential(nn.Linear(3,8),nn.ReLU(),nn.Linear(8,2))\nout=net(x)\nloss=nn.CrossEntropyLoss()(out,y)\nprint(out.shape,loss.item())",
          "steps": [
            "4 表示一批 4 个样本",
            "输出最后一维 2 是两类 logits",
            "CrossEntropyLoss 接受整数类别标签"
          ],
          "challenge": "将中间隐藏层由 8 改成 16，保持最终输出 2 类。",
          "solution": "net=nn.Sequential(nn.Linear(3,16),nn.ReLU(),nn.Linear(16,2))",
          "quiz": {
            "question": "CrossEntropyLoss 前需要手动调用 softmax 吗？",
            "options": [
              "需要",
              "不需要",
              "必须归一化成 0~255"
            ],
            "answer": 1,
            "reason": "CrossEntropyLoss 直接接收原始 logits。"
          },
          "exam": "6.3.1",
          "minutes": 20,
          "id": "C2"
        },
        {
          "title": "训练循环与反向传播",
          "concept": "一次训练迭代包含：清空梯度 zero_grad，前向预测，计算损失，backward 反向传播，step 更新参数。",
          "code": "import torch\nfrom torch import nn\nx=torch.tensor([[0.],[1.],[2.],[3.]])\ny=2*x+1\nnet=nn.Linear(1,1)\nopt=torch.optim.SGD(net.parameters(),lr=0.05)\nfor epoch in range(100):\n    opt.zero_grad()\n    loss=nn.MSELoss()(net(x),y)\n    loss.backward()\n    opt.step()\nprint(\"最终损失:\",loss.item())",
          "steps": [
            "zero_grad 避免上一步梯度累积",
            "backward 计算各参数梯度",
            "step 实际更新模型参数"
          ],
          "challenge": "把训练轮数改成 200，观察最终损失是否下降。",
          "solution": "for epoch in range(200):\n    opt.zero_grad()\n    loss=nn.MSELoss()(net(x),y)\n    loss.backward()\n    opt.step()",
          "quiz": {
            "question": "哪一步更新模型权重？",
            "options": [
              "loss.backward()",
              "opt.step()",
              "net.eval()"
            ],
            "answer": 1,
            "reason": "backward 算梯度，step 用梯度更新权重。"
          },
          "exam": "6.3.1",
          "minutes": 20,
          "id": "C3"
        },
        {
          "title": "CNN、卷积与图像形状",
          "concept": "Conv2d 处理二维图像；常见输入维度是 NCHW（批量、通道、高、宽）。MaxPool2d 会缩小空间尺寸，分类头常把特征图展平。",
          "code": "import torch\nfrom torch import nn\nx=torch.randn(2,1,20,20)\nnet=nn.Sequential(nn.Conv2d(1,8,3),nn.ReLU(),nn.MaxPool2d(2),nn.Flatten(),nn.Linear(8*9*9,10))\ny=net(x)\nprint(\"输出形状:\",y.shape)",
          "steps": [
            "无 padding 的 3×3 卷积让 20×20 变成 18×18",
            "2×2 池化后变成 9×9",
            "Linear 的输入数为 8×9×9"
          ],
          "challenge": "将 batch 从 2 改成 5，预测输出 shape 应该是什么？",
          "solution": "x=torch.randn(5,1,20,20)\nprint(net(x).shape)  # (5, 10)",
          "quiz": {
            "question": "Conv2d 输入的形状通常是？",
            "options": [
              "NHWC",
              "NCHW",
              "CHN"
            ],
            "answer": 1,
            "reason": "PyTorch 常用 NCHW。"
          },
          "exam": "6.3.1",
          "minutes": 20,
          "id": "C4"
        },
        {
          "title": "验证模式与模型保存",
          "concept": "训练使用 model.train；验证使用 model.eval 搭配 torch.no_grad。保存 state_dict 可复用模型权重，加载时结构必须匹配。",
          "code": "import torch\nfrom torch import nn\nnet=nn.Linear(3,2)\nnet.eval()\nwith torch.no_grad():\n    pred=net(torch.randn(4,3))\ntorch.save(net.state_dict(),\"demo.pt\")\nloaded=nn.Linear(3,2)\nloaded.load_state_dict(torch.load(\"demo.pt\",map_location=\"cpu\",weights_only=True))\nprint(pred.shape)",
          "steps": [
            "eval 会影响 Dropout/BatchNorm 等层",
            "no_grad 避免记录验证阶段计算图",
            "重新加载时创建相同结构的模型"
          ],
          "challenge": "比较 net 和 loaded 对同一输入的输出是否一致。",
          "solution": "x=torch.randn(2,3)\nwith torch.no_grad():\n    print(torch.allclose(net(x),loaded(x)))",
          "quiz": {
            "question": "验证模型时应使用哪个组合？",
            "options": [
              "train + backward",
              "eval + no_grad",
              "只使用 optimizer.step"
            ],
            "answer": 1,
            "reason": "验证不应更新权重。"
          },
          "exam": "6.3.2",
          "minutes": 20,
          "id": "C5"
        },
        {
          "title": "迁移学习、检测框与 IoU",
          "concept": "迁移学习常冻结已有骨干并替换分类头；目标检测返回框和类别；IoU = 两个框的交集面积 / 并集面积。语义分割输出每像素类别。",
          "code": "import torch\nbox_a=torch.tensor([0.,0.,4.,4.])\nbox_b=torch.tensor([2.,2.,6.,6.])\ninter_w=max(0.,float(min(box_a[2],box_b[2])-max(box_a[0],box_b[0])))\ninter_h=max(0.,float(min(box_a[3],box_b[3])-max(box_a[1],box_b[1])))\ninter=inter_w*inter_h\niou=inter/(16+16-inter)\nprint(\"IoU:\",iou)",
          "steps": [
            "xyxy 表示左上和右下角坐标",
            "计算交集面积要避免负宽高",
            "检测、分割都要先核对坐标或像素格式"
          ],
          "challenge": "把 box_b 改成和 box_a 完全一样，验证 IoU=1。",
          "solution": "box_b=box_a.clone()\nprint(\"重合框的 IoU 为 1\")",
          "quiz": {
            "question": "两个框完全重合时 IoU 为多少？",
            "options": [
              "0",
              "0.5",
              "1"
            ],
            "answer": 2,
            "reason": "交集等于并集，所以 IoU=1。"
          },
          "exam": "6.3.4",
          "minutes": 20,
          "id": "C6"
        }
      ]
    },
    {
      "id": "D",
      "name": "自然语言处理应用开发",
      "intro": "从字符串、分词开始，认识词袋和 TF-IDF、词向量、文本分类、序列建模、生成与 BLEU/ROUGE。",
      "steps": [
        {
          "title": "字符串、文本清洗与中文分词",
          "concept": "文本首先是字符串。strip 去掉首尾空白；replace 替换；jieba 可把中文句子分为词。基础课程不必先懂 Transformer。",
          "code": "text=\"  人工智能正在改变学习。  \"\nclean=text.strip().replace(\"。\",\"\")\nprint(clean)\ntry:\n    import jieba\n    print(list(jieba.cut(clean)))\nexcept ImportError:\n    print(\"需安装 competition_advanced_requirements.txt\")",
          "steps": [
            "strip() 处理空白",
            "replace() 替换指定文本",
            "中文分词结果是词列表"
          ],
          "challenge": "对“机器学习与图像处理”进行 jieba 精确分词。",
          "solution": "import jieba\nprint(list(jieba.cut(\"机器学习与图像处理\",cut_all=False)))",
          "quiz": {
            "question": "jieba.cut 的用途是？",
            "options": [
              "中文分词",
              "图像缩放",
              "训练 CNN"
            ],
            "answer": 0,
            "reason": "分词把文本切成可用于建模的词。"
          },
          "exam": "6.4.1",
          "minutes": 20,
          "id": "D1"
        },
        {
          "title": "词袋与 TF-IDF 向量化",
          "concept": "模型不能直接计算自然语言，需要转成数值向量。CountVectorizer 统计词频；TfidfVectorizer 提高具有区分度词语的权重。",
          "code": "from sklearn.feature_extraction.text import TfidfVectorizer\ntexts=[\"体育 比赛 足球\",\"科技 人工智能 计算机\",\"体育 足球 球队\"]\nvec=TfidfVectorizer()\nX=vec.fit_transform(texts)\nprint(vec.get_feature_names_out())\nprint(X.shape)",
          "steps": [
            "fit 学习词表",
            "transform 将文本转成向量",
            "shape=(文本数,词表长度)"
          ],
          "challenge": "增加一句“科技 计算机 算法”，再观察矩阵行数。",
          "solution": "texts.append(\"科技 计算机 算法\")\nprint(vec.fit_transform(texts).shape)",
          "quiz": {
            "question": "TF-IDF 主要用于？",
            "options": [
              "特征向量化",
              "图像滤波",
              "GPU 显存检测"
            ],
            "answer": 0,
            "reason": "文本先数值化才可训练传统模型。"
          },
          "exam": "6.4.1",
          "minutes": 20,
          "id": "D2"
        },
        {
          "title": "新闻分类与 F1",
          "concept": "文本分类流程：标签、训练集、TF-IDF、分类器、预测和指标。Pipeline 能防止训练/测试词表不一致。",
          "code": "from sklearn.pipeline import Pipeline\nfrom sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.linear_model import LogisticRegression\ntexts=[\"体育 足球 比赛\",\"体育 球队 进球\",\"科技 电脑 软件\",\"科技 算法 模型\"]\ny=[0,0,1,1]\npipe=Pipeline([(\"tfidf\",TfidfVectorizer()),(\"clf\",LogisticRegression())])\npipe.fit(texts,y)\nprint(pipe.predict([\"足球 进球\",\"电脑 算法\"]))",
          "steps": [
            "整个 Pipeline 只需一次 fit",
            "predict 自动使用同一个向量器",
            "真实项目应划分测试集并计算 F1"
          ],
          "challenge": "预测文本“科技 软件”，查看类别是否为 1。",
          "solution": "print(pipe.predict([\"科技 软件\"])[0])",
          "quiz": {
            "question": "对新文章预测时应该重新 fit TF-IDF 吗？",
            "options": [
              "应该",
              "不应该",
              "都可以"
            ],
            "answer": 1,
            "reason": "使用训练时相同的词表和权重映射。"
          },
          "exam": "6.4.1",
          "minutes": 20,
          "id": "D3"
        },
        {
          "title": "词向量、主题发现与实体",
          "concept": "Word2Vec 使词具有数值向量，能够测量相似性。LDA 通过词分布发现文档主题。NER 则提取人名、地名、组织等实体。",
          "code": "from sklearn.feature_extraction.text import CountVectorizer\nfrom sklearn.decomposition import LatentDirichletAllocation\ntexts=[\"足球 运动 球队\",\"球队 足球 比赛\",\"电脑 软件 算法\",\"科技 算法 软件\"]\nvec=CountVectorizer()\nX=vec.fit_transform(texts)\nlda=LatentDirichletAllocation(n_components=2,random_state=42)\nprint(\"主题概率 shape:\",lda.fit_transform(X).shape)",
          "steps": [
            "Word2Vec 任务通常要先分词",
            "LDA 是无监督主题模型",
            "实体抽取返回结构化名称或位置"
          ],
          "challenge": "打印第一篇文本的主题概率。",
          "solution": "topics=lda.transform(X)\nprint(topics[0])",
          "quiz": {
            "question": "LDA 的 n_components=2 表示？",
            "options": [
              "2 个主题",
              "2 张图片",
              "2 个 GPU"
            ],
            "answer": 0,
            "reason": "该参数是主题数量。"
          },
          "exam": "6.4.3",
          "minutes": 20,
          "id": "D4"
        },
        {
          "title": "序列模型、LSTM 与采样",
          "concept": "RNN/LSTM 按顺序处理序列；模型输出常是二维形状 (batch,vocab)。np.random.choice 的 p 要求一维、非负、和为 1 的概率；应取某一个样本并归一化。",
          "code": "import numpy as np\nlogits=np.array([[1.0,2.0,0.5]])\nex=np.exp(logits[0]-logits[0].max())\nprobs=ex/ex.sum()\nchoice=np.random.choice(len(probs),p=probs)\nprint(\"概率形状:\",probs.shape,\"和:\",probs.sum(),\"采样:\",choice)",
          "steps": [
            "模型的 (1,3) 输出不能直接作为 p",
            "logits 要先 softmax 成概率",
            "p 的长度必须等于候选项数量"
          ],
          "challenge": "将 probs 改为 np.array([0.2,0.3,0.5])，采样十次。",
          "solution": "probs=np.array([0.2,0.3,0.5])\nprint(np.random.choice(3,size=10,p=probs))",
          "quiz": {
            "question": "np.random.choice(3,p=...) 的 p 应是？",
            "options": [
              "形状 (1,3) 的 logits",
              "长度 3、和为 1 的一维概率",
              "任意二维矩阵"
            ],
            "answer": 1,
            "reason": "p 必须是一维概率数组。"
          },
          "exam": "6.4.4",
          "minutes": 20,
          "id": "D5"
        },
        {
          "title": "Transformer、生成、BLEU 与 ROUGE",
          "concept": "Transformer 使用注意力处理上下文；生成时需要指定停止条件。BLEU 评估机器翻译的 n-gram 精度，ROUGE 常用于摘要结果的词语重合度。",
          "code": "# 不用下载模型，先理解“参考结果”和“预测结果”\nreference=[\"人工\",\"智能\",\"发展\"]\nprediction=[\"人工\",\"智能\",\"应用\"]\noverlap=len(set(reference)&set(prediction))\nprecision=overlap/len(prediction)\nrecall=overlap/len(reference)\nprint(\"演示重合精确率:\",precision,\"召回率:\",recall)\n# 注意：上面仅是词集合演示，并非正式 BLEU 或 ROUGE 公式",
          "steps": [
            "正式 BLEU 要考虑 n-gram 和长度惩罚",
            "ROUGE-L 通常利用最长公共子序列",
            "API 和模型生成题还要验证输出格式"
          ],
          "challenge": "写出对候选和参考文本相同词数的统计，说明这不等于 BLEU。",
          "solution": "print(len(set(reference).intersection(prediction)))",
          "quiz": {
            "question": "BLEU 主要用于评价什么？",
            "options": [
              "图像尺寸",
              "翻译生成质量",
              "GPU 温度"
            ],
            "answer": 1,
            "reason": "BLEU 是翻译任务常用评价指标。"
          },
          "exam": "6.4.4",
          "minutes": 20,
          "id": "D6"
        }
      ]
    },
    {
      "id": "E",
      "name": "人工智能创新项目实战开发",
      "intro": "以可交付的小项目为主线，完成需求、数据、可视化、模型/API 集成、测试和报告，不必一开始训练大模型。",
      "steps": [
        {
          "title": "认识项目需求与交付物",
          "concept": "综合项目不只是模型准确率；需要明确输入、处理步骤、输出文件、异常处理及演示。先把任务书变成验收清单。",
          "code": "from pathlib import Path\noutputs=[\"cleaned.csv\",\"chart.png\",\"report.md\"]\nfor name in outputs:\n    print(name,\"已存在\" if Path(name).exists() else \"尚未生成\")",
          "steps": [
            "确定数据输入来源",
            "列出全部输出文件名和格式",
            "提前定义可检查的完成标准"
          ],
          "challenge": "把预测结果 predictions.csv 加入交付清单，再输出检查结果。",
          "solution": "outputs.append(\"predictions.csv\")\nprint(outputs)",
          "quiz": {
            "question": "交付时最容易遗漏的是？",
            "options": [
              "实际生成输出文件",
              "更换主题颜色",
              "增加注释长度"
            ],
            "answer": 0,
            "reason": "文件是否存在需要真实检查。"
          },
          "exam": "6.5.1",
          "minutes": 20,
          "id": "E1"
        },
        {
          "title": "读取 JSON、清洗数据、统计",
          "concept": "JSON 是一种常见数据交换格式，Pandas 可将对象列表转成表。先确定字段类型，再计算业务统计。",
          "code": "import pandas as pd\nrows=[{\"书名\":\"A\",\"价格\":\"20\",\"销量\":2},{\"书名\":\"B\",\"价格\":\"30\",\"销量\":3}]\ndf=pd.DataFrame(rows)\ndf[\"价格\"]=pd.to_numeric(df[\"价格\"],errors=\"coerce\")\ndf[\"销售额\"]=df[\"价格\"]*df[\"销量\"]\nprint(df)\nprint(\"总销售额:\",df[\"销售额\"].sum())",
          "steps": [
            "to_numeric(errors='coerce') 将非法数据转成 NaN",
            "新建字段使用 df['列名']=...",
            "指标前先核验原始字段含义"
          ],
          "challenge": "将清洗结果导出为 cleaned.csv，不保存索引并使用 utf-8-sig 编码。",
          "solution": "df.to_csv(\"cleaned.csv\",index=False,encoding=\"utf-8-sig\")",
          "quiz": {
            "question": "保存 CSV 时 index=False 表示？",
            "options": [
              "不保存 DataFrame 索引列",
              "不保存标题",
              "只保存前 10 行"
            ],
            "answer": 0,
            "reason": "用于避免多出来的一列数字索引。"
          },
          "exam": "6.5.1",
          "minutes": 20,
          "id": "E2"
        },
        {
          "title": "Matplotlib 图表与结果文件",
          "concept": "项目图表要标明标题、坐标轴并保存 PNG。使用 plt.tight_layout 避免标签被遮挡；非英文字体可能需要按本机安装情况配置。",
          "code": "import matplotlib.pyplot as plt\nfrom pathlib import Path\nnames=[\"A\",\"B\",\"C\"]; values=[10,18,13]\nplt.bar(names,values)\nplt.title(\"Count by group\")\nplt.xlabel(\"Group\"); plt.ylabel(\"Count\")\nplt.tight_layout()\nPath(\"output\").mkdir(exist_ok=True)\nplt.savefig(\"output/chart.png\",dpi=150)\nplt.close()\nprint(Path(\"output/chart.png\").exists())",
          "steps": [
            "bar 绘制柱形图",
            "title/xlabel/ylabel 是基本标注",
            "savefig 保存到磁盘，close 释放资源"
          ],
          "challenge": "将柱形图改成折线图并另存 output/line.png。",
          "solution": "plt.plot(names,values,marker=\"o\")\nplt.savefig(\"output/line.png\",dpi=150)\nplt.close()",
          "quiz": {
            "question": "正确保存图像的函数是？",
            "options": [
              "plt.show",
              "plt.savefig",
              "plt.xlabel"
            ],
            "answer": 1,
            "reason": "savefig 才会写入磁盘。"
          },
          "exam": "6.5.1",
          "minutes": 20,
          "id": "E3"
        },
        {
          "title": "模型预测与 API 调用",
          "concept": "本地模型用 predict；远程大模型 API 用 HTTP 请求，需配置地址、模型名和密钥。不要把私钥写入项目代码；使用环境变量，并处理断网/响应异常。",
          "code": "import os\nbase=os.getenv(\"OPENAI_BASE_URL\",\"\")\nmodel=os.getenv(\"OPENAI_MODEL\",\"\")\nkey=os.getenv(\"OPENAI_API_KEY\",\"\")\nif not all([base,model,key]):\n    print(\"未配置 API，先做离线数据分析\")\nelse:\n    print(\"已检测到配置，可进行联网调用（此示例不发送请求）\")",
          "steps": [
            "API 密钥从环境变量获取",
            "未配置时提供离线替代路径",
            "联网调用要考虑超时和响应解析"
          ],
          "challenge": "增加检查 API 基础地址是否以 http:// 或 https:// 开头。",
          "solution": "print(base.startswith((\"http://\",\"https://\")) if base else False)",
          "quiz": {
            "question": "API Key 应该放在哪里？",
            "options": [
              "公开代码里",
              "环境变量/安全配置",
              "写在图片标题里"
            ],
            "answer": 1,
            "reason": "避免把秘密密钥提交到仓库。"
          },
          "exam": "6.5.1",
          "minutes": 20,
          "id": "E4"
        },
        {
          "title": "RAG 检索、简单评测和性能",
          "concept": "RAG 先从资料检索，再让模型回答。入门可先实现 TF-IDF 检索，不必接大模型。性能测试要清楚计算总耗时与平均延迟。",
          "code": "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.metrics.pairwise import cosine_similarity\nimport time\ndocs=[\"图书馆周一开放\",\"实验室需预约\",\"食堂供应午餐\"]\nquery=\"图书馆几点开放\"\nt0=time.perf_counter()\nvec=TfidfVectorizer(analyzer=\"char\",ngram_range=(2,3))\nX=vec.fit_transform(docs)\nq=vec.transform([query])\nidx=cosine_similarity(q,X).argmax()\nprint(\"最相关:\",docs[idx])\nprint(\"耗时(秒):\",time.perf_counter()-t0)",
          "steps": [
            "中文可使用字符 n-gram",
            "相似度最高的文本并不保证答案一定正确",
            "总耗时除以调用次数是平均延迟"
          ],
          "challenge": "把 query 改为“需要预约实验室吗”，找出最相关段落。",
          "solution": "query=\"实验室是否预约\"\nprint(docs[cosine_similarity(vec.transform([query]),X).argmax()])",
          "quiz": {
            "question": "RAG 的检索步骤主要做什么？",
            "options": [
              "寻找与问题相关的资料",
              "直接训练显卡驱动",
              "删除所有文本"
            ],
            "answer": 0,
            "reason": "先找到证据，再组织答案。"
          },
          "exam": "6.5.3",
          "minutes": 20,
          "id": "E5"
        },
        {
          "title": "测试、README 与最终展示",
          "concept": "一个可复现的项目应包含环境说明、启动命令、输入输出样例、测试结果和失败兜底。实践中先跑通最小闭环，再优化效果。",
          "code": "from pathlib import Path\nrequired=[\"README.md\",\"output/chart.png\"]\nfor filename in required:\n    path=Path(filename)\n    print((\"通过\" if path.exists() else \"缺失\"),filename)\n# 请按你自己的练习目录修改 required 列表",
          "steps": [
            "用自动化检查而不是只靠肉眼",
            "README 说明如何重新运行",
            "确认预测输出、统计、图表、报告齐全"
          ],
          "challenge": "给检查脚本新增 output/line.png，并打印缺失文件列表。",
          "solution": "required.append(\"output/line.png\")\nmissing=[name for name in required if not Path(name).exists()]\nprint(\"缺失:\",missing)",
          "quiz": {
            "question": "可复现交付最重要的是？",
            "options": [
              "只有截图",
              "可运行代码、依赖、数据说明和结果文件",
              "只提供一段介绍"
            ],
            "answer": 1,
            "reason": "他人需要能按 README 重现运行与结果。"
          },
          "exam": "6.5.5",
          "minutes": 20,
          "id": "E6"
        }
      ]
    }
  ]
};
