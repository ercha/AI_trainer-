# Jupyter Notebook 模拟考试说明

## 环境

本项目的实操模拟考试使用独立 Python 3.12 虚拟环境和标准 Jupyter Notebook。

- 训练系统端口：`7000`
- Jupyter Notebook 模拟考试端口：`7001`
- 虚拟环境：`.venv`
- 临时考试目录：`_exam_workspace/`
- 已提交考试记录：`_exam_history/`

## 第一次使用

1. 安装 Python 3.12。
2. 双击 `安装环境.bat`，或运行 `install_env.bat`。
3. 安装器会自动创建 `.venv`，升级 pip，并安装 `requirements.txt` 中的 Jupyter Notebook、NumPy、Pandas、scikit-learn 等实操依赖。
4. 安装完成后双击 `启动实操训练.bat`。

## 模拟考试流程

1. 打开实操训练系统，选择一道题。
2. 切换到“模拟考试”。
3. 点击“开始模拟考试”。
4. 系统把该题原始 `.ipynb` 和数据素材复制到独立考试目录。
5. 系统在 `127.0.0.1:7001` 启动标准 Jupyter Notebook，并直接打开本题 Notebook。
6. 在 Jupyter Notebook 中独立补全代码、运行 Cell、查看输出。
7. 交卷前先在 Notebook 中按 `Ctrl+S` 保存。
8. 回到训练系统点击“保存后提交考试”。
9. 系统关闭本次 Jupyter，保存考试现场，并进行自动初评。

## 自动初评

当前自动初评会检查：

- 题目关键函数/代码是否出现；
- 是否仍有大量 `_____________` 占位符；
- 代码 Cell 是否执行；
- Notebook 输出中是否存在 Error；
- 是否生成了新的结果文件。

自动分数只用于训练反馈，不等同于官方考试评分。

## 考试记录

交卷后完整工作目录会移动到：

```text
_exam_history/考试时间_题号/
```

其中会保留：

- 完成后的 `.ipynb`；
- 原始数据和生成结果；
- `jupyter.log`；
- `score.json` 自动检查结果。

## 注意

- 模拟考试进行中会隐藏函数速查和参考答案。
- 同一时间只允许进行一场模拟考试。
- 如果 `7001` 已被其他 Jupyter 服务占用，请先关闭原 Jupyter。
- 不要直接修改 `人工智能训练师三级素材/人工智能训练师三级上网素材/` 下的原题；系统会自动复制到独立考试目录。
