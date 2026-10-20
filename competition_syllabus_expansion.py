#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""正式竞赛考纲扩展题：为 A-E 每个模块补足到 5 道强化训练。

本文件只生成 6.x.4 / 6.x.5 的新增题目与素材；原 6.x.1~3 由主生成器生成。
所有素材均可离线生成，避免训练阶段依赖外部下载。
"""
from __future__ import annotations

import json
import math
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "人工智能训练师三级素材" / "人工智能训练师三级上网素材"
ANS = ROOT / "人工智能训练师三级素材" / "操作题答案"
SEED = 20261020
random.seed(SEED)
np.random.seed(SEED)


def code_cell(text):
    return {"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],
            "source":[x+"\n" for x in text.strip("\n").split("\n")]}


def md_cell(text):
    return {"cell_type":"markdown","metadata":{},
            "source":[x+"\n" for x in text.strip("\n").split("\n")]}


def write_nb(qid, title, task, cells):
    nb = {
        "cells":[md_cell(f"# {qid} {title}\n\n{task}\n\n> 按 TODO 编号补全代码。不要删除 TODO 标记。"), *cells],
        "metadata":{"kernelspec":{"display_name":"Python 3 (ipykernel)","language":"python","name":"python3"},
                    "language_info":{"name":"python","version":"3.12"}},
        "nbformat":4,"nbformat_minor":5,
    }
    p = SRC / qid
    p.mkdir(parents=True, exist_ok=True)
    (p / f"{qid}.ipynb").write_text(json.dumps(nb, ensure_ascii=False, indent=1)+"\n", encoding="utf-8")


def write_answer(qid, title, solution):
    ANS.mkdir(parents=True, exist_ok=True)
    (ANS / f"{qid}_答案.md").write_text(
        f"# {qid} {title} - 参考答案\n\n~~~python\n{solution.strip()}\n~~~\n",
        encoding="utf-8",
    )


def qdir(qid):
    p = SRC / qid
    p.mkdir(parents=True, exist_ok=True)
    return p


def gen_a4(qid):
    p = qdir(qid)
    d = p / "color_images"
    d.mkdir(exist_ok=True)
    for i in range(12):
        im = Image.new("RGB", (420, 280), (225, 225, 225))
        dr = ImageDraw.Draw(im)
        for j in range(2 + i % 3):
            x = 35 + j * 115 + (i * 13) % 35
            y = 45 + (j % 2) * 100
            dr.rectangle((x, y, x + 65, y + 55), fill=(230, 35, 35))
        for j in range(1 + (i + 1) % 3):
            x = 75 + j * 125
            y = 165 - (j % 2) * 95
            dr.ellipse((x, y, x + 55, y + 55), fill=(35, 80, 230))
        im.save(d / f"colors_{i:02d}.jpg")

    starter = """import cv2
from pathlib import Path
import pandas as pd
import numpy as np

INPUT=Path("color_images")
MASK=Path("red_masks"); VIS=Path("color_vis")
MASK.mkdir(exist_ok=True); VIS.mkdir(exist_ok=True)
rows=[]
for fp in sorted(INPUT.glob("*.jpg")):
    img=cv2.imread(str(fp))
    # TODO 1-1：BGR 转 HSV
    hsv=_____________
    # TODO 1-2：提取低色相红色区域
    low_red=_____________
    # TODO 1-3：提取高色相红色区域并合并
    high_red=_____________
    mask=cv2.bitwise_or(low_red,high_red)
    kernel=np.ones((5,5),np.uint8)
    # TODO 2-1：先开运算去噪，再闭运算连接
    clean=_____________
    contours,_=cv2.findContours(clean,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    count=0
    for c in contours:
        if cv2.contourArea(c)<500: continue
        x,y,w,h=cv2.boundingRect(c)
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        count+=1
    cv2.imwrite(str(MASK/fp.name),clean)
    cv2.imwrite(str(VIS/fp.name),img)
    rows.append({"file":fp.name,"red_objects":count,"red_pixels":int((clean>0).sum())})
pd.DataFrame(rows).to_csv("color_detection.csv",index=False)
pd.DataFrame(rows)
"""
    sol = """cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
cv2.inRange(hsv,np.array([0,100,80]),np.array([10,255,255]))
cv2.inRange(hsv,np.array([170,100,80]),np.array([180,255,255]))
cv2.morphologyEx(cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel),cv2.MORPH_CLOSE,kernel)"""
    write_nb(qid, "HSV 颜色目标提取与形态学检测",
             "使用 HSV 颜色空间提取红色目标，完成掩膜去噪、轮廓检测、目标框绘制与数量统计。",
             [code_cell(starter)])
    write_answer(qid, "HSV 颜色目标提取与形态学检测", sol)


def gen_a5(qid):
    p = qdir(qid)
    scenes = p / "template_scenes"
    scenes.mkdir(exist_ok=True)
    tpl = Image.new("RGB", (34, 34), (245, 245, 245))
    td = ImageDraw.Draw(tpl)
    td.rectangle((4, 4, 29, 29), outline=(20, 20, 20), width=3)
    td.line((8, 17, 26, 17), fill=(20, 20, 20), width=3)
    td.line((17, 8, 17, 26), fill=(20, 20, 20), width=3)
    tpl.save(p / "template.png")
    truth = []
    for i in range(12):
        im = Image.new("RGB", (360, 240), (180 + i, 195, 205))
        dr = ImageDraw.Draw(im)
        for k in range(6):
            x = 10 + (k * 51 + i * 7) % 300
            y = 12 + (k * 37 + i * 11) % 180
            dr.ellipse((x, y, x + 18, y + 18), outline=(70, 80, 90), width=2)
        x = 25 + (i * 23) % 285
        y = 35 + (i * 17) % 150
        im.paste(tpl, (x, y))
        im.save(scenes / f"scene_{i:02d}.png")
        truth.append({"file":f"scene_{i:02d}.png","x":x,"y":y,"w":34,"h":34})
    pd.DataFrame(truth).to_csv(p / "ground_truth.csv", index=False)

    starter = """import cv2
from pathlib import Path
import pandas as pd

INPUT=Path("template_scenes")
OUT=Path("template_vis"); OUT.mkdir(exist_ok=True)
template=cv2.imread("template.png",cv2.IMREAD_GRAYSCALE)
th,tw=template.shape[:2]
rows=[]
for fp in sorted(INPUT.glob("*.png")):
    img=cv2.imread(str(fp))
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # TODO 1-1：使用 TM_CCOEFF_NORMED 做模板匹配
    result=_____________
    # TODO 1-2：取得最大匹配分数和位置
    min_val,max_val,min_loc,max_loc=_____________
    x,y=max_loc
    cv2.rectangle(img,(x,y),(x+tw,y+th),(0,255,0),2)
    cv2.imwrite(str(OUT/fp.name),img)
    rows.append({"file":fp.name,"x":x,"y":y,"score":float(max_val)})
pred=pd.DataFrame(rows)
truth=pd.read_csv("ground_truth.csv")
merged=pred.merge(truth,on="file",suffixes=("_pred","_true"))
merged["center_error"]=((merged.x_pred-merged.x_true)**2+(merged.y_pred-merged.y_true)**2)**0.5
merged.to_csv("template_detection.csv",index=False)
merged
"""
    sol = """cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED)
cv2.minMaxLoc(result)"""
    write_nb(qid, "OpenCV 模板匹配目标检测",
             "使用 matchTemplate 在复杂背景中定位指定目标，输出匹配分数、目标框与定位误差。",
             [code_cell(starter)])
    write_answer(qid, "OpenCV 模板匹配目标检测", sol)


def gen_b4(qid):
    p = qdir(qid)
    rng = np.random.default_rng(SEED + 4)
    n = 720
    x1 = rng.normal(0, 1, n)
    x2 = rng.normal(0, 1, n)
    x3 = rng.normal(0, 1, n)
    x4 = rng.normal(0, 1, n)
    score = 1.4*x1 - 1.0*x2 + 0.7*x3*x4 + rng.normal(0, 0.65, n)
    y = (score > 0).astype(int)
    pd.DataFrame({"f1":x1,"f2":x2,"f3":x3,"f4":x4,"target":y}).to_csv(p/"classification.csv",index=False)

    starter = """import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score,recall_score,f1_score,confusion_matrix

df=pd.read_csv("classification.csv")
X=df.drop(columns="target"); y=df["target"]
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
# TODO 1-1：建立逻辑回归、SVM、KNN 三个分类器
models=_____________
rows=[]
for name,model in models.items():
    pipe=Pipeline([("scaler",StandardScaler()),("model",model)])
    pipe.fit(X_train,y_train)
    pred=pipe.predict(X_test)
    # TODO 2-1：准确率
    acc=_____________
    # TODO 2-2：召回率
    recall=_____________
    # TODO 2-3：F1
    f1=_____________
    tn,fp,fn,tp=confusion_matrix(y_test,pred).ravel()
    rows.append({"model":name,"accuracy":acc,"recall":recall,"f1":f1,
                 "tn":tn,"fp":fp,"fn":fn,"tp":tp})
result=pd.DataFrame(rows).sort_values("f1",ascending=False)
result.to_csv("classifier_comparison.csv",index=False)
result
"""
    sol = """{"LogisticRegression":LogisticRegression(max_iter=1000),"SVM":SVC(),"KNN":KNeighborsClassifier(n_neighbors=7)}
accuracy_score(y_test,pred)
recall_score(y_test,pred)
f1_score(y_test,pred)"""
    write_nb(qid, "逻辑回归、SVM 与 KNN 分类器对比",
             "对同一二分类数据完成标准化、训练、预测，并使用准确率、召回率、F1 和混淆矩阵比较三种分类器。",
             [code_cell(starter)])
    write_answer(qid, "逻辑回归、SVM 与 KNN 分类器对比", sol)


def gen_b5(qid):
    p = qdir(qid)
    rng = np.random.default_rng(SEED + 5)
    centers = np.array([[-3,-2,0,1],[0,3,2,-1],[3,-1,-2,2]], dtype=float)
    X = np.vstack([rng.normal(c, .7, size=(150,4)) for c in centers])
    noise = rng.uniform(-6,6,size=(30,4))
    X = np.vstack([X,noise])
    pd.DataFrame(X,columns=["x1","x2","x3","x4"]).to_csv(p/"cluster_features.csv",index=False)

    starter = """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans,AgglomerativeClustering,DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

df=pd.read_csv("cluster_features.csv")
# TODO 1-1：标准化
X=_____________
# TODO 1-2：建立四种聚类算法
models=_____________
rows=[]; labels_all={}
for name,model in models.items():
    labels=model.fit_predict(X)
    labels_all[name]=labels
    valid=labels!=-1
    unique=np.unique(labels[valid])
    score=silhouette_score(X[valid],labels[valid]) if valid.sum()>2 and len(unique)>1 else float("nan")
    rows.append({"model":name,"clusters":len(unique),"silhouette":score,"noise":int((labels==-1).sum())})
comparison=pd.DataFrame(rows)
comparison.to_csv("cluster_comparison.csv",index=False)

# TODO 2-1：PCA 降到二维
pca_xy=_____________
# TODO 2-2：t-SNE 降到二维
tsne_xy=_____________
out=df.copy()
out["kmeans"]=labels_all["KMeans"]
out["dbscan"]=labels_all["DBSCAN"]
out["pca_x"],out["pca_y"]=pca_xy[:,0],pca_xy[:,1]
out["tsne_x"],out["tsne_y"]=tsne_xy[:,0],tsne_xy[:,1]
out.to_csv("cluster_results.csv",index=False)
fig,ax=plt.subplots(1,2,figsize=(11,4))
ax[0].scatter(pca_xy[:,0],pca_xy[:,1],c=labels_all["KMeans"],s=12); ax[0].set_title("PCA")
ax[1].scatter(tsne_xy[:,0],tsne_xy[:,1],c=labels_all["KMeans"],s=12); ax[1].set_title("t-SNE")
plt.tight_layout(); plt.savefig("pca_tsne.png",dpi=150)
comparison
"""
    sol = """StandardScaler().fit_transform(df)
{"KMeans":KMeans(n_clusters=3,random_state=42,n_init=10),"Agglomerative":AgglomerativeClustering(n_clusters=3),"DBSCAN":DBSCAN(eps=.8,min_samples=6),"GMM":GaussianMixture(n_components=3,random_state=42)}
PCA(n_components=2).fit_transform(X)
TSNE(n_components=2,random_state=42,perplexity=30,init="pca",learning_rate="auto").fit_transform(X)"""
    write_nb(qid, "多聚类算法与 PCA/t-SNE 可视化",
             "比较 K-Means、层次聚类、DBSCAN、高斯混合模型，并使用 PCA 与 t-SNE 对高维样本进行二维可视化。",
             [code_cell(starter)])
    write_answer(qid, "多聚类算法与 PCA/t-SNE 可视化", sol)


def gen_c4(qid):
    p = qdir(qid)
    imgs = p/"detection_images"; imgs.mkdir(exist_ok=True)
    anns=[]; preds=[]
    yolo_dir=p/"yolo_labels"; yolo_dir.mkdir(exist_ok=True)
    rng=np.random.default_rng(SEED+34)
    for i in range(10):
        im=Image.new("RGB",(128,128),(35,45,55))
        dr=ImageDraw.Draw(im)
        x1=int(rng.integers(12,55)); y1=int(rng.integers(12,55))
        w=int(rng.integers(35,55)); h=int(rng.integers(30,50))
        x2=min(x1+w,120); y2=min(y1+h,120)
        dr.rectangle((x1,y1,x2,y2),fill=(220,150,40))
        name=f"det_{i:02d}.png"; im.save(imgs/name)
        anns.append({"file":name,"x1":x1,"y1":y1,"x2":x2,"y2":y2})
        cx=((x1+x2)/2)/128; cy=((y1+y2)/2)/128
        nw=(x2-x1)/128; nh=(y2-y1)/128
        (yolo_dir/f"{Path(name).stem}.txt").write_text(f"0 {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")
        dx=int(rng.integers(-5,6)); dy=int(rng.integers(-5,6))
        preds.append({"file":name,"x1":max(0,x1+dx),"y1":max(0,y1+dy),
                      "x2":min(127,x2+dx),"y2":min(127,y2+dy),"score":float(rng.uniform(.75,.98))})
    pd.DataFrame(anns).to_csv(p/"annotations.csv",index=False)
    pd.DataFrame(preds).to_csv(p/"baseline_predictions.csv",index=False)

    starter = """import json
import cv2
import pandas as pd
import torch
from torchvision.transforms.functional import to_tensor
from torchvision.models.detection import fasterrcnn_mobilenet_v3_large_320_fpn

ann=pd.read_csv("annotations.csv")

def read_yolo_label(image_file):
    cls,cx,cy,w,h=map(float,open("yolo_labels/"+image_file.replace(".png",".txt")).read().split())
    # TODO 1-1：将 YOLO 归一化 cx,cy,w,h 转为像素 xyxy
    return _____________

yolo_boxes=[read_yolo_label(x) for x in ann.file]
# TODO 1-2：创建不下载预训练权重的 Faster R-CNN，两类（背景+目标）
model=_____________
model.train()
row=ann.iloc[0]
img=cv2.cvtColor(cv2.imread("detection_images/"+row.file),cv2.COLOR_BGR2RGB)
x=to_tensor(img)
target={"boxes":torch.tensor([[row.x1,row.y1,row.x2,row.y2]],dtype=torch.float32),
        "labels":torch.tensor([1],dtype=torch.int64)}
# TODO 1-3：SGD 优化器
optimizer=_____________
losses=model([x],[target])
# TODO 1-4：合计检测损失
loss=_____________
optimizer.zero_grad(); loss.backward(); optimizer.step()

def iou(a,b):
    ix1=max(a[0],b[0]); iy1=max(a[1],b[1]); ix2=min(a[2],b[2]); iy2=min(a[3],b[3])
    # TODO 2-1：交集面积
    inter=_____________
    area_a=max(0,a[2]-a[0])*max(0,a[3]-a[1]); area_b=max(0,b[2]-b[0])*max(0,b[3]-b[1])
    return inter/max(area_a+area_b-inter,1e-9)

pred=pd.read_csv("baseline_predictions.csv")
m=ann.merge(pred,on="file",suffixes=("_true","_pred"))
m["iou"]=[iou([r.x1_true,r.y1_true,r.x2_true,r.y2_true],[r.x1_pred,r.y1_pred,r.x2_pred,r.y2_pred]) for _,r in m.iterrows()]
ap50=float((m.iou>=.5).mean())
metrics={"training_loss":float(loss.detach()),"AP50":ap50,"mean_iou":float(m.iou.mean())}
open("detection_metrics.json","w").write(json.dumps(metrics,indent=2))
r=m.iloc[0]; vis=cv2.imread("detection_images/"+r.file)
cv2.rectangle(vis,(int(r.x1_true),int(r.y1_true)),(int(r.x2_true),int(r.y2_true)),(0,255,0),2)
cv2.rectangle(vis,(int(r.x1_pred),int(r.y1_pred)),(int(r.x2_pred),int(r.y2_pred)),(0,0,255),2)
cv2.imwrite("detection_preview.png",vis)
metrics
"""
    sol = """[(cx-w/2)*128,(cy-h/2)*128,(cx+w/2)*128,(cy+h/2)*128]
fasterrcnn_mobilenet_v3_large_320_fpn(weights=None,weights_backbone=None,num_classes=2,min_size=128,max_size=128)
torch.optim.SGD(model.parameters(),lr=0.001,momentum=0.9)
sum(losses.values())
max(0,ix2-ix1)*max(0,iy2-iy1)"""
    write_nb(qid, "YOLO 标注、Faster R-CNN 目标检测与 AP50",
             "掌握 YOLO 归一化标注格式与 xyxy 转换，并使用 torchvision Faster R-CNN 完成检测模型构建、一次训练更新、IoU/AP50 和可视化。",
             [code_cell(starter)])
    write_answer(qid, "YOLO 标注、Faster R-CNN 目标检测与 AP50", sol)


def gen_c5(qid):
    p=qdir(qid)
    imgs=p/"seg_images"; masks=p/"seg_masks"; imgs.mkdir(exist_ok=True); masks.mkdir(exist_ok=True)
    rng=np.random.default_rng(SEED+35)
    for i in range(48):
        im=Image.new("L",(64,64),20); mk=Image.new("L",(64,64),0)
        di=ImageDraw.Draw(im); dm=ImageDraw.Draw(mk)
        x=int(rng.integers(8,30)); y=int(rng.integers(8,30)); w=int(rng.integers(18,30)); h=int(rng.integers(18,30))
        di.ellipse((x,y,x+w,y+h),fill=200); dm.ellipse((x,y,x+w,y+h),fill=255)
        noise=rng.normal(0,10,(64,64)).astype(np.int16)
        arr=np.clip(np.array(im,dtype=np.int16)+noise,0,255).astype(np.uint8)
        Image.fromarray(arr).save(imgs/f"seg_{i:03d}.png"); mk.save(masks/f"seg_{i:03d}.png")

    starter = """import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.utils.data import TensorDataset,DataLoader
from torchvision.models.segmentation import deeplabv3_resnet50
from PIL import Image

X=np.stack([np.array(Image.open(p),dtype=np.float32)/255 for p in sorted(Path("seg_images").glob("*.png"))])[:,None]
Y=np.stack([np.array(Image.open(p),dtype=np.float32)/255 for p in sorted(Path("seg_masks").glob("*.png"))])[:,None]
loader=DataLoader(TensorDataset(torch.tensor(X),torch.tensor(Y)),batch_size=8,shuffle=True)

class TinyUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.e1=nn.Sequential(nn.Conv2d(1,16,3,padding=1),nn.ReLU(),nn.Conv2d(16,16,3,padding=1),nn.ReLU())
        self.pool=nn.MaxPool2d(2)
        self.e2=nn.Sequential(nn.Conv2d(16,32,3,padding=1),nn.ReLU())
        # TODO 1-1：2 倍上采样 32→16
        self.up=_____________
        self.out=nn.Conv2d(32,1,1)
    def forward(self,x):
        e1=self.e1(x); e2=self.e2(self.pool(e1)); u=self.up(e2)
        # TODO 1-2：跳跃连接
        z=_____________
        return self.out(z)

model=TinyUN()
# TODO 1-3：二值分割损失
criterion=_____________
optimizer=torch.optim.Adam(model.parameters(),lr=0.003)
for epoch in range(4):
    for x,y in loader:
        optimizer.zero_grad(); logits=model(x); loss=criterion(logits,y); loss.backward(); optimizer.step()

with torch.no_grad():
    pred=(torch.sigmoid(model(torch.tensor(X[:8])))>.5).float()
    truth=torch.tensor(Y[:8])
    inter=(pred*truth).sum().item(); union=((pred+truth)>0).sum().item()
    iou=inter/max(union,1)
# TODO 1-4：创建不下载权重的 DeepLabV3（二分类）
deeplab=_____________
deeplab.eval()
with torch.inference_mode():
    deeplab_shape=list(deeplab(torch.tensor(np.repeat(X[:1],3,axis=1)))["out"].shape)
json.dump({"mean_iou":iou,"deeplab_output_shape":deeplab_shape},open("segmentation_metrics.json","w"),indent=2)
fig,ax=plt.subplots(2,3,figsize=(8,5))
for i in range(3):
    ax[0,i].imshow(X[i,0],cmap="gray"); ax[0,i].axis("off")
    ax[1,i].imshow(pred[i,0],cmap="gray"); ax[1,i].axis("off")
plt.tight_layout(); plt.savefig("segmentation_preview.png",dpi=150)

# 轻量 GAN：学习 16×16 掩膜分布，训练少量步骤用于熟悉生成流程
real=torch.nn.functional.interpolate(torch.tensor(Y),size=(16,16)).flatten(1)
G=nn.Sequential(nn.Linear(32,128),nn.ReLU(),nn.Linear(128,256),nn.Sigmoid())
D=nn.Sequential(nn.Linear(256,64),nn.LeakyReLU(.2),nn.Linear(64,1),nn.Sigmoid())
# TODO 2-1：GAN 二分类损失
bce=_____________
go=torch.optim.Adam(G.parameters(),lr=.002); do=torch.optim.Adam(D.parameters(),lr=.002)
for step in range(40):
    idx=torch.randint(0,len(real),(16,)); rb=real[idx]
    z=torch.randn(16,32); fake=G(z)
    do.zero_grad(); dl=bce(D(rb),torch.ones(16,1))+bce(D(fake.detach()),torch.zeros(16,1)); dl.backward(); do.step()
    go.zero_grad(); fake=G(torch.randn(16,32)); gl=bce(D(fake),torch.ones(16,1)); gl.backward(); go.step()
with torch.no_grad(): samples=G(torch.randn(9,32)).reshape(-1,16,16).numpy()
fig,ax=plt.subplots(3,3,figsize=(5,5))
for a,s in zip(ax.ravel(),samples): a.imshow(s,cmap="gray"); a.axis("off")
plt.tight_layout(); plt.savefig("gan_samples.png",dpi=150)
print({"IoU":iou,"G_loss":float(gl.detach()),"D_loss":float(dl.detach())})
"""
    sol = """nn.ConvTranspose2d(32,16,2,stride=2)
torch.cat([u,e1],dim=1)
nn.BCEWithLogitsLoss()
deeplabv3_resnet50(weights=None,weights_backbone=None,num_classes=2)
nn.BCELoss()"""
    write_nb(qid, "U-Net/DeepLab 语义分割与轻量 GAN 图像生成",
             "在本地合成数据上完成 U-Net 跳跃连接与 IoU 评估，掌握 DeepLabV3 离线模型调用，并训练轻量 GAN 生成掩膜样本。",
             [code_cell(starter)])
    write_answer(qid, "U-Net/DeepLab 语义分割与轻量 GAN 图像生成", sol)


def gen_d4(qid):
    p=qdir(qid)
    ner_rows=[
        ("张伟今天到北京大学参加会议","张伟|北京大学"),
        ("李娜从上海前往杭州阿里巴巴园区","李娜|上海|杭州|阿里巴巴"),
        ("王强在深圳腾讯公司负责项目","王强|深圳|腾讯"),
        ("陈晨计划去南京大学交流","陈晨|南京大学"),
        ("刘洋在广州参加华为技术论坛","刘洋|广州|华为"),
    ]
    pd.DataFrame(ner_rows,columns=["text","expected"]).to_csv(p/"ner_texts.csv",index=False)
    pairs=[
        ("我 喜欢 苹果","i like apples"),("我 喜欢 音乐","i like music"),
        ("他 学习 Python","he studies python"),("她 学习 人工智能","she studies ai"),
        ("我们 去 学校","we go school"),("他们 去 北京","they go beijing"),
        ("今天 天气 很好","today weather good"),("机器 学习 很 有趣","machine learning is interesting"),
    ]
    pd.DataFrame(pairs,columns=["zh","en"]).to_csv(p/"translation_pairs.csv",index=False)

    starter = """import json
import pandas as pd
import numpy as np
import jieba.posseg as pseg
import torch
from torch import nn
from nltk.translate.bleu_score import sentence_bleu,SmoothingFunction

ner=pd.read_csv("ner_texts.csv")
def extract_entities(text):
    # TODO 1-1：jieba 词性标注
    words=_____________
    # nr 人名、ns 地名、nt 机构
    return [w.word for w in words if w.flag in {"nr","ns","nt"}]
ner["entities"]=ner.text.apply(lambda s:"|".join(extract_entities(s)))
ner.to_csv("ner_results.csv",index=False)

pairs=pd.read_csv("translation_pairs.csv")
chars=sorted(set("".join(pairs.zh.tolist()).replace(" ","")))
stoi={c:i+1 for i,c in enumerate(chars)}
max_len=max(len(x.replace(" ","")) for x in pairs.zh)
def encode(s):
    ids=[stoi[c] for c in s.replace(" ","")]
    return ids+[0]*(max_len-len(ids))
X=torch.tensor([encode(s) for s in pairs.zh],dtype=torch.long)
y=torch.arange(len(pairs))

class Translator(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb=nn.Embedding(len(stoi)+1,32,padding_idx=0)
        # TODO 2-1：TransformerEncoderLayer，4 个注意力头
        layer=_____________
        self.enc=nn.TransformerEncoder(layer,num_layers=2)
        self.fc=nn.Linear(32,len(pairs))
    def forward(self,x):
        z=self.enc(self.emb(x))
        mask=(x!=0).float().unsqueeze(-1)
        pooled=(z*mask).sum(1)/mask.sum(1).clamp_min(1)
        return self.fc(pooled)

model=Translator()
# TODO 2-2：交叉熵损失
loss_fn=_____________
opt=torch.optim.Adam(model.parameters(),lr=.01)
for epoch in range(120):
    opt.zero_grad(); out=model(X); loss=loss_fn(out,y); loss.backward(); opt.step()
pred=model(X).argmax(1).tolist()
rows=[]
smooth=SmoothingFunction().method1
for i,pid in enumerate(pred):
    ref=pairs.iloc[i].en.split(); hyp=pairs.iloc[pid].en.split()
    # TODO 3-1：计算 BLEU-2
    bleu=_____________
    rows.append({"source":pairs.iloc[i].zh,"reference":pairs.iloc[i].en,
                 "prediction":pairs.iloc[pid].en,"bleu2":bleu})
out=pd.DataFrame(rows)
out.to_csv("translation_results.csv",index=False)
print("平均 BLEU-2",out.bleu2.mean())
"""
    sol = """list(pseg.cut(text))
nn.TransformerEncoderLayer(d_model=32,nhead=4,batch_first=True)
nn.CrossEntropyLoss()
sentence_bleu([ref],hyp,weights=(0.5,0.5),smoothing_function=smooth)"""
    write_nb(qid, "命名实体识别与 Transformer 翻译/BLEU",
             "使用 jieba 词性完成中文实体提取，并构建离线小样本 Transformer 编码器完成中英短句翻译流程与 BLEU-2 评估。",
             [code_cell(starter)])
    write_answer(qid, "命名实体识别与 Transformer 翻译/BLEU", sol)


def gen_d5(qid):
    p=qdir(qid)
    tasks=[
        {"task":"summary","prompt":"学校上线新的AI实训平台，支持课程资源、在线练习、自动评分和学习分析，请生成一句摘要。",
         "reference":"学校上线支持练习、评分和学习分析的AI实训平台"},
        {"task":"summary","prompt":"图书馆延长开放时间并新增自助借还设备，方便学生晚间学习，请生成一句摘要。",
         "reference":"图书馆延长开放并新增自助借还设备"},
        {"task":"dialogue","prompt":"学生：我的校园卡丢了怎么办？请用客服口吻回复。",
         "reference":"请尽快挂失校园卡，并到服务中心补办"},
        {"task":"dialogue","prompt":"学生：忘记教务系统密码怎么办？请用客服口吻回复。",
         "reference":"请通过密码找回功能重置，无法处理时联系教务服务中心"},
        {"task":"poem","prompt":"以校园秋天为主题写两句短诗。",
         "reference":"秋风轻过校园路，金叶满阶伴书声"},
    ]
    pd.DataFrame(tasks).to_csv(p/"generation_tasks.csv",index=False)

    starter = """import os,json,requests
import pandas as pd

df=pd.read_csv("generation_tasks.csv")
BASE=os.getenv("OPENAI_BASE_URL",""); KEY=os.getenv("OPENAI_API_KEY",""); MODEL=os.getenv("OPENAI_MODEL","")

def call_gpt(prompt):
    if not (BASE and KEY and MODEL):
        return prompt.split("，")[0][:32]
    # TODO 1-1：调用 OpenAI 兼容 chat/completions
    r=_____________
    r.raise_for_status()
    # TODO 1-2：提取生成文本
    return _____________

def lcs(a,b):
    m,n=len(a),len(b); dp=[[0]*(n+1) for _ in range(m+1)]
    for i in range(m):
        for j in range(n):
            dp[i+1][j+1]=dp[i][j]+1 if a[i]==b[j] else max(dp[i][j+1],dp[i+1][j])
    return dp[m][n]

def rouge_l(pred,ref):
    common=lcs(pred,ref)
    p=common/max(len(pred),1); r=common/max(len(ref),1)
    # TODO 2-1：ROUGE-L F1
    return _____________

rows=[]
for _,r in df.iterrows():
    ans=call_gpt(r.prompt)
    rows.append({"task":r.task,"prompt":r.prompt,"reference":r.reference,
                 "answer":ans,"rouge_l":rouge_l(ans,r.reference)})
out=pd.DataFrame(rows)
out.to_csv("generation_results.csv",index=False)
report={"average_rouge_l":float(out.rouge_l.mean()),
        "by_task":out.groupby("task").rouge_l.mean().to_dict()}
open("rouge_report.json","w",encoding="utf-8").write(json.dumps(report,ensure_ascii=False,indent=2))
report
"""
    sol = """requests.post(BASE.rstrip("/")+"/v1/chat/completions",headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},json={"model":MODEL,"messages":[{"role":"user","content":prompt}],"temperature":0.3},timeout=60)
r.json()["choices"][0]["message"]["content"]
0 if p+r==0 else 2*p*r/(p+r)"""
    write_nb(qid, "GPT 文本摘要、对话/诗歌生成与 ROUGE",
             "调用 OpenAI 兼容 GPT 接口完成摘要、对话回复和诗歌生成，并实现 ROUGE-L 自动评价；未配置 API 时保留离线基线。",
             [code_cell(starter)])
    write_answer(qid, "GPT 文本摘要、对话/诗歌生成与 ROUGE", sol)


def gen_e4(qid):
    p=qdir(qid)
    rng=np.random.default_rng(SEED+54)
    n=240; seq=16; vocab=128
    ids=rng.integers(5,vocab,size=(n,seq),dtype=np.int64)
    labels=((ids[:,:4].mean(1)+ids[:,4:8].mean(1))>125).astype(np.int64)
    np.savez(p/"lora_train.npz",input_ids=ids,attention_mask=np.ones_like(ids),labels=labels)

    starter = """import json,time
import numpy as np
import pandas as pd
import torch
from transformers import BertConfig,BertForSequenceClassification
from peft import LoraConfig,get_peft_model

data=np.load("lora_train.npz")
ids=torch.tensor(data["input_ids"],dtype=torch.long)
mask=torch.tensor(data["attention_mask"],dtype=torch.long)
labels=torch.tensor(data["labels"],dtype=torch.long)
config=BertConfig(vocab_size=128,hidden_size=48,num_hidden_layers=2,num_attention_heads=4,
                  intermediate_size=96,num_labels=2,max_position_embeddings=64)
base=BertForSequenceClassification(config)
# TODO 1-1：LoRA 配置，分类任务，r=4，作用于 query/value
lora_cfg=_____________
# TODO 1-2：包装为 PEFT 模型
model=_____________
trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
total=sum(p.numel() for p in model.parameters())
opt=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),lr=.01)
model.train()
for epoch in range(5):
    order=torch.randperm(len(ids))
    for start in range(0,len(ids),32):
        idx=order[start:start+32]
        out=model(input_ids=ids[idx],attention_mask=mask[idx],labels=labels[idx])
        opt.zero_grad(); out.loss.backward(); opt.step()
model.eval()
with torch.inference_mode():
    pred=model(input_ids=ids,attention_mask=mask).logits.argmax(1)
acc=float((pred==labels).float().mean())
model.save_pretrained("lora_adapter")

def benchmark(batch):
    loops=20
    t0=time.perf_counter()
    with torch.inference_mode():
        for _ in range(loops):
            model(input_ids=ids[:batch],attention_mask=mask[:batch])
    elapsed=time.perf_counter()-t0
    # TODO 2-1：吞吐量 samples/s
    throughput=_____________
    return {"batch":batch,"latency_ms":elapsed/loops*1000,"throughput":throughput}

bench=pd.DataFrame([benchmark(1),benchmark(8),benchmark(32)])
bench.to_csv("benchmark.csv",index=False)
metrics={"accuracy":acc,"trainable_params":trainable,"total_params":total,
         "trainable_ratio":trainable/total}
open("lora_metrics.json","w").write(json.dumps(metrics,indent=2))
metrics,bench
"""
    sol = """LoraConfig(r=4,lora_alpha=8,lora_dropout=0.05,target_modules=["query","value"],task_type="SEQ_CLS")
get_peft_model(base,lora_cfg)
batch*loops/elapsed"""
    write_nb(qid, "LoRA/PEFT 微调与推理性能评测",
             "使用本地随机初始化的小型 BERT 完成 LoRA/PEFT 参数高效微调，统计可训练参数比例、准确率、延迟与吞吐量，全程无需下载模型。",
             [code_cell(starter)])
    write_answer(qid, "LoRA/PEFT 微调与推理性能评测", sol)


def gen_e5(qid):
    p=qdir(qid)
    kd=p/"knowledge_docs"; kd.mkdir(exist_ok=True)
    docs={
        "请假制度.txt":"学生请假需提前提交申请。一天以内由班主任审批，超过一天需要系部审批。紧急情况可先电话报备后补手续。",
        "机房制度.txt":"进入机房不得携带饮料。上机必须使用本人账号，禁止安装无关软件。发现设备故障应立即报告教师。",
        "奖学金制度.txt":"综合成绩排名前10%的学生可申请一等奖学金，前25%可申请二等奖学金，同时要求本学期无纪律处分。",
    }
    for name,txt in docs.items(): (kd/name).write_text(txt,encoding="utf-8")
    qs=[
        ("请假两天由谁审批？","系部审批"),
        ("机房能不能带饮料？","不得携带饮料"),
        ("一等奖学金排名要求是什么？","前10%"),
    ]
    pd.DataFrame(qs,columns=["question","expected"]).to_csv(p/"eval_questions.csv",index=False)

    starter = '''import os,time,json
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

chunks=[]
for fp in Path("knowledge_docs").glob("*.txt"):
    for text in fp.read_text(encoding="utf-8").splitlines():
        if text.strip(): chunks.append({"source":fp.name,"text":text.strip()})
texts=[x["text"] for x in chunks]
# TODO 1-1：建立 TF-IDF 检索矩阵
vectorizer=_____________; matrix=vectorizer.fit_transform(texts)

def retrieve(query,k=2):
    q=vectorizer.transform([query]); score=cosine_similarity(q,matrix)[0]
    # TODO 1-2：按相似度取 Top-K
    idx=_____________
    return [chunks[i] for i in idx]

def answer(query):
    refs=retrieve(query,2)
    context="\\n".join(f"[{x['source']}] {x['text']}" for x in refs)
    return context

eval_df=pd.read_csv("eval_questions.csv")
rows=[]
for _,r in eval_df.iterrows():
    t=time.perf_counter(); ans=answer(r.question); dt=time.perf_counter()-t
    rows.append({"question":r.question,"answer":ans,"correct":int(r.expected in ans),"latency_ms":dt*1000})
result=pd.DataFrame(rows)
# TODO 2-1：每秒可处理查询数
throughput=_____________
pd.DataFrame([{"accuracy":result.correct.mean(),"avg_latency_ms":result.latency_ms.mean(),
               "throughput_qps":throughput}]).to_csv("benchmark.csv",index=False)

APP = """from pathlib import Path
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

chunks=[]
for fp in Path('knowledge_docs').glob('*.txt'):
    text=fp.read_text(encoding='utf-8')
    chunks.append((fp.name,text))
vec=TfidfVectorizer(); mat=vec.fit_transform([x[1] for x in chunks])

def ask():
    q=entry.get().strip()
    s=cosine_similarity(vec.transform([q]),mat)[0]
    i=int(s.argmax())
    output.delete('1.0',tk.END)
    output.insert(tk.END,f'来源：{chunks[i][0]}\\\\n\\\\n{chunks[i][1]}')

root=tk.Tk(); root.title('智慧校园制度问答')
entry=tk.Entry(root,width=70); entry.pack(padx=12,pady=8)
tk.Button(root,text='查询',command=ask).pack()
output=ScrolledText(root,width=76,height=16); output.pack(padx=12,pady=8)
root.mainloop()
"""
Path("app.py").write_text(APP,encoding="utf-8")
Path("README.md").write_text("""# 智慧校园制度问答原型

## 功能
- 本地制度文档检索
- Top-K 相关内容返回
- Tkinter 图形界面
- benchmark.csv 提供准确率、平均响应时间和吞吐量

## 运行
python app.py

## 可复现性
素材位于 knowledge_docs，评测问题位于 eval_questions.csv。
""",encoding="utf-8")
result.to_csv("evaluation_results.csv",index=False)
print(result)
'''
    sol = """TfidfVectorizer()
score.argsort()[::-1][:k]
len(result)/(result.latency_ms.sum()/1000)"""
    write_nb(qid, "智慧校园 AI 原型：需求、检索、界面、性能与交付",
             "完成一个可复现的智慧校园制度问答原型：本地知识检索、自动评测、响应时间/吞吐量统计、Tkinter 界面和 README 交付文档。",
             [code_cell(starter)])
    write_answer(qid, "智慧校园 AI 原型：需求、检索、界面、性能与交付", sol)


def generate_expanded_questions():
    gen_a4("6.1.4"); gen_a5("6.1.5")
    gen_b4("6.2.4"); gen_b5("6.2.5")
    gen_c4("6.3.4"); gen_c5("6.3.5")
    gen_d4("6.4.4"); gen_d5("6.4.5")
    gen_e4("6.5.4"); gen_e5("6.5.5")


if __name__ == "__main__":
    generate_expanded_questions()
