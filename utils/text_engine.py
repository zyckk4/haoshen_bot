# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from PIL import Image,ImageFont,ImageDraw

def text_to_img(text:str,font_path="statics/fonts/msyh.ttc",font_size=36):
    lst=text.split('\n')
    font=ImageFont.truetype(font_path,font_size)
    x_max,h_max=0,0
    for t in lst:
        size_x,size_y=font.getsize(t)
        x_max=max(x_max,size_x)
        h_max=max(h_max,size_y)
    img = Image.new('RGB',(x_max+30,h_max*len(lst)),(255,255,255))
    draw=ImageDraw.Draw(img)
    for i in range(len(lst)):
        draw.text((0+2,i*h_max+2),lst[i],fill=0,font=font)
    
    return img


if __name__=='__main__':
    img=text_to_img("""输入</注册>以注册游戏账号开始游戏！
1.</签到,/档案,/升级,/改名,/赠送>执行对应操作
2.输入</24>快速开始单人24点,输入</24 e(或m,h,代表每题时间长短) x(1~10间的数代表总题数)>可以指定不同模式和题数
输入"/24pk"与他人pk24点(目前有无解情况,可以输入"."或"pass"或"过"或"放弃")
3.</重力棋,/五子棋,/反井字棋,/犹太人棋,/黑白棋,/围棋,/国际象棋>+@你想对阵的玩家开始下棋！
输入</反井字棋>+@bot,与AI对弈！
4.输入</背单词+你想背的词书+词数>开始背单词!目前可选词书有:CET4,CET6,GRE,TOEFL,KAOYAN,IELTS
5.输入</五十音>快速开始五十音抢答竞赛,</五十音+平(或片,或不填)+数量>自定义模式和题数
6.输入/扫雷,/数织，大家一起玩！输入/扫雷e或/扫雷m指定为标准初级或中级难度扫雷
7.合成十上线！规则简要介绍:变种消消乐。
相同值的相邻块可选择一个合成，你选择的那个块值+1，其他与他相邻的块会被消除，并加分：3*方块数*方块值。
然后其他方块下方有空位则会下落。最后会根据你场上最大数产生新方块，新方块不超过场上最大数。
输入</合成十>开始游戏，</合成十AI>随机生成一盘AI的对局
8.连珠消消乐上线！规则简介：
移动珠子，将同色珠子连成5个或以上来消除得分，其中珠子只能移动到与它联通的空位上。
开局有7颗珠子，每移一步新产生3颗，除非这一步消除了则不新产生。当无珠子可动时游戏结束。
输入</连珠消消乐>开始游戏
9.趣味连线上线！规则简介：
编辑图片，将同色格子用线连起来并填满棋盘的空位。
输入</趣味连线>开始游戏""",font_path='msyh.ttc')
    img.show()