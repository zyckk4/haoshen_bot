# haoshen_bot
[![Licence](https://img.shields.io/github/license/zyckk4/haoshen_bot)](https://github.com/zyckk4/haoshen_bot/blob/master/LICENSE)

**haoshen_bot**（豪神豪神）是一个基于[YiriMirai](https://github.com/YiriMiraiProject/YiriMirai)的多功能QQ机器人。

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

# 功能简介
游戏功能：下各种棋，扫雷，wordle，24点，数织，抢答单词和日语假名，等等，并计算金币经验，参与群富豪榜排名；

学习功能：百度百科，在线编程，Wolfram|Alpha请求，LaTeX图片生成，oeis数列搜索，等等；

生活休闲：数十种趣味/实用小功能，例如趣味图片制作，高德地图api，搜索MCwiki和MC模组，自动生成狗屁不通文章、申论，获取知乎、微博热搜，等等；

q群管理：可选开启复读禁言，可以帮助管理员禁言。

在qq群内输入"/help"即可查看所有功能

# 常见问题

## 1.cariosvg报错

若您在首次部署本bot时出现cariosvg报错：
```
OSError: no library called "cairo" was found
no library called "libcairo-2" was found
cannot load library 'libcairo.so': error 0x7e
cannot load library 'libcairo.2.dylib': error 0x7e
cannot load library 'libcairo-2.dll': error 0x7e
```
这是因为缺少gtk2环境，可以用链接：

https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2021-01-30/gtk2-runtime-2.24.33-2021-01-30-ts-win64.exe

下载，或者假如您不使用相关功能的话，注释掉mychess.py下cariosvg相关代码即可

## 2.Real-ESRGAN报错

本项目用到了[Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)来进行图像超分，您需要根据该项目的要求下载对应代码，并下载模型到statics文件夹下，或者您可以将super_resolution.py移除或改名为__super_resolution.py以禁用本功能

# 代码说明
项目基于yirimirai，并进一步做了一些封装

优点：

1.结构清晰方便继续开发

2.各功能开关方便，只需把想关闭的功能对应的.py文件删除，或者在名字前加上“ __ “即可

# 开发计划
进一步优化、调整代码

玩家数据存储优化，考虑不再使用表格存储

添加更多趣味功能

# 联系方式
qq群: 758960240

项目尚不完善，可能有很多bug，欢迎提出问题或建议，可以加群联系或者提issue和pr
