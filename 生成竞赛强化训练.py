#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成 6.1.1~6.5.3 共 15 道竞赛强化训练题。

特点：
- 固定随机种子，便于重复训练和自动评分。
- 每题都有带 TODO x-x 的 Notebook、小型本地素材和参考答案。
- 不联网生成数据；深度学习/NLP 运行依赖见 competition_advanced_requirements.txt。
"""

from __future__ import annotations
import argparse, json, math, random, shutil
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT=Path(__file__).resolve().parent
SRC=ROOT/"人工智能训练师三级素材"/"人工智能训练师三级上网素材"
ANS=ROOT/"人工智能训练师三级素材"/"操作题答案"
SEED=20261005
random.seed(SEED); np.random.seed(SEED)

def code_cell(text):
    return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":[x+"\n" for x in text.strip("\n").split("\n")]}

def md_cell(text):
    return {"cell_type":"markdown","metadata":{},"source":[x+"\n" for x in text.strip("\n").split("\n")]}

def write_nb(qid,title,task,cells):
    nb={"cells":[md_cell(f"# {qid} {title}\n\n{task}\n\n> 按 TODO 编号补全代码。不要删除 TODO 标记。"),*cells],
        "metadata":{"kernelspec":{"display_name":"Python 3 (ipykernel)","language":"python","name":"python3"},
                    "language_info":{"name":"python","version":"3.12"}},
        "nbformat":4,"nbformat_minor":5}
    (SRC/qid).mkdir(parents=True,exist_ok=True)
    (SRC/qid/f"{qid}.ipynb").write_text(json.dumps(nb,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")

def write_answer(qid,title,solution):
    ANS.mkdir(parents=True,exist_ok=True)
    (ANS/f"{qid}_答案.md").write_text(f"# {qid} {title} - 参考答案\n\n~~~python\n{solution.strip()}\n~~~\n",encoding="utf-8")

def img_dir(qid,name):
    p=SRC/qid/name; p.mkdir(parents=True,exist_ok=True); return p

def gen_a1(qid):
    p=img_dir(qid,"input_images")
    for i in range(30):
        base=np.random.randint(40,216)
        arr=np.full((160,160,3),base,dtype=np.uint8)
        yy,xx=np.ogrid[:160,:160]
        mask=(xx-80)**2+(yy-80)**2 < (25+i%20)**2
        arr[mask]=np.clip(base+np.random.randint(-30,60),0,255)
        im=Image.fromarray(arr)
        if i%7==0: im=ImageEnhance.Brightness(im).enhance(0.25)
        if i%11==0: im=ImageEnhance.Brightness(im).enhance(1.8)
        if i%6==0: im=im.filter(ImageFilter.GaussianBlur(3))
        im.save(p/f"product_{i:03d}.jpg")
    cells=[
code_cell("""import cv2, json, random
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance
import matplotlib.pyplot as plt

INPUT=Path("input_images")
OUTPUT=Path("augmented_images")
OUTPUT.mkdir(exist_ok=True)
QUALITY_CSV=Path("image_quality.csv")"""),
code_cell("""rows=[]
for fp in sorted(INPUT.glob("*.jpg")):
    img=cv2.imread(str(fp))
    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # TODO 1-1：计算 Laplacian 方差作为清晰度
    sharpness = _____________
    # TODO 1-2：计算灰度均值作为亮度
    brightness = _____________
    status="合格"
    if sharpness < 35: status="模糊"
    elif brightness < 45: status="过暗"
    elif brightness > 215: status="过亮"
    rows.append({"file":fp.name,"sharpness":sharpness,"brightness":brightness,"status":status})
quality=pd.DataFrame(rows)
quality.to_csv(QUALITY_CSV,index=False,encoding="utf-8-sig")
quality["status"].value_counts()"""),
code_cell("""good=quality.loc[quality["status"]=="合格","file"].tolist()
random.seed(42)
for name in good:
    im=Image.open(INPUT/name).convert("RGB")
    im.save(OUTPUT/name)
    # TODO 2-1：生成水平翻转图
    flipped = _____________
    flipped.save(OUTPUT/f"{Path(name).stem}_flip.jpg")
    # TODO 2-2：生成 +15 度旋转图
    rotated = _____________
    rotated.save(OUTPUT/f"{Path(name).stem}_rot15.jpg")
    # TODO 2-3：将亮度随机调整到 0.8~1.2
    factor = _____________
    bright = ImageEnhance.Brightness(im).enhance(factor)
    bright.save(OUTPUT/f"{Path(name).stem}_bright.jpg")"""),
code_cell("""summary={
 "original":len(list(INPUT.glob("*.jpg"))),
 "qualified":len(good),
 "augmented_total":len(list(OUTPUT.glob("*.jpg"))),
 "quality_counts":quality["status"].value_counts().to_dict()
}
Path("summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
files=list(OUTPUT.glob("*.jpg"))
sample=random.sample(files,min(6,len(files)))
fig,axes=plt.subplots(2,3,figsize=(10,7))
for ax,fp in zip(axes.ravel(),sample):
    ax.imshow(Image.open(fp)); ax.set_title(fp.name,fontsize=8); ax.axis("off")
plt.tight_layout(); plt.savefig("augmentation_preview.png",dpi=150)
summary""")]
    write_nb(qid,"商品图片质量检测与多策略数据增强","完成质量检测、筛选、三类增强、统计和预览图输出。",cells)
    sol="""sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
brightness = gray.mean()
flipped = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
rotated = im.rotate(15, expand=False)
factor = random.uniform(0.8, 1.2)"""
    write_answer(qid,"商品图片质量检测与多策略数据增强",sol)

def gen_a2(qid):
    p=img_dir(qid,"road_images")
    for i in range(12):
        im=Image.new("RGB",(640,360),(120+i*3,160,190))
        d=ImageDraw.Draw(im); d.rectangle((0,230,640,360),fill=(70,70,70))
        for j in range(2+i%4):
            x=40+j*130+(i*17)%70; y=235+(j%2)*35
            d.rectangle((x,y,x+80,y+40),fill=(40+20*j,40,200-15*j))
            d.ellipse((x+12,y+30,x+28,y+46),fill="black"); d.ellipse((x+55,y+30,x+71,y+46),fill="black")
        im.save(p/f"road_{i:02d}.jpg")
    cells=[
code_cell("""import cv2
from pathlib import Path
import pandas as pd
import numpy as np
INPUT=Path("road_images"); ROI=Path("roi_output"); VIS=Path("visualized")
ROI.mkdir(exist_ok=True); VIS.mkdir(exist_ok=True)"""),
code_cell("""records=[]
for fp in sorted(INPUT.glob("*.jpg")):
    img=cv2.imread(str(fp))
    # TODO 1-1：统一尺寸为 640×360
    img = _____________
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # TODO 1-2：5×5 高斯滤波
    blur = _____________
    # TODO 1-3：Canny(50,150)
    edges = _____________
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(9,5))
    # TODO 1-4：闭运算连接边缘
    closed = _____________
    contours,_=cv2.findContours(closed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    kept=[]
    for c in contours:
        x,y,w,h=cv2.boundingRect(c); area=w*h; ratio=w/max(h,1)
        if area>=1200 and 1.2<=ratio<=5.0:
            kept.append((x,y,w,h))
    for k,(x,y,w,h) in enumerate(kept):
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        cv2.imwrite(str(ROI/f"{fp.stem}_{k}.jpg"),img[y:y+h,x:x+w])
    cv2.imwrite(str(VIS/fp.name),img)
    records.append({"file":fp.name,"candidates":len(kept),
                    "area_ratio":sum(w*h for x,y,w,h in kept)/(640*360)})
pd.DataFrame(records).to_csv("detection_summary.csv",index=False)
pd.DataFrame(records)""")]
    write_nb(qid,"道路车辆图像预处理与目标区域提取","完成道路图像预处理、候选区域提取、ROI 保存和汇总统计。",cells)
    write_answer(qid,"道路车辆图像预处理与目标区域提取","""img=cv2.resize(img,(640,360))
blur=cv2.GaussianBlur(gray,(5,5),0)
edges=cv2.Canny(blur,50,150)
closed=cv2.morphologyEx(edges,cv2.MORPH_CLOSE,kernel,iterations=2)""")

def gen_a3(qid):
    p=img_dir(qid,"defect_images")
    for i in range(30):
        arr=np.random.normal(128,8,(256,256)).clip(0,255).astype(np.uint8)
        im=Image.fromarray(arr); d=ImageDraw.Draw(im)
        for _ in range(i%5):
            x=random.randint(25,230); y=random.randint(25,230); r=random.randint(4,14)
            val=220 if random.random()>0.5 else 35
            d.ellipse((x-r,y-r,x+r,y+r),fill=val)
        im.save(p/f"metal_{i:03d}.png")
    cells=[
code_cell("""import cv2
from pathlib import Path
import pandas as pd, numpy as np
INPUT=Path("defect_images"); MASK=Path("masks"); VIS=Path("defect_vis")
MASK.mkdir(exist_ok=True); VIS.mkdir(exist_ok=True)
clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))"""),
code_cell("""rows=[]
for fp in sorted(INPUT.glob("*.png")):
    gray=cv2.imread(str(fp),cv2.IMREAD_GRAYSCALE)
    # TODO 1-1：CLAHE 增强
    enhanced = _____________
    # TODO 1-2：检测亮缺陷 >180
    bright = _____________
    # TODO 1-3：检测暗缺陷 <70
    dark = _____________
    mask=cv2.bitwise_or(bright,dark)
    kernel=np.ones((3,3),np.uint8)
    # TODO 1-4：开运算去噪后闭运算连接
    mask = _____________
    n,labels,stats,cent=cv2.connectedComponentsWithStats(mask,8)
    keep=np.zeros_like(mask); areas=[]
    for idx in range(1,n):
        area=stats[idx,cv2.CC_STAT_AREA]
        if area>=40: keep[labels==idx]=255; areas.append(int(area))
    total=sum(areas); ratio=total/keep.size
    level="正常" if ratio<0.002 else ("轻微" if ratio<0.01 else "严重")
    cv2.imwrite(str(MASK/fp.name),keep)
    rows.append({"file":fp.name,"defect_count":len(areas),"defect_area":total,"ratio":ratio,"level":level})
pd.DataFrame(rows).to_csv("defect_report.csv",index=False,encoding="utf-8-sig")
pd.DataFrame(rows).head()""")]
    write_nb(qid,"工业表面缺陷增强、分割与统计","完成局部增强、双阈值缺陷分割、形态学处理、连通域统计与分级。",cells)
    write_answer(qid,"工业表面缺陷增强、分割与统计","""enhanced=clahe.apply(gray)
_,bright=cv2.threshold(enhanced,180,255,cv2.THRESH_BINARY)
_,dark=cv2.threshold(enhanced,70,255,cv2.THRESH_BINARY_INV)
mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernel,iterations=2)""")

def gen_b(qid,kind):
    p=SRC/qid; p.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(SEED+int(qid[-1]))
    if kind=="cluster":
        n=600
        df=pd.DataFrame({"Age":rng.integers(18,65,n),"Income":rng.normal(9000,3500,n).clip(2500,30000),
         "MonthlySpend":rng.normal(1800,900,n).clip(100,8000),"Visits":rng.poisson(7,n),
         "Region":rng.choice(["East","West","North","South"],n),"Member":rng.choice(["Yes","No"],n,p=[.65,.35])})
        df.loc[rng.choice(n,25,False),"Income"]=np.nan; df.to_csv(p/"customer_behavior.csv",index=False)
        title="用户画像聚类与最佳 K 自动选择"
        starter="""import pandas as pd, numpy as np, joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

df=pd.read_csv("customer_behavior.csv")
num=["Age","Income","MonthlySpend","Visits"]; cat=["Region","Member"]
# TODO 1-1：数值列中位数填补并标准化
num_pipe=Pipeline([("imputer",_____________),("scaler",_____________)])
# TODO 1-2：类别列众数填补并 OneHot
cat_pipe=Pipeline([("imputer",_____________),("onehot",_____________)])
pre=ColumnTransformer([("num",num_pipe,num),("cat",cat_pipe,cat)])
X=pre.fit_transform(df)
rows=[]
for k in range(2,7):
    model=KMeans(n_clusters=k,random_state=42,n_init=10)
    labels=model.fit_predict(X)
    # TODO 2-1：计算轮廓系数
    score=_____________
    rows.append((k,score))
scores=pd.DataFrame(rows,columns=["k","silhouette"])
best_k=int(scores.loc[scores.silhouette.idxmax(),"k"])
# TODO 2-2：训练最佳 KMeans
best=_____________
df["cluster"]=best.fit_predict(X)
df.to_csv("customer_clusters.csv",index=False)
scores.to_csv("k_selection.csv",index=False)
joblib.dump((pre,best),"best_cluster_model.pkl")
df.groupby("cluster")[num].mean()"""
        sol="""SimpleImputer(strategy="median")
StandardScaler()
SimpleImputer(strategy="most_frequent")
OneHotEncoder(handle_unknown="ignore")
silhouette_score(X,labels)
KMeans(n_clusters=best_k,random_state=42,n_init=10)"""
    elif kind=="churn":
        n=800
        tenure=rng.integers(1,73,n); fee=rng.normal(95,30,n).clip(20,220); support=rng.poisson(1.5,n)
        prob=1/(1+np.exp(-(-2+0.018*fee-0.03*tenure+0.35*support)))
        df=pd.DataFrame({"Tenure":tenure,"MonthlyFee":fee,"SupportCalls":support,"Contract":rng.choice(["Month","Year","TwoYear"],n),
        "Internet":rng.choice(["Fiber","DSL","None"],n),"AutoPay":rng.choice(["Yes","No"],n),"Churn":rng.binomial(1,prob)})
        df.loc[rng.choice(n,20,False),"MonthlyFee"]=np.nan; df.to_csv(p/"telecom_churn.csv",index=False)
        title="客户流失随机森林分类与参数调优"
        starter="""import pandas as pd, json, joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix

df=pd.read_csv("telecom_churn.csv"); X=df.drop(columns="Churn"); y=df["Churn"]
num=X.select_dtypes(include="number").columns; cat=X.select_dtypes(exclude="number").columns
pre=ColumnTransformer([("num",SimpleImputer(strategy="median"),num),
 ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("oh",OneHotEncoder(handle_unknown="ignore"))]),cat)])
# TODO 1-1：按 8:2 分层划分
X_train,X_test,y_train,y_test=_____________
pipe=Pipeline([("pre",pre),("model",RandomForestClassifier(random_state=42,class_weight="balanced"))])
pipe.fit(X_train,y_train); pred=pipe.predict(X_test)
# TODO 2-1：计算四项分类指标
metrics={"accuracy":_____________,"precision":_____________,"recall":_____________,"f1":_____________}
print(metrics,confusion_matrix(y_test,pred))
grid={"model__n_estimators":[100,200],"model__max_depth":[None,8,14],"model__min_samples_split":[2,5]}
# TODO 2-2：以 F1 为评分做 GridSearchCV
search=_____________
search.fit(X_train,y_train)
joblib.dump(search.best_estimator_,"best_churn_model.pkl")
pd.DataFrame({"y_true":y_test,"y_pred":search.predict(X_test)}).to_csv("predictions.csv",index=False)
Path=None
open("metrics.json","w",encoding="utf-8").write(json.dumps(metrics,ensure_ascii=False,indent=2))"""
        sol="""train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
accuracy_score(y_test,pred)
precision_score(y_test,pred,zero_division=0)
recall_score(y_test,pred,zero_division=0)
f1_score(y_test,pred,zero_division=0)
GridSearchCV(pipe,grid,scoring="f1",cv=4,n_jobs=-1)"""
    else:
        n=800
        year=rng.integers(1995,2026,n); area=rng.normal(105,35,n).clip(35,260); rooms=rng.integers(1,7,n)
        region=rng.choice(["Center","East","West","Suburb"],n); school=rng.uniform(1,10,n)
        price=area*22000+school*85000+(2026-year)*-12000+np.where(region=="Center",800000,0)+rng.normal(0,180000,n)
        df=pd.DataFrame({"BuildYear":year,"Area":area,"Rooms":rooms,"Region":region,"SchoolScore":school,"Price":price.clip(350000)})
        df.to_csv(p/"housing.csv",index=False)
        title="房价回归特征工程与多模型比较"
        starter="""import pandas as pd, numpy as np, joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.metrics import mean_squared_error,r2_score

df=pd.read_csv("housing.csv")
# TODO 1-1：构造房龄
df["HouseAge"]=_____________
# TODO 1-2：构造平均房间面积
df["AreaPerRoom"]=_____________
X=df.drop(columns="Price"); y=df["Price"]
num=X.select_dtypes(include="number").columns; cat=X.select_dtypes(exclude="number").columns
pre=ColumnTransformer([("num",StandardScaler(),num),("cat",OneHotEncoder(handle_unknown="ignore"),cat)])
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=42)
models={"RandomForest":RandomForestRegressor(n_estimators=180,random_state=42),
        "GradientBoosting":GradientBoostingRegressor(random_state=42)}
rows=[]; fitted={}
for name,m in models.items():
    pipe=Pipeline([("pre",pre),("model",m)]); pipe.fit(X_train,y_train); pred=pipe.predict(X_test)
    # TODO 2-1：计算 RMSE
    rmse=_____________
    # TODO 2-2：计算 R²
    r2=_____________
    rows.append({"model":name,"RMSE":rmse,"R2":r2}); fitted[name]=pipe
result=pd.DataFrame(rows); result.to_csv("model_comparison.csv",index=False)
best_name=result.sort_values("RMSE").iloc[0]["model"]
best=fitted[best_name]; joblib.dump(best,"best_house_model.pkl")
pd.DataFrame({"actual":y_test,"pred":best.predict(X_test)}).to_csv("test_predictions.csv",index=False)
result"""
        sol="""2026-df["BuildYear"]
df["Area"]/df["Rooms"]
mean_squared_error(y_test,pred)**0.5
r2_score(y_test,pred)"""
    write_nb(qid,title,"按 TODO 完成完整机器学习流水线。",[code_cell(starter)])
    write_answer(qid,title,sol)

def draw_shape(im,kind,color):
    d=ImageDraw.Draw(im); w,h=im.size
    if kind=="circle": d.ellipse((25,25,w-25,h-25),fill=color)
    elif kind=="square": d.rectangle((25,25,w-25,h-25),fill=color)
    elif kind=="triangle": d.polygon([(w//2,20),(20,h-20),(w-20,h-20)],fill=color)
    else: d.rounded_rectangle((20,30,w-20,h-30),radius=15,fill=color)

def gen_c(qid,variant):
    p=SRC/qid; p.mkdir(parents=True,exist_ok=True)
    if variant==1: root=p/"shape_images"; classes=["circle","square","triangle"]
    elif variant==2: root=p/"flower_images"; classes=["rose","sunflower","tulip","daisy"]
    else: root=p/"scene_images"; classes=["city","forest","sea","mountain"]
    for ci,c in enumerate(classes):
        d=root/c; d.mkdir(parents=True,exist_ok=True)
        for i in range(70):
            im=Image.new("RGB",(64,64),(20+ci*20,30,40))
            color=(60+ci*45,140+(i%20),80+ci*30)
            draw_shape(im,["circle","square","triangle","other"][ci%4],color)
            im=im.rotate(random.uniform(-12,12))
            im.save(d/f"{c}_{i:03d}.png")
    if variant==1:
        title="三类图形 CNN 分类完整训练流程"
        starter="""import torch
from torch import nn
from torch.utils.data import DataLoader,random_split
from torchvision.datasets import ImageFolder
from torchvision import transforms
from pathlib import Path
import pandas as pd

transform=transforms.Compose([transforms.ToTensor()])
# TODO 1-1：使用 ImageFolder 读取 shape_images
dataset=_____________
train_n=int(len(dataset)*0.8); val_n=len(dataset)-train_n
# TODO 1-2：固定随机种子划分训练/验证集
train_set,val_set=_____________
train_loader=DataLoader(train_set,batch_size=32,shuffle=True); val_loader=DataLoader(val_set,batch_size=64)
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.features=nn.Sequential(nn.Conv2d(3,16,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
                                    nn.Conv2d(16,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2))
        # TODO 2-1：64×64 两次池化后为 16×16
        self.fc=_____________
    def forward(self,x): return self.fc(self.features(x).flatten(1))
model=Net()
# TODO 2-2：定义 CrossEntropyLoss 和 Adam
criterion=_____________; optimizer=_____________
history=[]
for epoch in range(8):
    model.train(); total=correct=0; loss_sum=0
    for x,y in train_loader:
        optimizer.zero_grad(); out=model(x); loss=criterion(out,y); loss.backward(); optimizer.step()
        loss_sum+=loss.item()*len(y); correct+=(out.argmax(1)==y).sum().item(); total+=len(y)
    history.append({"epoch":epoch+1,"loss":loss_sum/total,"train_acc":correct/total})
torch.save(model.state_dict(),"shape_cnn.pt")
pd.DataFrame(history).to_csv("training_history.csv",index=False)
history[-1]"""
        sol="""dataset=ImageFolder("shape_images",transform=transform)
train_set,val_set=random_split(dataset,[train_n,val_n],generator=torch.Generator().manual_seed(42))
self.fc=nn.Linear(32*16*16,3)
criterion=nn.CrossEntropyLoss()
optimizer=torch.optim.Adam(model.parameters(),lr=1e-3)"""
    elif variant==2:
        title="四类花卉 CNN：增强、BatchNorm 与 Dropout"
        starter="""import torch, copy
from torch import nn
from torch.utils.data import DataLoader,random_split
from torchvision.datasets import ImageFolder
from torchvision import transforms
import pandas as pd, matplotlib.pyplot as plt

# TODO 1-1：训练增强：翻转、旋转、ColorJitter、ToTensor
train_tf=transforms.Compose([_____________])
val_tf=transforms.Compose([transforms.ToTensor()])
base=ImageFolder("flower_images")
n=int(len(base)*.8); train_idx,val_idx=random_split(range(len(base)),[n,len(base)-n],generator=torch.Generator().manual_seed(42))
train_ds=ImageFolder("flower_images",transform=train_tf); val_ds=ImageFolder("flower_images",transform=val_tf)
train_ds=torch.utils.data.Subset(train_ds,train_idx.indices); val_ds=torch.utils.data.Subset(val_ds,val_idx.indices)
train_loader=DataLoader(train_ds,32,shuffle=True); val_loader=DataLoader(val_ds,64)
class FlowerNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net=nn.Sequential(nn.Conv2d(3,24,3,padding=1),
          # TODO 2-1：加入 BatchNorm2d
          _____________,nn.ReLU(),nn.MaxPool2d(2),
          nn.Conv2d(24,48,3,padding=1),nn.BatchNorm2d(48),nn.ReLU(),nn.MaxPool2d(2),
          nn.Flatten(),nn.Linear(48*16*16,128),nn.ReLU(),
          # TODO 2-2：加入 Dropout(0.4)
          _____________,nn.Linear(128,4))
    def forward(self,x): return self.net(x)
model=FlowerNet(); criterion=nn.CrossEntropyLoss(); opt=torch.optim.Adam(model.parameters(),lr=1e-3)
print(model)"""
        sol="""transforms.RandomHorizontalFlip(),
transforms.RandomRotation(15),
transforms.ColorJitter(brightness=.2,contrast=.2),
transforms.ToTensor()
nn.BatchNorm2d(24)
nn.Dropout(0.4)"""
    else:
        title="ResNet18 骨干冻结、微调与模型复载验证"
        starter="""import torch
from torch import nn
from torchvision import transforms,models
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader,random_split

tf=transforms.Compose([transforms.Resize((128,128)),transforms.ToTensor()])
ds=ImageFolder("scene_images",transform=tf)
n=int(len(ds)*.8); train_ds,val_ds=random_split(ds,[n,len(ds)-n],generator=torch.Generator().manual_seed(42))
train_loader=DataLoader(train_ds,32,shuffle=True); val_loader=DataLoader(val_ds,64)
# TODO 1-1：创建 ResNet18，不下载预训练权重
model=_____________
# TODO 1-2：冻结所有参数
for p in model.parameters(): _____________
# TODO 1-3：替换 fc 为 4 类输出，并保持可训练
model.fc=_____________
criterion=nn.CrossEntropyLoss(); opt=torch.optim.Adam(model.fc.parameters(),lr=1e-3)
# 第一阶段训练代码按课堂模板补全
# TODO 2-1：解冻 layer4
for p in model.layer4.parameters(): _____________
# TODO 2-2：以更小学习率优化 layer4 + fc
opt=_____________
torch.save(model.state_dict(),"best_resnet18.pt")
print("模型已保存")"""
        sol="""model=models.resnet18(weights=None)
p.requires_grad=False
model.fc=nn.Linear(model.fc.in_features,4)
p.requires_grad=True
torch.optim.Adam(filter(lambda p:p.requires_grad,model.parameters()),lr=1e-4)"""
    write_nb(qid,title,"完成指定深度学习训练流程；首次运行请安装竞赛强化依赖。",[code_cell(starter)])
    write_answer(qid,title,sol)

def gen_d(qid,variant):
    p=SRC/qid; p.mkdir(parents=True,exist_ok=True)
    cats={"科技":["人工智能 模型 芯片 算法 数据 云计算","手机 发布 芯片 性能 系统 创新"],
          "体育":["球队 比赛 联赛 冠军 球员 教练","篮球 足球 赛季 得分 主场 胜利"],
          "财经":["市场 股票 投资 企业 收益 经济","银行 利率 基金 交易 金融 增长"],
          "娱乐":["电影 演员 票房 综艺 音乐","导演 剧情 明星 演出 观众 节目"]}
    rows=[]
    for c,templates in cats.items():
        for i in range(90):
            rows.append({"text":templates[i%2]+" "+random.choice(["今日","最新","行业","中国","发展"]), "label":c})
    random.shuffle(rows)
    pd.DataFrame(rows).to_csv(p/("news_train.csv" if variant==1 else "corpus_news.csv"),index=False)
    (p/"stopwords.txt").write_text("的\n了\n和\n是\n在\n今日\n",encoding="utf-8")
    if variant==2:
        reviews=[]
        pos=["商品 很 满意 质量 好 物流 快","体验 精彩 值得 推荐 服务 好","非常 喜欢 性价比 高"]
        neg=["商品 很 失望 质量 差 物流 慢","体验 糟糕 不 推荐 服务 差","非常 不满 性价比 低"]
        for i in range(300):
            label=i%2; reviews.append({"review":(pos if label else neg)[i%3],"label":label})
        pd.DataFrame(reviews).to_csv(p/"reviews.csv",index=False)
    if variant==1:
        title="中文新闻 TF-IDF 分类与关键词解释"
        starter="""import pandas as pd, json, joblib, jieba
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

df=pd.read_csv("news_train.csv")
stop=set(x.strip() for x in open("stopwords.txt",encoding="utf-8") if x.strip())
def cut(s):
    # TODO 1-1：jieba 精确分词并过滤停用词
    return " ".join(_____________)
df["cut"]=df["text"].map(cut)
X_train,X_test,y_train,y_test=train_test_split(df["cut"],df["label"],test_size=.2,random_state=42,stratify=df["label"])
# TODO 1-2：TF-IDF，最大 2000 特征，1-2 gram
vec=_____________
Xtr=vec.fit_transform(X_train); Xte=vec.transform(X_test)
# TODO 2-1：训练 LogisticRegression
model=_____________; model.fit(Xtr,y_train)
pred=model.predict(Xte); print(classification_report(y_test,pred))
features=vec.get_feature_names_out(); kws={}
for i,c in enumerate(model.classes_):
    # TODO 2-2：取该类别系数最大的 10 个词
    idx=_____________
    kws[c]=features[idx].tolist()
json.dump(kws,open("class_keywords.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
joblib.dump((vec,model),"news_classifier.pkl")"""
        sol="""[w for w in jieba.cut(str(s),cut_all=False) if w.strip() and w not in stop]
TfidfVectorizer(max_features=2000,ngram_range=(1,2))
LogisticRegression(max_iter=1000)
model.coef_[i].argsort()[-10:][::-1]"""
    elif variant==2:
        title="商品评论 Word2Vec 句向量与情感分类"
        starter="""import pandas as pd, numpy as np, jieba
from gensim.models import Word2Vec
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score,confusion_matrix

df=pd.read_csv("reviews.csv")
stop=set(x.strip() for x in open("stopwords.txt",encoding="utf-8") if x.strip())
# TODO 1-1：完成分词并过滤停用词
tokens=_____________
# TODO 1-2：训练 100 维 Word2Vec
w2v=_____________
w2v.save("reviews_word2vec.model")
def sentence_vector(words):
    valid=[w2v.wv[w] for w in words if w in w2v.wv]
    # TODO 2-1：返回平均词向量；无有效词返回全零
    return _____________
X=np.vstack([sentence_vector(x) for x in tokens]); y=df["label"].to_numpy()
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
clf=LogisticRegression(max_iter=1000).fit(Xtr,ytr); pred=clf.predict(Xte)
print("F1",f1_score(yte,pred)); print(confusion_matrix(yte,pred))
# TODO 2-2：查询“满意”最相似的 5 个词
print(_____________)"""
        sol="""tokens=[[w for w in jieba.cut(str(s)) if w.strip() and w not in stop] for s in df["review"]]
w2v=Word2Vec(tokens,vector_size=100,window=5,min_count=1,workers=2,seed=42)
np.mean(valid,axis=0) if valid else np.zeros(w2v.vector_size,dtype=float)
w2v.wv.most_similar("满意",topn=5)"""
    else:
        title="新闻 LDA 主题发现与相似文章推荐"
        starter="""import pandas as pd, json, jieba
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity

df=pd.read_csv("corpus_news.csv")
df["cut"]=df["text"].map(lambda s:" ".join(jieba.cut(str(s))))
# TODO 1-1：构建 CountVectorizer，max_features=1500
cv=_____________; X=cv.fit_transform(df["cut"])
# TODO 1-2：训练 5 主题 LDA
lda=_____________; topic_dist=lda.fit_transform(X)
df["dominant_topic"]=topic_dist.argmax(1)
words=cv.get_feature_names_out(); topics={}
for i,comp in enumerate(lda.components_):
    # TODO 2-1：每主题 Top-10 关键词
    topics[str(i)]=_____________
json.dump(topics,open("topics.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)
tf=TfidfVectorizer(max_features=1500); T=tf.fit_transform(df["cut"])
sim=cosine_similarity(T)
target=0
# TODO 2-2：排除自身，找最相似 5 篇
idx=_____________
json.dump({"target":int(target),"similar":[int(x) for x in idx]},open("recommendations.json","w"),indent=2)
df.to_csv("topic_result.csv",index=False)"""
        sol="""CountVectorizer(max_features=1500)
LatentDirichletAllocation(n_components=5,random_state=42)
words[comp.argsort()[-10:][::-1]].tolist()
sim[target].argsort()[::-1][1:6]"""
    write_nb(qid,title,"完成中文文本预处理、建模和结果解释。",[code_cell(starter)])
    write_answer(qid,title,sol)

def gen_e(qid,variant):
    p=SRC/qid; p.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(SEED+variant)
    if variant==1:
        orders=[]
        for i in range(420):
            orders.append({"order_id":f"O{i:04d}","customer_id":f"C{rng.integers(1,130):03d}",
             "category":rng.choice(["数码","家居","食品","服装"]),"price":round(float(rng.uniform(20,1500)),2),
             "qty":int(rng.integers(1,5)),"date":f"2026-{int(rng.integers(1,10)):02d}-{int(rng.integers(1,28)):02d}"})
        (p/"orders.json").write_text(json.dumps(orders,ensure_ascii=False,indent=2),encoding="utf-8")
        title="电商经营数据分析与 AI 经营报告"
        starter="""import json, os, requests
import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_json("orders.json")
# TODO 1-1：日期转 datetime
df["date"]=_____________
# TODO 1-2：计算 sales=price*qty
df["sales"]=_____________
gmv=float(df["sales"].sum()); orders=df["order_id"].nunique()
# TODO 2-1：计算客单价
aov=_____________
customer_orders=df.groupby("customer_id")["order_id"].nunique()
# TODO 2-2：计算复购率（订单数>1客户占比）
repeat_rate=_____________
df["month"]=df["date"].dt.to_period("M").astype(str)
monthly=df.groupby("month")["sales"].sum(); category=df.groupby("category")["sales"].sum().sort_values(ascending=False)
fig,ax=plt.subplots(1,2,figsize=(12,4)); monthly.plot(kind="bar",ax=ax[0]); category.plot(kind="bar",ax=ax[1])
plt.tight_layout(); plt.savefig("dashboard.png",dpi=150)
df.to_excel("orders_clean.xlsx",index=False)
prompt=f"""你是经营分析师。根据指标生成 Markdown 报告，必须包含：现状、问题、原因、建议。
GMV={gmv:.2f}，订单数={orders}，客单价={aov:.2f}，复购率={repeat_rate:.2%}
品类销售额={category.to_dict()}"""
# TODO 3-1：从环境变量读取 BASE_URL/API_KEY/MODEL
BASE_URL=_____________; API_KEY=_____________; MODEL=_____________
report="# 电商经营分析\n\n"+prompt
if BASE_URL and API_KEY and MODEL:
    try:
        # TODO 3-2：调用 /v1/chat/completions
        r=_____________
        r.raise_for_status(); report=r.json()["choices"][0]["message"]["content"]
    except Exception as e: report += f"\n\n> AI 调用失败：{e}"
open("business_report.md","w",encoding="utf-8").write(report)
print(report[:1000])"""
        sol="""pd.to_datetime(df["date"],errors="coerce")
df["price"]*df["qty"]
gmv/orders
float((customer_orders>1).mean())
os.getenv("OPENAI_BASE_URL","")
os.getenv("OPENAI_API_KEY","")
os.getenv("OPENAI_MODEL","")
requests.post(BASE_URL.rstrip("/")+"/v1/chat/completions",headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},json={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0.2},timeout=60)"""
    elif variant==2:
        cats=["物流","质量","退款","售后"]; texts={"物流":"物流 延迟 快递 一直 没到","质量":"商品 破损 质量 很差","退款":"申请 退款 一直 未处理","售后":"客服 不回复 售后 体验 差"}
        rows=[]
        for i in range(500):
            c=random.choice(cats); rows.append({"id":i,"text":texts[c]+" "+random.choice(["非常生气","希望尽快解决","影响使用","要求处理"]),
                 "amount":round(float(rng.uniform(20,5000)),2),"category":c})
        pd.DataFrame(rows).to_csv(p/"complaints.csv",index=False)
        title="客户投诉分类、优先级预测与 AI 处置建议"
        starter="""import pandas as pd, json, os, requests
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

df=pd.read_csv("complaints.csv").fillna({"text":"","amount":0})
Xtr,Xte,ytr,yte=train_test_split(df["text"],df["category"],test_size=.2,random_state=42,stratify=df["category"])
# TODO 1-1：TF-IDF + LogisticRegression Pipeline
clf=_____________; clf.fit(Xtr,ytr)
print(classification_report(yte,clf.predict(Xte)))
df["pred_category"]=clf.predict(df["text"])
negative=["生气","差","破损","未处理","不回复"]
# TODO 2-1：金额、负面词和类别共同计算优先级分数
df["priority_score"]=_____________
df["priority"]=pd.cut(df["priority_score"],[-1,1,3,99],labels=["P3","P2","P1"])
BASE=os.getenv("OPENAI_BASE_URL",""); KEY=os.getenv("OPENAI_API_KEY",""); MODEL=os.getenv("OPENAI_MODEL","")
actions=[]
for _,row in df[df["priority"]=="P1"].head(20).iterrows():
    prompt=f'请针对投诉输出严格 JSON，字段 summary/risk/action/reply：{row.text}'
    item={"id":int(row.id),"error":None}
    try:
        if not (BASE and KEY and MODEL): raise RuntimeError("未配置 API")
        # TODO 3-1：调用兼容接口并解析 JSON 文本
        content=_____________
        item["result"]=json.loads(content)
    except Exception as e: item["error"]=str(e)
    actions.append(item)
df.to_excel("complaint_results.xlsx",index=False)
json.dump(actions,open("ai_actions.json","w",encoding="utf-8"),ensure_ascii=False,indent=2)"""
        sol="""Pipeline([("tfidf",TfidfVectorizer(max_features=2000)),("model",LogisticRegression(max_iter=1000))])
(df["amount"]>2000).astype(int)+(df["text"].apply(lambda s:any(w in s for w in negative))).astype(int)+(df["pred_category"].isin(["退款","质量"])).astype(int)
requests.post(BASE.rstrip("/")+"/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json={"model":MODEL,"messages":[{"role":"user","content":prompt}],"response_format":{"type":"json_object"}},timeout=60).json()["choices"][0]["message"]["content"]"""
    else:
        docs={"考勤制度.txt":"员工应在工作日 9:00 前完成签到。迟到超过30分钟按缺勤半天处理。每月可申请两次异常考勤修正。",
              "报销制度.txt":"差旅报销需在返程后10个工作日内提交。单笔住宿超过600元需要部门负责人审批。发票必须真实有效。",
              "信息安全制度.txt":"禁止共享账号密码。重要系统必须启用多因素认证。发现疑似数据泄露应立即报告信息安全负责人。",
              "采购制度.txt":"5000元以下采购由部门负责人审批；5000元及以上需要采购部门复核；20000元以上需三方比价。"}
        kd=p/"knowledge_docs"; kd.mkdir(exist_ok=True)
        for name,txt in docs.items():(kd/name).write_text(txt,encoding="utf-8")
        pd.DataFrame([
         {"question":"差旅报销应该多久内提交？","expected_keywords":"10个工作日,返程"},
         {"question":"住宿费超过600元怎么办？","expected_keywords":"部门负责人,审批"},
         {"question":"重要系统账号安全有什么要求？","expected_keywords":"多因素认证,禁止共享"},
         {"question":"两万元以上采购有什么要求？","expected_keywords":"三方比价"}
        ]).to_csv(p/"questions.csv",index=False)
        title="企业知识库检索增强问答与自动评测"
        starter="""from pathlib import Path
import pandas as pd, numpy as np, os, time, requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

chunks=[]
for fp in Path("knowledge_docs").glob("*.txt"):
    for para in fp.read_text(encoding="utf-8").splitlines():
        if para.strip(): chunks.append({"source":fp.name,"text":para.strip()})
texts=[x["text"] for x in chunks]
# TODO 1-1：TF-IDF 建库
vectorizer=_____________; matrix=vectorizer.fit_transform(texts)
def retrieve(query,top_k=3):
    q=vectorizer.transform([query]); scores=cosine_similarity(q,matrix)[0]
    # TODO 1-2：取相似度最高的 top_k
    idx=_____________
    return [{**chunks[i],"score":float(scores[i])} for i in idx]

BASE=os.getenv("OPENAI_BASE_URL",""); KEY=os.getenv("OPENAI_API_KEY",""); MODEL=os.getenv("OPENAI_MODEL","")
def answer(query):
    refs=retrieve(query,3)
    context="\n".join(f'[{x["source"]}] {x["text"]}' for x in refs)
    prompt=f"仅依据资料回答并在句末注明来源文件。\n资料：\n{context}\n\n问题：{query}"
    if not (BASE and KEY and MODEL):
        return context,[x["source"] for x in refs]
    # TODO 2-1：调用 OpenAI 兼容接口
    content=_____________
    return content,[x["source"] for x in refs]

rows=[]
for _,r in pd.read_csv("questions.csv").iterrows():
    t=time.time(); a,sources=answer(r.question)
    keys=str(r.expected_keywords).split(",")
    # TODO 3-1：关键词覆盖率
    score=_____________
    rows.append({"question":r.question,"answer":a,"sources":";".join(sources),"score":score,"latency":time.time()-t})
out=pd.DataFrame(rows); out.to_csv("rag_results.csv",index=False)
open("rag_evaluation.md","w",encoding="utf-8").write(f"# RAG 自动评测\n\n平均关键词覆盖率：{out.score.mean():.2%}\n")"""
        sol="""TfidfVectorizer()
scores.argsort()[::-1][:top_k]
requests.post(BASE.rstrip("/")+"/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}"},json={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0.1},timeout=60).json()["choices"][0]["message"]["content"]
sum(k in a for k in keys)/len(keys)"""
    write_nb(qid,title,"完成数据分析/本地模型或检索，并与 OpenAI 兼容接口组成完整项目流水线。",[code_cell(starter)])
    write_answer(qid,title,sol)

def generate(force=False):
    for qid in [f"6.1.{i}" for i in range(1,4)]+[f"6.2.{i}" for i in range(1,4)]+[f"6.3.{i}" for i in range(1,4)]+[f"6.4.{i}" for i in range(1,4)]+[f"6.5.{i}" for i in range(1,4)]:
        if force and (SRC/qid).exists(): shutil.rmtree(SRC/qid)
    gen_a1("6.1.1"); gen_a2("6.1.2"); gen_a3("6.1.3")
    gen_b("6.2.1","cluster"); gen_b("6.2.2","churn"); gen_b("6.2.3","house")
    gen_c("6.3.1",1); gen_c("6.3.2",2); gen_c("6.3.3",3)
    gen_d("6.4.1",1); gen_d("6.4.2",2); gen_d("6.4.3",3)
    gen_e("6.5.1",1); gen_e("6.5.2",2); gen_e("6.5.3",3)
    marker=SRC/".advanced_competition_v1"
    marker.write_text("generated\n",encoding="utf-8")
    print("已生成 15 道竞赛强化训练题：6.1.1 ~ 6.5.3")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--force",action="store_true",help="覆盖并重新生成 15 道强化题")
    args=ap.parse_args()
    generate(force=args.force)
