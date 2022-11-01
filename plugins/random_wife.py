# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
from mirai import Image, MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'random_wife',
    '二次元老婆生成,输入"/来个老婆"以获取'
)


@plugin.all_mesg()
async def random_waifu(event: MessageEvent):
    if str(event.message_chain) == '/来个老婆' or str(event.message_chain) == '/随机老婆':
        url = f"https://www.thiswaifudoesnotexist.net/example-{random.randint(1, 100000)}.jpg"
        await send(event, Image(url=url))
