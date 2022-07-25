# haoshen_bot
一个基于[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai)的多功能QQ机器人

# 如何使用

## 1.安装mirai

首先，需要先安装 mirai-console 和 mirai-api-http，在mcl登录qq，并修改mirai-api-http的配置文件

建议参考 YiriMirai 官方文档的[环境配置](https://yiri-mirai.vercel.app/tutorials/01/configuration)。

## 2.配置python环境

建议使用python3.9版本，建议创建虚拟环境方便管理，下面以anaconda为例

第一步，进入终端，输入

```
conda create --name haoshen_bot python==3.9.7
y
conda activate haoshen_bot
```

创建一个名为haoshen_bot的虚拟环境并进入

第二步，下载源代码，或使用

```git clone https://github.com/zyckk4/haoshen_bot.git```

若没有git可以先使用```conda install git```

第三步，安装所需库

```
cd haoshen_bot
pip install -r requirements.txt
```

## 3.运行bot

打开config/config.yml，填写相关配置

填写完并保存后，确保mcl中已登录机器人qq，然后在终端输入```python main.py```运行即可
