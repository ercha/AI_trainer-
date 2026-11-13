window.BEGINNER_COURSE_EXTRAS={
  "version": 2,
  "lessons": {
    "A1": {
      "why": "读入图片后遇到 shape、dtype、像素值时，先知道它们是什么，才不会误把高度当宽度。",
      "terms": [
        {
          "name": "像素",
          "meaning": "一幅图最小的颜色采样单位；灰度图每个像素是一个 0～255 的数"
        },
        {
          "name": "数组",
          "meaning": "按行列组织的数据容器；灰度图通常有两个维度"
        },
        {
          "name": "uint8",
          "meaning": "无符号 8 位整数，范围 0～255；常用于存储普通图像"
        }
      ],
      "walkthrough": [
        "第 1 行导入 numpy 并起别名 np，之后调用 np.array 等函数。",
        "np.array 把二维列表转换为形状 (2,2) 的数组；每个嵌套列表代表一行。",
        "pixels.shape 返回高度与宽度；dtype 表示元素的存储类型。"
      ],
      "apis": [
        {
          "api": "np.array",
          "signature": "np.array(object, dtype=None)",
          "parameters": "object：输入列表；dtype：元素数据类型",
          "returns": "返回 ndarray",
          "tip": "uint8 不适合直接保存超过 255 的像素数值"
        },
        {
          "api": "np.zeros",
          "signature": "np.zeros(shape, dtype=float)",
          "parameters": "shape：各维长度；dtype：默认浮点类型",
          "returns": "给定形状的全零数组",
          "tip": "图像练习常明确写 dtype=np.uint8"
        }
      ],
      "expected": "将显示 2×2 的整数数组、shape=(2,2)、dtype=uint8；它并没有图像文件。",
      "pitfalls": [
        "把 shape=(2,3) 看成宽 2、高 3；二维数组按 (行,列) 排列。",
        "把 300 直接写入 uint8 像素；范围超出 0～255，会发生类型转换问题。"
      ],
      "levels": [
        "入门：修改示例右下角像素为 0，重新打印。",
        "巩固：创建 3×4 的灰度图并把第一行全部改成 255。",
        "挑战：创建形状 (5,6,3) 的彩色图，并解释最后一维。"
      ],
      "check": "能说出 shape、dtype 与灰度图和 BGR 彩色图的维度差别。"
    },
    "A2": {
      "why": "竞赛可能直接给带中文的图片文件名。读取失败若不检查 None，后面 resize/cvtColor 会连续报错。",
      "terms": [
        {
          "name": "路径",
          "meaning": "文件在电脑上的位置，可以是相对路径或绝对路径"
        },
        {
          "name": "解码",
          "meaning": "将 PNG/JPEG 的压缩字节还原为可操作的像素数组"
        },
        {
          "name": "BGR",
          "meaning": "OpenCV 彩色图默认的三个通道排列：蓝、绿、红"
        }
      ],
      "walkthrough": [
        "Path('练习图片.png') 指向当前工作目录的文件，而不是脚本本身所在目录。",
        "np.fromfile 以字节形式读取，cv2.imdecode 按图片格式解码，中文路径也适用。",
        "保存时 cv2.imencode 先生成 PNG 字节，再调用 .tofile 写入中文路径。"
      ],
      "apis": [
        {
          "api": "cv2.imdecode",
          "signature": "cv2.imdecode(buf, flags)",
          "parameters": "buf：uint8 字节数组；flags：cv2.IMREAD_COLOR / GRAYSCALE",
          "returns": "成功返回图像数组；失败可能返回 None",
          "tip": "在读取后检查 img is None"
        },
        {
          "api": "cv2.imencode",
          "signature": "cv2.imencode(ext, img)",
          "parameters": "ext：文件格式扩展名如 '.png'；img：数组",
          "returns": "返回 (成功标志, 字节缓冲区)",
          "tip": "一定先验证 ok 再执行 buf.tofile"
        }
      ],
      "expected": "若当前目录缺少『练习图片.png』，示例只会提示放入图片；创建文件后才会生成『保存结果.png』。",
      "pitfalls": [
        "文件不存在却直接访问 img.shape，会出现 AttributeError。",
        "把 JPEG 图片当作 PNG 保存只改文件名，不代表真实编码变了；要使用 .imencode('.png', img)。"
      ],
      "levels": [
        "入门：运行一次故意缺失图片的情况，观察保护提示。",
        "巩固：创建名为『中文路径测试.png』的测试图像，解码后打印 shape。",
        "挑战：将当前目录所有 PNG 批量复制到 output/ 并保留原文件名。"
      ],
      "check": "能使用中文路径读、写图片，并知道如何处理文件不存在的情况。"
    },
    "A3": {
      "why": "模型常要求固定输入尺寸，显示时常需要 RGB；相机图片与 Matplotlib 显示顺序不同。",
      "terms": [
        {
          "name": "尺寸",
          "meaning": "图像的宽度和高度；OpenCV resize 参数写 (宽,高)"
        },
        {
          "name": "颜色空间",
          "meaning": "表示颜色的方法，常用 BGR、RGB、HSV、灰度"
        },
        {
          "name": "边界填充",
          "meaning": "在图像四周补像素，避免卷积时图像边缘信息不足"
        }
      ],
      "walkthrough": [
        "img 是 80 行×120 列×3 通道。",
        "resize(img,(60,40)) 产生 40 行×60 列×3 通道。",
        "BGR2GRAY 后去掉颜色通道维；再分别补 5 像素得到 50 行×70 列。"
      ],
      "apis": [
        {
          "api": "cv2.resize",
          "signature": "cv2.resize(src, dsize, interpolation=cv2.INTER_LINEAR)",
          "parameters": "dsize：(宽,高)；interpolation：插值算法",
          "returns": "返回缩放后的图像",
          "tip": "shape 却按 (高,宽,通道) 输出"
        },
        {
          "api": "cv2.cvtColor",
          "signature": "cv2.cvtColor(src, code)",
          "parameters": "code：cv2.COLOR_BGR2GRAY / BGR2RGB / BGR2HSV",
          "returns": "返回新颜色空间图像",
          "tip": "使用 plt.imshow 显示 OpenCV 彩图前常需 BGR→RGB"
        }
      ],
      "expected": "预计打印 (80,120,3)、(40,60,3)、(40,60)、(50,70)。",
      "pitfalls": [
        "把 cv2.COLOR_RGB2GRAY 用在默认 BGR 输入上，颜色权重可能不符合预期。",
        "copyMakeBorder 的 top/bottom/left/right 次序与一般的 (x,y) 坐标混淆。"
      ],
      "levels": [
        "入门：将 120×80 图缩放为宽 100、高 50。",
        "巩固：分别生成 RGB、HSV、灰度数组，观察 shape。",
        "挑战：并排绘制原图与缩放图并添加标题、保存 PNG。"
      ],
      "check": "能解释 reshape 与 resize 的区别，以及 dsize 与 shape 顺序不一致的原因。"
    },
    "A4": {
      "why": "图像受到随机噪声影响时，先滤波再做边缘或阈值检测往往更稳定。",
      "terms": [
        {
          "name": "卷积核",
          "meaning": "在局部像素范围做运算的小窗口，如 3×3、5×5"
        },
        {
          "name": "椒盐噪声",
          "meaning": "随机出现的黑白孤立噪点"
        },
        {
          "name": "高斯权重",
          "meaning": "中心像素权重较高、远处较低的平滑方式"
        }
      ],
      "walkthrough": [
        "img = np.full 创建均匀灰色背景。",
        "设置中心像素为 255，模拟一个亮噪点。",
        "比较三种滤波下中心像素值，观察中值滤波消除孤立噪点的效果。"
      ],
      "apis": [
        {
          "api": "cv2.GaussianBlur",
          "signature": "cv2.GaussianBlur(src, ksize, sigmaX)",
          "parameters": "ksize：奇数尺寸元组；sigmaX：X方向标准差，0 表示自动推导",
          "returns": "返回平滑图",
          "tip": "(5,5),0 是常见写法，不是『滤波关闭』"
        },
        {
          "api": "cv2.medianBlur",
          "signature": "cv2.medianBlur(src, ksize)",
          "parameters": "ksize：奇数整数，不是 (5,5) 元组",
          "returns": "返回中值滤波图",
          "tip": "若写成 (5,5) 会发生参数类型错误"
        }
      ],
      "expected": "由于孤立亮噪点会被周围正常灰度覆盖，中值滤波中心结果常回到 120。",
      "pitfalls": [
        "把 GaussianBlur 的内核写成 (4,4)，常报尺寸须为正奇数。",
        "误把 blur 的 (5,5) 传给 medianBlur；后者要整数 5。"
      ],
      "levels": [
        "入门：分别使用三种核大小为 3 的滤波。",
        "巩固：给一张小图添加 10 个白色噪点，对比滤波结果。",
        "挑战：用 plt.subplots 绘制原图、均值、高斯、中值四宫格并保存。"
      ],
      "check": "能在任务中根据『椒盐噪声』联想到中值滤波，并说出 sigmaX=0 含义。"
    },
    "A5": {
      "why": "从彩色图片找到目标边界通常经过灰度、阈值或边缘、形态学清理的过程。",
      "terms": [
        {
          "name": "二值掩膜",
          "meaning": "只有两种值的图，通常用 0 和 255"
        },
        {
          "name": "边缘",
          "meaning": "像素亮度变化明显的轮廓线"
        },
        {
          "name": "开运算/闭运算",
          "meaning": "先腐蚀后膨胀一般去小白点；先膨胀后腐蚀一般填小黑洞"
        }
      ],
      "walkthrough": [
        "先构造灰度背景与亮色矩形。",
        "threshold 函数返回两个值，真正的掩膜是第二个。",
        "Canny 返回边缘图；morphologyEx 清理掩膜。"
      ],
      "apis": [
        {
          "api": "cv2.threshold",
          "signature": "cv2.threshold(src, thresh, maxval, type)",
          "parameters": "thresh：分界阈值；maxval：常用 255；type：THRESH_BINARY",
          "returns": "返回 (实际使用阈值, 图像)",
          "tip": "_,mask=... 不能只写 mask=cv2.threshold(...)"
        },
        {
          "api": "cv2.Canny",
          "signature": "cv2.Canny(image, threshold1, threshold2)",
          "parameters": "threshold1/2：低/高梯度阈值",
          "returns": "返回单通道边缘图",
          "tip": "阈值不是图像亮度阈值；和 threshold 功能不同"
        }
      ],
      "expected": "掩膜的独特取值通常是 [0,255]；边缘计数应大于 0。",
      "pitfalls": [
        "把 cv2.threshold 的二元返回值当图像传给 morphologyEx。",
        "把 0/1 的布尔数组不做 uint8 转换就直接进入一些 OpenCV 操作。"
      ],
      "levels": [
        "入门：修改阈值 127→200，再查看结果变化。",
        "巩固：先执行开运算，再执行闭运算，并保存掩膜图。",
        "挑战：对两种阈值执行 Canny 并用 Matplotlib 展示差异。"
      ],
      "check": "能清楚区分阈值分割的掩膜与 Canny 边缘图。"
    },
    "A6": {
      "why": "竞赛不仅要找出目标，还要画框、统计、生成图表并检查文件是否保存成功。",
      "terms": [
        {
          "name": "轮廓",
          "meaning": "像素区域外边缘的点序列"
        },
        {
          "name": "外接矩形",
          "meaning": "包含目标的最小轴对齐矩形，使用 x、y、w、h"
        },
        {
          "name": "交付物",
          "meaning": "任务书要求最终提交的文件，如 CSV、PNG、模型"
        }
      ],
      "walkthrough": [
        "cv2.findContours 返回轮廓列表和层级信息。",
        "cv2.boundingRect 的返回值代表左上角坐标和尺寸，不是右下角坐标。",
        "plt.savefig 把图写入 output/，并用 Path.exists 检查。"
      ],
      "apis": [
        {
          "api": "cv2.findContours",
          "signature": "cv2.findContours(image, mode, method)",
          "parameters": "image：二值图；mode：RETR_EXTERNAL；method：CHAIN_APPROX_SIMPLE",
          "returns": "返回 (contours, hierarchy)",
          "tip": "OpenCV 4 的常见解包形式是 contours,_"
        },
        {
          "api": "plt.savefig",
          "signature": "plt.savefig(fname, dpi=150, bbox_inches='tight')",
          "parameters": "fname：目标路径；dpi：输出分辨率",
          "returns": "写入 PNG 等文件",
          "tip": "仅调用 plt.show 不代表已保存"
        }
      ],
      "expected": "应识别 1 个矩形轮廓；输出目录出现 preview.png。",
      "pitfalls": [
        "找不到轮廓时直接访问 contours[0] 会报 IndexError。",
        "忘记创建 output/ 目录就保存文件，会抛出 FileNotFoundError。"
      ],
      "levels": [
        "入门：打印全部轮廓的 contourArea。",
        "巩固：给最大轮廓绘制绿色外接框，保存检测图。",
        "挑战：批量处理三张测试图，将目标数保存为 CSV。"
      ],
      "check": "能独立完成『读取→处理→统计→展示→保存→核验』整条流程。"
    },
    "B1": {
      "why": "每一道机器学习题都要先辨认『样本是什么、特征有哪些、预测目标是什么』，否则模型代码写得再对也可能用错数据。",
      "terms": [
        {
          "name": "DataFrame",
          "meaning": "带行和列标签的二维数据表"
        },
        {
          "name": "特征 X",
          "meaning": "用于预测的输入信息，可以是一列或多列"
        },
        {
          "name": "目标 y",
          "meaning": "已有的正确标签或连续数值，训练时用于比较"
        }
      ],
      "walkthrough": [
        "pd.DataFrame 用字典构造三行数据；字典键自动成为列名。",
        "df[['年龄','学习小时']] 返回形状 (3,2) 的特征表。",
        "df['通过'] 返回形状 (3,) 的单列目标 Series。"
      ],
      "apis": [
        {
          "api": "pd.read_csv",
          "signature": "pd.read_csv(filepath_or_buffer, encoding='utf-8')",
          "parameters": "filepath_or_buffer：CSV 文件路径；encoding：编码",
          "returns": "返回 DataFrame",
          "tip": "中文 Excel 导出 CSV 可能是 utf-8-sig，需要检查"
        },
        {
          "api": "DataFrame.drop",
          "signature": "df.drop(columns=['target'])",
          "parameters": "columns：要移除的列名列表",
          "returns": "返回删列后的表（默认不修改原表）",
          "tip": "X=df.drop(columns=['target']); y=df['target']"
        }
      ],
      "expected": "X 的 shape 为 (3,2)，y 的 shape 为 (3,)。",
      "pitfalls": [
        "拿 y 当作 X 的特征，会发生目标泄漏，得到虚高成绩。",
        "使用单层方括号选多列，例如 df['年龄','学习小时']，通常不是正确语法。"
      ],
      "levels": [
        "入门：打印 df.dtypes 和 df.isna().sum()。",
        "巩固：增加一列『作业次数』并重新创建 X。",
        "挑战：把 df 保存为 CSV，再读取并比较列名。"
      ],
      "check": "能用一句话解释每个表格字段属于输入特征、目标还是样本标识。"
    },
    "B2": {
      "why": "预处理不是随意清洗：填补缺失值的中位数和标准化均值必须由训练集学得，不能偷偷读取测试集信息。",
      "terms": [
        {
          "name": "缺失值 NaN",
          "meaning": "无法获得的数据，numpy 中常写 np.nan"
        },
        {
          "name": "拟合 fit",
          "meaning": "根据当前数据计算预处理参数/模型参数"
        },
        {
          "name": "数据泄漏",
          "meaning": "使用了预测时不应该知道的信息，导致评估失真"
        }
      ],
      "walkthrough": [
        "train_test_split 先随机划分 8:2 并根据 y 分层。",
        "SimpleImputer 的 fit_transform 在训练集上求中位数并填补。",
        "StandardScaler 再在训练集计算均值和标准差；测试集只能 transform。"
      ],
      "apis": [
        {
          "api": "train_test_split",
          "signature": "train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)",
          "parameters": "test_size：测试占比；random_state：固定随机；stratify：分层依据",
          "returns": "返回 X_train,X_test,y_train,y_test",
          "tip": "分类标签分层有助于稳定训练/测试类别比例"
        },
        {
          "api": "StandardScaler",
          "signature": "scaler.fit_transform(X_train) / scaler.transform(X_test)",
          "parameters": "fit_transform：学习后转换；transform：仅转换",
          "returns": "返回标准化数组",
          "tip": "测试集不能重新拟合"
        }
      ],
      "expected": "训练/测试 shape 应分别为 (8,1) 和 (2,1)，执行过程中不会出现 NaN。",
      "pitfalls": [
        "对全部 X 先 fit_transform 再 split，会把测试集统计信息泄漏进训练流程。",
        "在已标准化的 Xtr 上再次调用 imp.fit_transform，虽然通常不报错但已经不是原始数据处理逻辑。"
      ],
      "levels": [
        "入门：修改缺失值填补策略为 mean 并比较。",
        "巩固：尝试把 test_size 改为 0.3，打印两组标签分布。",
        "挑战：将 Imputer/Scaler/LogisticRegression 组合成 Pipeline。"
      ],
      "check": "能解释为什么训练集是 fit_transform、测试集只能 transform。"
    },
    "B3": {
      "why": "监督分类最基本的标准动作是『划分→训练→预测→评价』。先掌握这个流程，再换 SVM、KNN、随机森林。",
      "terms": [
        {
          "name": "分类",
          "meaning": "预测属于哪个类别，如猫/狗或通过/未通过"
        },
        {
          "name": "训练集",
          "meaning": "允许模型学习的数据"
        },
        {
          "name": "准确率",
          "meaning": "预测正确数量除以测试样本总数"
        }
      ],
      "walkthrough": [
        "load_iris(return_X_y=True) 获取无须下载的鸢尾花样本和类别。",
        "model.fit(Xtr,ytr) 学习参数；model.predict(Xte) 输出测试样本类别。",
        "accuracy_score(yte,pred) 比较预测和真实测试标签。"
      ],
      "apis": [
        {
          "api": "LogisticRegression",
          "signature": "LogisticRegression(max_iter=300)",
          "parameters": "max_iter：优化求解允许的最大迭代次数",
          "returns": "返回待拟合分类器",
          "tip": "虽然叫回归，但这里常用于分类"
        },
        {
          "api": "accuracy_score",
          "signature": "accuracy_score(y_true, y_pred)",
          "parameters": "y_true：真实标签；y_pred：预测类别",
          "returns": "返回 0～1 的准确率",
          "tip": "两个数组必须按同样顺序逐项对应"
        }
      ],
      "expected": "代码会输出 0～1 之间的测试集准确率；由于数据较简单通常较高。",
      "pitfalls": [
        "把 pred 当作 y_true，把 yte 当作预测结果；部分指标可能对称但不能养成反写习惯。",
        "只在训练数据上报告准确率，可能掩盖过拟合。"
      ],
      "levels": [
        "入门：打印 pred[:5] 与 yte[:5]。",
        "巩固：改成 KNN 和 SVC 对同一测试集比较结果。",
        "挑战：计算混淆矩阵并保存预测结果到 CSV。"
      ],
      "check": "能不查资料写出 fit、predict 与 accuracy_score 的基本用法。"
    },
    "B4": {
      "why": "当数据既有数字列又有文本类别列时，可以先使用 ColumnTransformer 分列处理，再由 Pipeline 接分类器。",
      "terms": [
        {
          "name": "Pipeline",
          "meaning": "将预处理器和模型串成有顺序的流水线"
        },
        {
          "name": "ColumnTransformer",
          "meaning": "按不同列选择不同处理方法并拼接结果"
        },
        {
          "name": "Precision/Recall/F1",
          "meaning": "预测为正的可靠性、找回正例的能力、两者调和平均"
        }
      ],
      "walkthrough": [
        "Pipeline 的每个元素是 (步骤名,处理器) 元组。",
        "先对 StandardScaler 调用 fit，然后把结果传给 SVC。",
        "classification_report 给出每类 precision、recall、f1-score 与 support。"
      ],
      "apis": [
        {
          "api": "Pipeline",
          "signature": "Pipeline([('scale', StandardScaler()), ('model', SVC())])",
          "parameters": "每步输入是 (自定义名称, sklearn 对象)；最后一步可为预测器",
          "returns": "返回可统一 fit/predict 的流水线",
          "tip": "步骤名称不是函数名，任取字符串但不要重复"
        },
        {
          "api": "ColumnTransformer",
          "signature": "ColumnTransformer([('num', num_pipeline, num_cols), ('cat', cat_pipeline, cat_cols)])",
          "parameters": "每一项 (名字, 转换器, 列选择器)",
          "returns": "组合数值与分类特征",
          "tip": "需要数据表列名时宜使用 Pandas DataFrame"
        }
      ],
      "expected": "输出每类 precision、recall、f1-score 和 support；可以比较模型而不手动处理 scaler。",
      "pitfalls": [
        "把 StandardScaler 不经独热编码直接用于字符串类别，通常报字符串转浮点失败。",
        "F1 不等于 accuracy，尤其在样本不平衡时两者可能差异很大。"
      ],
      "levels": [
        "入门：访问 pipe.named_steps['model'] 观察分类器。",
        "巩固：给示例增加 pd.DataFrame 的类别列，并用 OneHotEncoder 处理。",
        "挑战：使用 ColumnTransformer+Pipeline 完成数值/类别混合数据的分类。"
      ],
      "check": "能说明 Pipeline 是按顺序串联，ColumnTransformer 是按列分工。"
    },
    "B5": {
      "why": "分类回答『是哪类』，回归回答『是多少』。估价、温度和销售额预测都属于连续数值回归问题。",
      "terms": [
        {
          "name": "连续值",
          "meaning": "例如价格、温度，通常有很多可能的数值"
        },
        {
          "name": "RMSE",
          "meaning": "均方误差的平方根，单位与预测目标相同"
        },
        {
          "name": "R²",
          "meaning": "回归评价指标，1 代表完美拟合，也可能为负"
        }
      ],
      "walkthrough": [
        "make_regression 生成虚拟连续数值数据，无需外部文件。",
        "LinearRegression 拟合训练集，预测测试集。",
        "mean_squared_error 求平方误差平均值，np.sqrt 再开方得到 RMSE。"
      ],
      "apis": [
        {
          "api": "mean_squared_error",
          "signature": "mean_squared_error(y_true, y_pred)",
          "parameters": "y_true：真实数值；y_pred：预测数值",
          "returns": "返回均方误差 MSE",
          "tip": "RMSE=np.sqrt(MSE)"
        },
        {
          "api": "r2_score",
          "signature": "r2_score(y_true,y_pred)",
          "parameters": "按测试集真实值和预测值比较",
          "returns": "返回决定系数 R²",
          "tip": "R² 可能小于 0，不能机械限定在 0～1"
        }
      ],
      "expected": "会打印 RMSE（非负）和 R²；由于模拟数据有噪声，不一定达到 1。",
      "pitfalls": [
        "把回归输出 round 成整数后使用 accuracy_score，会误把连续问题当分类。",
        "比较不同模型时分别划分不同随机测试集，评价不公平。"
      ],
      "levels": [
        "入门：打印 5 组真实值与预测值。",
        "巩固：比较 LinearRegression 与 DecisionTreeRegressor。",
        "挑战：绘制真实值/预测值散点图和 y=x 参考线。"
      ],
      "check": "能选对回归任务的 RMSE、R²，而不是 accuracy。"
    },
    "B6": {
      "why": "聚类不需要人为标签，用样本之间的距离找分组；k 的选择可使用轮廓系数辅助，最后还要保存模型供重用。",
      "terms": [
        {
          "name": "无监督学习",
          "meaning": "训练时没有标准 y 标签，算法只看 X 的分布"
        },
        {
          "name": "聚类中心",
          "meaning": "KMeans 每个分组的代表性中心"
        },
        {
          "name": "轮廓系数",
          "meaning": "描述样本与本簇及其他簇的相对距离，可用于比较 k"
        }
      ],
      "walkthrough": [
        "make_blobs 生成 100 个分为 3 簇的二维点。",
        "fit_predict(X) 先训练 KMeans，再对每个样本给出聚类编号。",
        "silhouette_score 计算结果；joblib.dump 保存模型到 pkl 文件。"
      ],
      "apis": [
        {
          "api": "KMeans",
          "signature": "KMeans(n_clusters=3, random_state=42, n_init=10)",
          "parameters": "n_clusters：簇数；n_init：初始化尝试次数",
          "returns": "返回聚类器",
          "tip": "聚类编号 0/1/2 不等同于真实业务标签"
        },
        {
          "api": "silhouette_score",
          "signature": "silhouette_score(X, labels)",
          "parameters": "X：原始特征；labels：各样本的簇编号",
          "returns": "返回 -1～1 的系数（在适用条件下）",
          "tip": "需至少两个有效簇，单簇会报错"
        }
      ],
      "expected": "输出轮廓系数和保存 kmeans_model.pkl；系数通常为正。",
      "pitfalls": [
        "对只有一个聚类标签的数据计算 silhouette_score，会报 ValueError。",
        "把 n_clusters=3 理解为 3 个分类答案；无监督模型没有 y_test。"
      ],
      "levels": [
        "入门：用 K=2、3、4 分别计算轮廓系数。",
        "巩固：绘制聚类散点图，按 labels 设置颜色。",
        "挑战：用 joblib.load 恢复模型，预测两个新样本所属簇。"
      ],
      "check": "能解释聚类和分类的区别，并知道何时用 silhouette_score。"
    },
    "C1": {
      "why": "深度学习最容易被忽视的是张量 shape 和 device：模型和输入必须位于相同设备。先让 CPU 代码跑通，再使用 GPU 加速。",
      "terms": [
        {
          "name": "Tensor",
          "meaning": "PyTorch 的多维数值数组，支持梯度计算"
        },
        {
          "name": "device",
          "meaning": "张量存储及计算的位置，例如 cpu 或 cuda"
        },
        {
          "name": "batch",
          "meaning": "一次交给模型处理的样本组"
        }
      ],
      "walkthrough": [
        "先检查 torch.cuda.is_available 是否能使用 NVIDIA CUDA。",
        "torch.device 用于构建实际设备，torch.tensor(..., device=device) 在指定设备创建张量。",
        "x.mean() 返回张量元素均值，print(x.shape) 检查矩阵行列。"
      ],
      "apis": [
        {
          "api": "torch.cuda.is_available",
          "signature": "torch.cuda.is_available()",
          "parameters": "无参数；检查 PyTorch CUDA 能否实际使用",
          "returns": "布尔值 True/False",
          "tip": "nvidia-smi 识别到显卡，不代表对应 PyTorch wheel 可用"
        },
        {
          "api": "torch.zeros",
          "signature": "torch.zeros(shape, device=device, dtype=torch.float32)",
          "parameters": "shape：维度；device：运算设备；dtype：元素类型",
          "returns": "全零张量",
          "tip": "需要和模型参数放同一个 device"
        }
      ],
      "expected": "输出设备 cpu 或 cuda、张量 shape=(2,2) 和平均值 2.5。",
      "pitfalls": [
        "CPU 模型遇到 CUDA Tensor，通常报设备不一致错误。",
        "把 torch.cuda.is_available 为 False 当成无法学习 PyTorch；绝大多数入门代码 CPU 就能跑。"
      ],
      "levels": [
        "入门：创建形状 (2,3) 的全零 float32 Tensor。",
        "巩固：把 Tensor 调用 .cpu().numpy() 转成 NumPy。",
        "挑战：在有 CUDA 的机器上比较 CPU 与 GPU 的矩阵运算结果。"
      ],
      "check": "能解释 Tensor shape、dtype、device 三个常见属性。"
    },
    "C2": {
      "why": "神经网络实际上是多层数学运算。建立最小的分类网络，先观察输入与 logits 的形状，再讨论损失函数。",
      "terms": [
        {
          "name": "神经元/层",
          "meaning": "nn.Linear 定义可学习的线性变换"
        },
        {
          "name": "logits",
          "meaning": "分类模型最后一层未经 softmax 的原始得分"
        },
        {
          "name": "交叉熵",
          "meaning": "分类训练中衡量预测分数与正确类别差异的损失"
        }
      ],
      "walkthrough": [
        "x=torch.randn(4,3) 模拟 4 个 3 维样本。",
        "nn.Sequential 将 Linear、ReLU 和 Linear 按顺序串接。",
        "输出 logits=(4,2)，CrossEntropyLoss 读取每行的正确类别索引。"
      ],
      "apis": [
        {
          "api": "nn.Linear",
          "signature": "nn.Linear(in_features, out_features)",
          "parameters": "in_features：输入特征数；out_features：输出特征数",
          "returns": "带可学习参数的线性层",
          "tip": "上一层的 out_features 必须等于下一层 in_features"
        },
        {
          "api": "nn.CrossEntropyLoss",
          "signature": "nn.CrossEntropyLoss()(logits, class_index)",
          "parameters": "logits：形状 (N,C)；class_index：形状 (N,)，整数类别",
          "returns": "标量损失 Tensor",
          "tip": "不要在 logits 前额外调用 softmax"
        }
      ],
      "expected": "打印 logits 形状 (4,2)，损失为一个非负标量。",
      "pitfalls": [
        "把 target 变成形状 (N,1) 或浮点类别，常发生形状/类型错误。",
        "把最后一层输出改成 3 却忘记设置正确类别范围及目标。"
      ],
      "levels": [
        "入门：将隐藏层 8 改为 16。",
        "巩固：打印 net[0].weight.shape 和 bias.shape。",
        "挑战：将类别数改为 3，准备正确标签再计算交叉熵。"
      ],
      "check": "能区分 logits、概率和类别标签。"
    },
    "C3": {
      "why": "掌握训练循环比记忆复杂 CNN 网络更重要。每轮训练有固定的五步，不可遗漏 backward 或 step。",
      "terms": [
        {
          "name": "epoch",
          "meaning": "把整个训练数据遍历一遍"
        },
        {
          "name": "梯度",
          "meaning": "损失对参数变化率的估计，决定更新方向"
        },
        {
          "name": "优化器",
          "meaning": "根据梯度调整网络参数的算法，如 SGD/Adam"
        }
      ],
      "walkthrough": [
        "x 与 y 构造线性映射 y=2x+1 的训练数据。",
        "opt.zero_grad(); loss=...; loss.backward(); opt.step() 是固定循环。",
        "随着 epoch 增加，loss 一般逐渐降低。"
      ],
      "apis": [
        {
          "api": "optimizer.zero_grad",
          "signature": "optimizer.zero_grad()",
          "parameters": "清零上一轮梯度",
          "returns": "无返回值",
          "tip": "梯度默认累积；训练前应清零"
        },
        {
          "api": "loss.backward",
          "signature": "loss.backward()",
          "parameters": "对当前标量损失反向传播",
          "returns": "写入参数 .grad",
          "tip": "这一步并不直接更新参数；随后还要 optimizer.step"
        }
      ],
      "expected": "100 次训练结束后输出一个 MSE，通常比初始值小。",
      "pitfalls": [
        "只调用 backward 不调用 optimizer.step，权重不会更新。",
        "用 net.eval() 替代零梯度和优化器更新，无法训练。"
      ],
      "levels": [
        "入门：打印首轮和最后一轮损失。",
        "巩固：换用 torch.optim.Adam 并比较收敛。",
        "挑战：记录每个 epoch 的 loss，画折线图保存训练曲线。"
      ],
      "check": "能不参考答案写出训练五步：zero_grad→前向→loss→backward→step。"
    },
    "C4": {
      "why": "竞赛 CNN 题大量报错来自 NCHW 形状、卷积核和全连接维度算错。先学会手算每层输出。",
      "terms": [
        {
          "name": "NCHW",
          "meaning": "批量 N、通道 C、高 H、宽 W 的 Tensor 维序"
        },
        {
          "name": "卷积",
          "meaning": "用卷积核在图像上提取局部特征"
        },
        {
          "name": "池化",
          "meaning": "缩小图像空间尺度；最大池化保留局部最强响应"
        }
      ],
      "walkthrough": [
        "输入形状 (2,1,20,20)。",
        "Conv2d(1,8,3) 默认无 padding：20-3+1=18。",
        "MaxPool2d(2) 使 18×18→9×9；Flatten 得 8×9×9=648，Linear 映射到 10 类。"
      ],
      "apis": [
        {
          "api": "nn.Conv2d",
          "signature": "nn.Conv2d(in_channels, out_channels, kernel_size, stride=1, padding=0)",
          "parameters": "通道数、核大小、步长、填充",
          "returns": "卷积后特征图",
          "tip": "输出尺寸 floor((H+2P-K)/S)+1（不考虑膨胀）"
        },
        {
          "api": "nn.Flatten",
          "signature": "nn.Flatten(start_dim=1)",
          "parameters": "start_dim=1：保留 batch 维",
          "returns": "将 (N,C,H,W) 变 (N,C×H×W)",
          "tip": "接 Linear 前须计算展平后的维度"
        }
      ],
      "expected": "网络输出形状 (2,10)；改 batch 为 5 则变 (5,10)。",
      "pitfalls": [
        "Linear(8*10*10,10) 会造成矩阵尺寸不匹配 RuntimeError。",
        "把 OpenCV 的 HWC 彩图直接交给 CNN，通常需要转换为 NCHW。"
      ],
      "levels": [
        "入门：手算每层的形状，再调用 print 验证。",
        "巩固：换 5×5 卷积核，重新计算 Linear 输入维度。",
        "挑战：用两个卷积池化块搭建 20×20 手写数字分类网络。"
      ],
      "check": "给定 NCHW=(8,1,20,20) 能算出该模型的最终输出 (8,10)。"
    },
    "C5": {
      "why": "测试模型时不应该再更新权重，且 Dropout/BatchNorm 在训练和预测时行为不同；保存权重需要能重新加载验证。",
      "terms": [
        {
          "name": "state_dict",
          "meaning": "模型可学习参数等状态的字典"
        },
        {
          "name": "eval 模式",
          "meaning": "预测/验证模式，影响 Dropout 和 BatchNorm 等层"
        },
        {
          "name": "no_grad",
          "meaning": "暂停构建梯度计算图，节省验证内存"
        }
      ],
      "walkthrough": [
        "nn.Linear(3,2) 创建最小模型。",
        "net.eval(); with torch.no_grad() 在无梯度记录下预测。",
        "torch.save 保存参数字典，重新建同结构网络后 load_state_dict 恢复。"
      ],
      "apis": [
        {
          "api": "torch.save",
          "signature": "torch.save(obj, f)",
          "parameters": "obj：通常是 model.state_dict()；f：保存路径",
          "returns": "写入权重文件",
          "tip": "保存 state_dict 更方便部署及版本控制"
        },
        {
          "api": "torch.load",
          "signature": "torch.load(file, map_location='cpu', weights_only=True)",
          "parameters": "map_location：目标设备；weights_only：安全加载常规权重",
          "returns": "返回状态字典",
          "tip": "只加载来自可信来源的模型文件"
        }
      ],
      "expected": "预测形状为 (4,2)；demo.pt 文件保存成功。",
      "pitfalls": [
        "更换网络结构后 load_state_dict 会因为 key 或形状不匹配而报错。",
        "只写 torch.save(model) 会把整个对象结构一并序列化，不推荐作为入门默认方式。"
      ],
      "levels": [
        "入门：打印模型 state_dict 的键。",
        "巩固：比较加载前后同一输入的输出，使用 torch.allclose。",
        "挑战：保存 best_model.pt 并在 CPU 上加载之前 GPU 训练的权重。"
      ],
      "check": "能独立解释为什么使用 model.eval() 和 torch.no_grad()。"
    },
    "C6": {
      "why": "实际运行 ResNet18 的冻结、替换分类头、单批次更新，再计算检测框 IoU。切记随机骨干不等于真正的预训练模型。",
      "terms": [
        {
          "name": "迁移学习",
          "meaning": "复用已有模型学到的权重，通常替换最后一层"
        },
        {
          "name": "检测框 xyxy",
          "meaning": "左上角 (x1,y1) 和右下角 (x2,y2) 的坐标"
        },
        {
          "name": "IoU",
          "meaning": "交集面积 / 并集面积，是检测和分割的重要重合度指标"
        }
      ],
      "walkthrough": [
        "weights=None 创建随机初始化网络结构；冻结全部参数后仍需替换分类头。",
        "fc 替换为 2 类输出，优化器只更新 model.fc.parameters()。",
        "model.eval() 保持 BatchNorm 统计固定；即使在 eval 状态也能对 fc 求梯度，本示例仅演示冻结机制。",
        "两个 4×4 框交集为 2×2，IoU=4/(16+16-4)=1/7。"
      ],
      "apis": [
        {
          "api": "torchvision.models.resnet18",
          "signature": "models.resnet18(weights=None)",
          "parameters": "weights=None 表示随机初始化，不是预训练！",
          "returns": "返回 ResNet18 网络结构",
          "tip": "迁移学习必须有真实加载的预训练权重才叫使用已学知识"
        },
        {
          "api": "requires_grad",
          "signature": "parameter.requires_grad=False",
          "parameters": "False：冻结该参数梯度",
          "returns": "禁止训练该参数",
          "tip": "替换分类头后重新选择可训练参数给优化器"
        }
      ],
      "expected": "显示可训练参数只有 fc.weight、fc.bias；分类输出 (2,2)；IoU 约 0.142857。注意这不是具有实际迁移效果的预训练模型。",
      "pitfalls": [
        "weights=None 只创建结构，不包含预训练知识。",
        "冻结参数后忘记重新创建 optimizer，可能导致优化器更新了错误参数。"
      ],
      "levels": [
        "入门：手算例子 IoU=1/7。",
        "巩固：让 box_b 与 box_a 重合，观察 IoU=1。",
        "挑战：写一个计算两个 xyxy 框 IoU 的可重用函数。"
      ],
      "check": "能区分图像分类、检测、分割，以及 weights=None 的真实含义。"
    },
    "D1": {
      "why": "自然语言处理最先遇到的是字符串和编码。中文没有天然空格，通常需要分词或字符级表示。",
      "terms": [
        {
          "name": "字符串 str",
          "meaning": "Python 处理文本的类型，支持切片、strip、replace"
        },
        {
          "name": "分词",
          "meaning": "把一句话拆成有意义的词列表"
        },
        {
          "name": "停用词",
          "meaning": "如『的、了』等常在特定任务中不提供明显区分信息的词"
        }
      ],
      "walkthrough": [
        "strip() 删除原句前后空格，replace('。','') 移除句末符号。",
        "jieba.cut 返回可迭代对象，因此用 list 包装查看分词结果。",
        "没有 jieba 时例子只提示安装额外依赖，不中断其它模块。"
      ],
      "apis": [
        {
          "api": "jieba.cut",
          "signature": "jieba.cut(sentence, cut_all=False)",
          "parameters": "sentence：中文句子；cut_all=False：精确模式",
          "returns": "返回可迭代分词结果",
          "tip": "分词结果可能受词典影响，需实际检查"
        },
        {
          "api": "str.strip",
          "signature": "text.strip()",
          "parameters": "默认清除首尾空白字符",
          "returns": "返回新字符串",
          "tip": "不会改变原始字符串变量，需重新赋值"
        }
      ],
      "expected": "会输出没有首尾空格和句号的文本，并列出若干中文词。",
      "pitfalls": [
        "把 jieba.cut 结果直接调用 .append，实际上它可能是生成器而非列表。",
        "处理读取文件时没有指定编码，含中文文本会出现乱码或解码错误。"
      ],
      "levels": [
        "入门：将标点、换行与空格从输入中清理。",
        "巩固：构建 stopwords 集合，过滤停用词。",
        "挑战：读取 UTF-8 文本文件并逐行分词，统计高频词。"
      ],
      "check": "能从文本原文得到一个过滤空白与停用词的词列表。"
    },
    "D2": {
      "why": "把词变成数字是传统 NLP 的第一步。TF-IDF 并不是深度学习，而是一种词语特征权重算法。",
      "terms": [
        {
          "name": "词袋",
          "meaning": "统计词是否出现及出现多少次，不考虑顺序"
        },
        {
          "name": "TF-IDF",
          "meaning": "同时考虑词在本文中的频率与跨文档稀有程度"
        },
        {
          "name": "稀疏矩阵",
          "meaning": "大多数位置为 0 的矩阵，能节省存储空间"
        }
      ],
      "walkthrough": [
        "TfidfVectorizer 在训练文本中建立词表。",
        "fit_transform 同时学词表并把文章转换为矩阵。",
        "get_feature_names_out 显示词表；X.shape 是 (文章数,词数)。"
      ],
      "apis": [
        {
          "api": "TfidfVectorizer",
          "signature": "TfidfVectorizer(max_features=None, ngram_range=(1,1))",
          "parameters": "max_features：最大词数；ngram_range：考虑的 n-gram 范围",
          "returns": "返回向量器；fit_transform 返回稀疏矩阵",
          "tip": "中文已按空格分好词时可直接使用默认分词器"
        },
        {
          "api": "fit_transform",
          "signature": "vectorizer.fit_transform(texts)",
          "parameters": "texts：字符串列表",
          "returns": "返回数值特征矩阵",
          "tip": "新文本只需 transform，不能重新 fit"
        }
      ],
      "expected": "词表会包含足球、体育、计算机等词；矩阵行数等于文本数 3。",
      "pitfalls": [
        "向量化训练与测试分别 fit，导致词表排列不一致。",
        "未分词的中文直接用默认按空格/词形的 tokenizer，得到的词表可能不符合预期。"
      ],
      "levels": [
        "入门：调用 X.toarray() 观察数字矩阵。",
        "巩固：把 ngram_range 改为 (1,2)，比较列数。",
        "挑战：使用 TfidfVectorizer(analyzer='char',ngram_range=(2,3)) 处理未分词中文。"
      ],
      "check": "能解释为什么样本数决定矩阵行数，而词表大小决定列数。"
    },
    "D3": {
      "why": "文本分类与机器学习模块 B 的分类流程一致；区别主要是输入为文字，必须先向量化。",
      "terms": [
        {
          "name": "文本标签",
          "meaning": "例如体育=0、科技=1"
        },
        {
          "name": "向量化器",
          "meaning": "把新文本用与训练时一致的词表映射到数字"
        },
        {
          "name": "误分类",
          "meaning": "模型预测标签与真实标签不一致的样本"
        }
      ],
      "walkthrough": [
        "texts 和 y 定义四条简短训练语句及类别。",
        "TfidfVectorizer 和 LogisticRegression 用 Pipeline 顺序连接。",
        "pipe.fit 训练；predict 对『足球进球』『电脑算法』输出类别。"
      ],
      "apis": [
        {
          "api": "Pipeline",
          "signature": "Pipeline([('tfidf', TfidfVectorizer()),('clf', LogisticRegression())])",
          "parameters": "一个向量化步骤 + 一个分类器步骤",
          "returns": "返回统一预测器",
          "tip": "训练/预测会自动复用相同词表"
        },
        {
          "api": "classification_report",
          "signature": "classification_report(y_true,y_pred,zero_division=0)",
          "parameters": "输入真实/预测标签；zero_division 控制分母为 0 的处理",
          "returns": "返回文本形式指标报告",
          "tip": "正式评价必须划分独立测试集"
        }
      ],
      "expected": "输出一个长度为 2 的预测类别数组，通常在训练词相近的样本上与预期一致。",
      "pitfalls": [
        "只有 4 句训练文字，结果不是可泛化真实模型；不要用示例成绩评价商业效果。",
        "在训练集上评估再说模型达到 100% 准确率，缺少测试意义。"
      ],
      "levels": [
        "入门：修改预测语句为『体育 球队 比赛』。",
        "巩固：加入另外两条文本和标签，预测新句子。",
        "挑战：准备 20 条样本，按 8:2 分层划分并计算 F1。"
      ],
      "check": "能从零搭建 TF-IDF + 逻辑回归分类 Pipeline。"
    },
    "D4": {
      "why": "文本任务除了分类还有发现隐藏主题、词相似度与实体抽取。先从可视的词袋主题概率理解无监督 NLP。",
      "terms": [
        {
          "name": "主题模型",
          "meaning": "从多篇文档挖掘潜在词语分布的无监督模型"
        },
        {
          "name": "LDA",
          "meaning": "基于概率分布的主题模型，这里是 LatentDirichletAllocation"
        },
        {
          "name": "命名实体",
          "meaning": "人、地、机构等专有名称，NER 任务要识别其类型"
        }
      ],
      "walkthrough": [
        "CountVectorizer 把每条空格分词的句子转为词频矩阵。",
        "LDA 设置 n_components=2，拟合这组小语料的主题分布。",
        "fit_transform 的输出每行包含该文档在 2 个主题上的概率。"
      ],
      "apis": [
        {
          "api": "CountVectorizer",
          "signature": "CountVectorizer(max_features=1500)",
          "parameters": "max_features：限制词表规模",
          "returns": "返回文本词频矩阵",
          "tip": "与 TF-IDF 不同，词频不会先做 TF-IDF 权重"
        },
        {
          "api": "LatentDirichletAllocation",
          "signature": "LatentDirichletAllocation(n_components=2, random_state=42)",
          "parameters": "n_components：主题数量",
          "returns": "返回可拟合 LDA 对象",
          "tip": "主题编号是无监督结果，不代表人工标注类别"
        }
      ],
      "expected": "输出主题概率矩阵 (4,2)，每行大致加和为 1。",
      "pitfalls": [
        "把 LDA 主题分配当成准确的新闻类别标签；主题没有自动命名。",
        "在极小样本上得到的主题结构不稳定，只用来理解 API。"
      ],
      "levels": [
        "入门：打印第一条文本的两个主题概率。",
        "巩固：用 lda.components_ 找每个主题权重最大的 3 个词。",
        "挑战：将新闻文本和主主题编号保存为 CSV。"
      ],
      "check": "能说明 CountVectorizer 与 TfidfVectorizer 的差别，以及主题模型不需要 y 标签。"
    },
    "D5": {
      "why": "通过一次真实 LSTM 训练理解为什么模型输出常为二维 (batch,vocab)，以及如何安全交给 NumPy 概率采样。",
      "terms": [
        {
          "name": "logits",
          "meaning": "模型输出的原始分数，可正可负，不保证总和为 1"
        },
        {
          "name": "softmax",
          "meaning": "把一组分数变成非负且和为 1 的概率"
        },
        {
          "name": "采样",
          "meaning": "根据概率随机挑选下一个字符/词的索引"
        }
      ],
      "walkthrough": [
        "Embedding(4,8) 把 4 种符号编码为 8 维向量；LSTM 的 batch_first=True 接收 (batch,seq,feature)。",
        "每次迭代执行 zero_grad→forward→CrossEntropyLoss→backward→step。",
        "X[:1] 得到一个样本，网络输出 logits 形状为 (1,4)。",
        "softmax 沿最后一维生成概率；probabilities[0] 去掉 batch 维后转 NumPy。",
        "np.random.choice 使用长度为 4 的一维概率 p 采样一个符号索引。"
      ],
      "apis": [
        {
          "api": "np.random.choice",
          "signature": "np.random.choice(a, size=None, replace=True, p=None)",
          "parameters": "a：候选索引数/数组；p：对应的一维概率数组",
          "returns": "返回样本索引或样本数组",
          "tip": "p 一定要一维、非负、总和近似等于 1"
        },
        {
          "api": "softmax",
          "signature": "torch.softmax(logits, dim=-1)",
          "parameters": "dim=-1：在最后一维按类别归一化",
          "returns": "返回与 logits 同 shape 的概率张量",
          "tip": "NumPy 用 np.exp(x-x.max()) 再除总和也可"
        }
      ],
      "expected": "输出 logits=(1,4)，概率 shape=(4,)，总和约 1，采样索引为 0～3。训练损失随随机初始化及硬件可能略有差异。",
      "pitfalls": [
        "直接把 (1,4) 的 probabilities 传入 choice，会报 p must be 1-dimensional。",
        "将 logits 当概率传入 p：logits 可能为负或总和不为 1。"
      ],
      "levels": [
        "入门：打印 logits.shape、logits[0].shape、probs.sum()。",
        "巩固：将类别扩展到 5 并执行 100 次采样，统计频率。",
        "挑战：用 torch.nn.LSTM 输出一个 batch 的 logits，再 softmax 和采样。"
      ],
      "check": "遇到二维预测结果时能先取单条结果并归一化，再传给 np.random.choice。"
    },
    "D6": {
      "why": "验证 Transformer 前向传播，再对相同参考与候选序列计算标准 BLEU-2 和基于 LCS 的 ROUGE-L。",
      "terms": [
        {
          "name": "Transformer",
          "meaning": "借助注意力机制处理序列关系的架构"
        },
        {
          "name": "BLEU",
          "meaning": "机器翻译常用的 n-gram 匹配指标"
        },
        {
          "name": "ROUGE-L",
          "meaning": "利用最长公共子序列衡量摘要和参考文本的重合度"
        }
      ],
      "walkthrough": [
        "nn.Transformer(d_model=8,nhead=2) 使用随机输入，仅演示前向传播，输出 (2,2,8)。",
        "nltk.sentence_bleu 以参考列表、预测列表和权重 (0.5,0.5) 计算 BLEU-2。",
        "lcs_length 使用动态规划找到公共子序列，顺序不同会改变结果。",
        "使用 LCS 长度计算 ROUGE-L precision、recall 与 F1。"
      ],
      "apis": [
        {
          "api": "sentence_bleu",
          "signature": "sentence_bleu([reference_tokens], hypothesis_tokens, weights=(0.5,0.5))",
          "parameters": "reference_tokens：参考词序列列表；hypothesis_tokens：预测词序列",
          "returns": "返回 BLEU 分数",
          "tip": "短句常用 nltk.translate.bleu_score.SmoothingFunction"
        },
        {
          "api": "max length of common subsequence",
          "signature": "LCS(reference, prediction)",
          "parameters": "两个有顺序的词列表",
          "returns": "最长公共子序列长度",
          "tip": "ROUGE-L 不能简单地用 set 求交集代替"
        }
      ],
      "expected": "Transformer 输出 (2,2,8)；BLEU-2 为 0～1 的数；ROUGE-L F1 约 0.6667。这不是训练完成的翻译模型。",
      "pitfalls": [
        "把随机 Transformer 的输出当作有效翻译结果。",
        "把无序集合交集当作 ROUGE-L，会失去词语顺序信息。"
      ],
      "levels": [
        "入门：手算示例的精确率与召回率。",
        "巩固：安装 nltk 后用 sentence_bleu 计算 BLEU-2。",
        "挑战：实现最长公共子序列 LCS，再计算简化 ROUGE-L F1。"
      ],
      "check": "能区分模型架构、模型输出，以及 BLEU/ROUGE 各自评价用途。"
    },
    "E1": {
      "why": "模块 E 分值高但不是一上来训练大模型；首先把需求写成『输入→处理→输出→验收』表，明确可交付成果。",
      "terms": [
        {
          "name": "输入",
          "meaning": "项目使用的数据与配置来源"
        },
        {
          "name": "输出",
          "meaning": "程序产出的 CSV、PNG、Markdown、模型等文件"
        },
        {
          "name": "验收标准",
          "meaning": "用于判断需求是否真的实现的可检查条件"
        }
      ],
      "walkthrough": [
        "required 文件列表就是一份最小交付清单。",
        "Path.exists() 检查真实磁盘文件，不只是程序变量是否生成。",
        "显示缺失清单可让项目在提交前自查。"
      ],
      "apis": [
        {
          "api": "Path.exists",
          "signature": "Path(path).exists()",
          "parameters": "path：文件或目录的位置",
          "returns": "True/False",
          "tip": "存在不代表内容正确，还应检查大小/列名等"
        },
        {
          "api": "Path.mkdir",
          "signature": "Path('output').mkdir(parents=True, exist_ok=True)",
          "parameters": "parents：创建父目录；exist_ok：已存在不报错",
          "returns": "创建目录",
          "tip": "建议在写文件前调用"
        }
      ],
      "expected": "首次运行如果文件还没生成，会显示『尚未生成』，这不是程序错误。",
      "pitfalls": [
        "认为只要运行了 savefig 就必然有文件；路径和权限可能失败。",
        "需求中有 xlsx 但代码只生成 csv，仍然不满足交付要求。"
      ],
      "levels": [
        "入门：创建 output/ 目录并打印位置。",
        "巩固：对 CSV、PNG、MD 逐一检查 exists 和大小。",
        "挑战：构建一份任务需求表，增加文件格式、文件名和验收方法列。"
      ],
      "check": "可以自己写出项目的最小输入/输出/验收清单。"
    },
    "E2": {
      "why": "Python 的 JSON 和 Pandas DataFrame 是常见数据源。先把数据字段清理干净，再计算 GMV、订单数等指标。",
      "terms": [
        {
          "name": "JSON",
          "meaning": "用对象、数组存储字段和数据的文本格式"
        },
        {
          "name": "类型转换",
          "meaning": "把价格字符串变成数字后才能用于乘法"
        },
        {
          "name": "GMV",
          "meaning": "成交总额，这里用价格×数量求和作为示例"
        }
      ],
      "walkthrough": [
        "records 是商品字典列表，每个字典作为 DataFrame 一行。",
        "pd.to_numeric 将价格字符串转换为可计算数值。",
        "df['销售额'] 创建新列，再调用 .sum() 计算总销售额。"
      ],
      "apis": [
        {
          "api": "pd.to_numeric",
          "signature": "pd.to_numeric(arg, errors='coerce')",
          "parameters": "arg：输入列；errors='coerce' 使无效值变 NaN",
          "returns": "数值 Series",
          "tip": "非法值转 NaN 后仍要决定怎么填补或删除"
        },
        {
          "api": "to_csv",
          "signature": "df.to_csv('cleaned.csv', index=False, encoding='utf-8-sig')",
          "parameters": "index=False：不多写行索引；encoding：中文 Excel 兼容",
          "returns": "写 CSV 文件",
          "tip": "数据清洗后要确认文件真实存在"
        }
      ],
      "expected": "两条数据销售额分别为 40 和 90，总额 130。",
      "pitfalls": [
        "价格字符串直接乘数量，可能重复字符串而不是数学乘法。",
        "to_numeric 后存在 NaN，却忽略缺失值继续汇总会影响质量。"
      ],
      "levels": [
        "入门：在 rows 中增加第三条商品。",
        "巩固：构造一个非法价格字符串，查看 to_numeric 产生的 NaN。",
        "挑战：读取真实 JSON 文件，按品类分组并输出 sales_by_category.csv。"
      ],
      "check": "能完成 JSON→DataFrame→类型清洗→新字段→CSV 的流程。"
    },
    "E3": {
      "why": "Matplotlib 是今年多道题的交付考点。图表必须能保存、标注完整，还要确认中文显示/字体。",
      "terms": [
        {
          "name": "Figure",
          "meaning": "整张图像画布"
        },
        {
          "name": "Axes",
          "meaning": "图中的绘图区，可设置坐标轴标题"
        },
        {
          "name": "dpi",
          "meaning": "保存图像的像素密度设置，常用 150 或 300"
        }
      ],
      "walkthrough": [
        "plt.bar 生成按类别分布的柱形图。",
        "title、xlabel、ylabel 增加解释，让阅卷人能理解内容。",
        "tight_layout 防止挤压；savefig 写入 PNG；close 关闭图像释放资源。"
      ],
      "apis": [
        {
          "api": "plt.savefig",
          "signature": "plt.savefig(fname, dpi=150, bbox_inches='tight')",
          "parameters": "fname：输出文件；dpi：图像清晰度；bbox_inches：边距调整",
          "returns": "写入图像文件",
          "tip": "保存前先 mkdir 创建目录"
        },
        {
          "api": "plt.subplots",
          "signature": "fig,ax=plt.subplots(1,2,figsize=(10,4))",
          "parameters": "行数、列数、画布尺寸",
          "returns": "返回 Figure 与 Axes",
          "tip": "多图建议使用 ax.plot、ax.bar、ax.set_title"
        }
      ],
      "expected": "会生成 output/chart.png，Path.exists() 应返回 True。",
      "pitfalls": [
        "plt.show() 只显示不保存；不要漏写 plt.savefig。",
        "中文图表乱码/方框可能是缺少字体，不是绘图数据错误。"
      ],
      "levels": [
        "入门：修改柱形图标题并再次保存。",
        "巩固：在每根柱子上方使用 plt.text 标数值。",
        "挑战：一张 Figure 中并排绘制柱形图和折线图，保存对比图。"
      ],
      "check": "能熟练使用标题、坐标轴、图例/标数值和 savefig。"
    },
    "E4": {
      "why": "大模型 API 与本地模型区别很大：前者要请求网络、身份认证和解析返回，后者直接调用本地 predict。先管理好配置和密钥。",
      "terms": [
        {
          "name": "API",
          "meaning": "程序之间约定的调用接口"
        },
        {
          "name": "环境变量",
          "meaning": "保存地址、模型名、密钥等配置的操作系统变量"
        },
        {
          "name": "超时与异常处理",
          "meaning": "网络慢、服务失败时不能让批处理无限等待或直接崩溃"
        }
      ],
      "walkthrough": [
        "os.getenv 从环境变量读取地址、模型名、密钥；缺失时返回空字符串。",
        "all([...]) 检查三者是否齐全，缺失则走离线路径。",
        "实际调用 requests.post 前必须验证地址，并使用 timeout；返回 JSON 要检查 choices 等字段。"
      ],
      "apis": [
        {
          "api": "os.getenv",
          "signature": "os.getenv('OPENAI_BASE_URL', '')",
          "parameters": "第一个参数：变量名；第二个参数：缺失时默认值",
          "returns": "返回配置字符串",
          "tip": "不要把 API Key 写入版本库"
        },
        {
          "api": "requests.post",
          "signature": "requests.post(url, headers=..., json=..., timeout=60)",
          "parameters": "json：请求体；headers：认证；timeout：最大等待时间",
          "returns": "HTTP Response",
          "tip": "先检查 status_code/raise_for_status 再解析 JSON"
        }
      ],
      "expected": "没有配置 API 环境变量时只输出『未配置 API，先做离线数据分析』，不会发送真实请求。",
      "pitfalls": [
        "把完整密钥打印到日志或 Notebook 输出，会造成泄漏。",
        "省略 timeout 导致 API 超时阻塞；或假定所有响应都含 choices[0].message.content。"
      ],
      "levels": [
        "入门：打印三个环境变量是否已设置（不打印密钥内容）。",
        "巩固：用字典构造一个 chat/completions 请求体并打印模型名。",
        "挑战：编写请求函数并提供超时/HTTP 错误/非法 JSON 三种兜底。"
      ],
      "check": "能把 API 配置与业务逻辑分离，API 不通时保持离线流程可运行。"
    },
    "E5": {
      "why": "检索增强 RAG 的本质是『先查资料，再组织回答』。入门只需要 TF-IDF + 余弦相似度就能做完整检索，不强迫使用 GPU。",
      "terms": [
        {
          "name": "检索 Top-K",
          "meaning": "按相关性选出最相近的 K 段资料"
        },
        {
          "name": "余弦相似度",
          "meaning": "衡量两个向量方向接近程度的指标"
        },
        {
          "name": "延迟/吞吐量",
          "meaning": "一次请求耗时，以及单位时间内处理多少请求"
        }
      ],
      "walkthrough": [
        "TfidfVectorizer(analyzer='char') 将中文句子转成字符 n-gram 向量。",
        "fit_transform 建立文档向量库；transform 将用户问题投影到相同词表。",
        "cosine_similarity 计算相关性，argmax 选得分最高的文档，perf_counter 计时。"
      ],
      "apis": [
        {
          "api": "cosine_similarity",
          "signature": "cosine_similarity(query_vector, document_matrix)",
          "parameters": "输入形状 (1,V) 与 (N,V)",
          "returns": "返回形状 (1,N) 的相似度矩阵",
          "tip": "得分高代表相关，不等于已验证事实"
        },
        {
          "api": "time.perf_counter",
          "signature": "time.perf_counter()",
          "parameters": "无参数，读取高精度计时器",
          "returns": "返回秒数（相对时间）",
          "tip": "延迟=t1-t0，吞吐量=总请求数/总耗时"
        }
      ],
      "expected": "对于『图书馆几点开放』，通常最相关的是『图书馆周一开放』，但它没有具体开门时间；不能编造。",
      "pitfalls": [
        "把检索到的片段当成完整答案，忽略片段未包含具体时间。",
        "每次查询时重新 fit_transform 全部文档，在正式系统中会增加耗时且难复用。"
      ],
      "levels": [
        "入门：修改查询为『实验室需要预约吗』。",
        "巩固：输出相似度最高的 Top-2 文档及得分。",
        "挑战：构建 10 条制度知识，输出有引用原文的问答与简单覆盖率。"
      ],
      "check": "能解释 RAG 的检索阶段，以及检索得到的证据不足时如何回答。"
    },
    "E6": {
      "why": "竞赛 E 模块最终看的是可运行、可检查、可复现。把测试、性能、README 和演示流程看作代码的一部分。",
      "terms": [
        {
          "name": "单元测试",
          "meaning": "验证一个功能在给定输入下是否返回预期结果"
        },
        {
          "name": "回归测试",
          "meaning": "修改代码后重复确认旧功能不受影响"
        },
        {
          "name": "README",
          "meaning": "说明安装、运行、输入输出、测试结果的交付文档"
        }
      ],
      "walkthrough": [
        "required 指定需要提交的文档和图像。",
        "通过 Path.exists 遍历输出文件并标记缺失。",
        "实际项目还要检查 CSV 列名、图像尺寸与报告是否包含必要章节。"
      ],
      "apis": [
        {
          "api": "assert",
          "signature": "assert condition, 'message'",
          "parameters": "condition：必须满足的条件；message：失败提示",
          "returns": "条件 False 时抛出 AssertionError",
          "tip": "适用于测试断言，不能代替生产环境完整错误处理"
        },
        {
          "api": "path.stat",
          "signature": "Path('output/chart.png').stat().st_size",
          "parameters": "st_size：文件字节数",
          "returns": "返回文件大小",
          "tip": "存在但大小为零的文件不能算通过交付"
        }
      ],
      "expected": "如果 README.md 存在但 output/chart.png 不存在，会显示『缺失 output/chart.png』。",
      "pitfalls": [
        "把 Notebook 最后一个单元显示『已完成』当作交付验证，没有检查真实文件。",
        "只写模型代码没有安装说明和运行步骤，评委或其他用户无法复现。"
      ],
      "levels": [
        "入门：写 missing 文件清单。",
        "巩固：检查 CSV 指定字段存在、PNG 文件非空。",
        "挑战：写 README 包含环境、启动、示例输入输出、测试与展示顺序。"
      ],
      "check": "能准备一份可独立复现的最小 AI 项目交付包。"
    }
  }
};
