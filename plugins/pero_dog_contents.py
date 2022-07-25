# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send
from statics.pero_dog_contents import pero_dog_contents
import random

@Listen.all_mesg()
async def pero_dog(event):
    if str(event.message_chain)=='/舔':
        text=random.choice(pero_dog_contents).replace('*','')
        await send(event,text)