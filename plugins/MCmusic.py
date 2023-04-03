# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from mirai import MessageEvent, Voice

from utils.utils import Listen, send

plugin = Listen(
    'MCmusic',
    '我的世界唱片,输入"/mcr"获取唱片列表,输入"/mcr 唱片名"获取音乐'
)


@plugin.all_mesg()
async def MCrecord(event: MessageEvent):
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
