# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from utils.utils import Listen, send

plugin = Listen(
    'yingxiaohao_content_maker',
    '营销号内容生成器,输入"/yxh 某人 某事“以生成'
)


@plugin.all_mesg()
async def YXH_content_maker(event):
    if str(event.message_chain).startswith('/yxh'):
        x = str(event.message_chain).replace('/yxh', '', 1).strip()
        lst = x.split()
        if len(lst) < 2 or len(lst) > 3:
            await send(event, "指令错误")
            return
        somebody = lst[0]
        something = lst[1]
        other_word = lst[2] if len(lst) == 3 else something
        mesg = f"{somebody}{something}是怎么回事呢？" \
            f"{somebody}相信大家都很熟悉，但是{somebody}{something}是怎么回事呢，下面就让小编带大家一起了解下吧。\n" \
            f"{somebody}{something}，其实就是{somebody}{other_word}，大家可能会很惊讶{somebody}怎么会{something}呢？" \
            f"但事实就是这样，小编也感到非常惊讶。\n" \
            f"这就是关于{somebody}{something}的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！ "
        await send(event, mesg)
