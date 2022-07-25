# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from mirai import Voice
from utils.utils import Listen,send


@Listen.all_mesg()
async def MCrecord(event):
    if str(event.message_chain).startswith('/mcr'):
        lst_record = ['11', '13', '5', 'blocks', 'cat', 'chirp', 'far', 'mall',
                      'mellohi', 'otherside', 'pigstep', 'stal', 'strad', 'wait', 'ward']
        if str(event.message_chain) == '/mcr':
            await send(event, '唱片列表：\n'+'\n'.join(lst_record))
            return
        
        path = 'statics/MCrecords'
        for r in lst_record:
            if r in str(event.message_chain):
                await send(event, Voice(path=f'{path}/{r}.ogg'))
                return
