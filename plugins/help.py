# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from mirai import GroupMessage
from utils.utils import Listen, send
from utils.text_engine import text_to_img


help_mesg = '''豪神豪神功能列表

以下是python实现,mirai插件功能请输入'/插件'查看
1.输入'报时'以报时\n2.试试戳戳我
3./百科,/oeis.或/mcwiki+你想搜索的内容，查看相应内容,输入//+链接名可以追加点击图中的一个链接
4./纯几何吧,/纯几何吧人,/纯几何吧签+内容以搜索纯几何吧的帖子.输入//+链接名可以追加点击图中的一个链接
5./latex+LaTeX代码可以生成LaTeX图片
6.多项式功能./hm+多项式生成热图，/tri+多项式生成系数阵
7.在线编程.输入/+<R,vb,ts,kt,pas,lua,node.js,go,swift,rs,sh,pl,erl,scala,cs,rb,cpp,c,java,py3,py,php>以开始.
如果程序需要输入，请在代码前面添加一行“输入：+你想输入的内容”(是中文冒号)
8.'/缩',拼音缩写查询
9.'/抽象',把你的话翻译成抽象话
10.'/ETC'+数字，看某特征点的信息；'/查ETC preci=<精度>,'+数字，进行6_9_13搜索
11./制图或/制图b +文字+图片在图片底部加文字；/精神支柱+at或图片,/低语,/狂粉或/喜报+图片,制作特色图片.
12.高德地图功能。/经纬+某地查询某地经纬度；/天气或/天气预报+某市/区/县，查询当前天气和天气预报
13.输入/对联+上联，机器自动对下联
14./pin+一张图片，将图片钉在群上,输入看pin,删pin来查看,删除
15.输入/日报,获取每日新闻
16.输入/作诗,/作诗7,/藏头诗或/词+主题，机器自动作诗词
17./知乎热榜或/微博热榜，查看当前热搜
18./zen获取github禅语
19.“来点(美国/法国/苏联/xx)笑话"
20./cp a b,生成cp文
21./mcmod+模组名,搜索我的世界模组
22.MC音乐功能.输入/mcr查看音乐列表;/mcr+音乐名,发送音乐
23./舔,生成舔狗日记
24./幻影坦克+两张图片制作幻影坦克
25./毒鸡汤,获取毒鸡汤语句
26./二维码+文本(可以是链接),生成二维码
27./来个老婆,生成随机二次元老婆
28.'来张涩图'
29./屁文+主题生成狗屁不通文章;/申论+主题生成申论文
30.丢骰子功能.输入“丢色子”或“丢骰子”丢随机点数的骰子.输入“丢+数字”丢指定点数的骰子
31.游戏已上线！！！输入"/游戏"或'/game'查看帮助
32.更多功能等你探索!'''

mirai_plugins_mesg = '''#插件指令列表：
插件1：#ph,#bw,#5k兆,#0,#osu,#marble,#flash,#erode,emoji合成;
插件2：/pet;
插件3：锤,贴,踢,打,抱,踩;
插件4：#音乐,#语音,#外链,#QQ,#网易,#网易电台,#酷狗,#千千;
#插件详情信息：
插件1,DrawMeme - 基于Skiko的奇怪的图片生成器,(https://github.com/LaoLittle/DrawMeme)
插件2,Petpet - 生成各种奇怪的图片,(https://github.com/Dituon/petpet)
插件3,HitHit锤人插件,(https://gitee.com/arisaka-iris/hithit)
插件4,Mirai点歌插件,(https://github.com/khjxiaogu/MiraiSongPlugin)
请支持插件原作者！'''

repo_info = '''项目地址：
https://github.com/zyckk4/haoshen_bot
如果觉得好可以点个star⭐，如出现bug，或您有任何建议，欢迎反馈！'''

plugin = Listen(
    'help',
    r'帮助'
)


@plugin.group()
async def help_info(event: GroupMessage):
    if str(event.message_chain) == '/菜单' or \
            str(event.message_chain) == '/help' or \
            str(event.message_chain) == '/帮助':
        await send(event, [], PIL_image=text_to_img(help_mesg))

    elif str(event.message_chain) == '/插件':
        await send(event, [], PIL_image=text_to_img(mirai_plugins_mesg))

    elif str(event.message_chain) == '/项目地址':
        await send(event, repo_info)
