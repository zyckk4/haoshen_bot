# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send
from mirai import Image
import random

@Listen.all_mesg()
async def random_waifu(event):
    if str(event.message_chain)=='/来个老婆' or str(event.message_chain)=='/随机老婆':
        url=f"https://www.thiswaifudoesnotexist.net/example-{random.randint(1, 100000)}.jpg"
        await send(event,Image(url=url))