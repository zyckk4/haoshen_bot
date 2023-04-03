# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import json
import random

from mirai import MessageEvent

from utils.utils import Listen, send

plugin = Listen(
    'make_cp_content',
    'cp文生成器,输入"/cp a b"以生成'
)


@plugin.all_mesg()
async def make_cp_mesg(event: MessageEvent):
    if str(event.message_chain).startswith("/cp "):
        x = str(event.message_chain).replace('/cp ', '', 1)
        x = x.split(' ')
        if len(x) != 2:
            await send(event, "指令错误", True)
            return
        mesg = get_cp_mesg(x[0], x[1])
        await send(event, mesg, True)


def get_cp_mesg(gong, shou):
    with open('statics/cp_data.json', "r", encoding="utf-8") as f:
        cp_data = json.loads(f.read())
    return random.choice(cp_data['data']).replace('<攻>', gong).replace('<受>', shou)
