# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send
from statics.jokes import french_jokes,america_jokes,soviet_jokes,jokes
import random

@Listen.group()
async def make_jokes(event):
    if str(event.message_chain).startswith('来点') and str(event.message_chain).endswith('笑话'):
        x=str(event.message_chain)[2:-2]
        joke=get_joke(x)
        await send(event,joke)
        
def get_joke(joke_tp):
    if joke_tp=='法国':
        return random.choice(french_jokes)
    elif joke_tp=='美国':
        return random.choice(america_jokes)
    elif joke_tp=='苏联':
        return random.choice(soviet_jokes)
    else:
        if joke_tp=='':
            joke_tp='豪神豪神' 
        return random.choice(jokes).replace('%name%',joke_tp)