# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
from mirai import MessageEvent
from utils.utils import Listen, send
from statics.pero_dog_contents import pero_dog_contents

plugin = Listen(
    'pero_dog_contents',
    r'舔狗内容生成,输入"/舔"以生成'
)


@plugin.all_mesg()
async def pero_dog(event: MessageEvent):
    if str(event.message_chain) == '/舔':
        text = random.choice(pero_dog_contents).replace('*', '')
        await send(event, text)
