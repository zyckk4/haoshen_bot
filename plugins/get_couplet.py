# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from mirai import GroupMessage
from utils.utils import Listen, send

plugin = Listen(
    'get_couplet',
    '作对联,输入"/对联 内容"以查询'
)


@plugin.group()
async def get_couplet(event: GroupMessage):
    if str(event.message_chain).startswith('/对联'):
        x = str(event.message_chain).replace('/对联', '', 1).strip()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }

        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
                async with session.get(url='https://seq2seq-couplet-model.rssbrain.com/v0.2/couplet/'+x, headers=headers) as resp:
                    info = await resp.json()
        except Exception:
            await send(event, "请求失败了！", True)
            return
        output = info['output']
        if output[0] == '':
            await send(event, "错误", True)
            return
        elif output[0] == '您的输入太长了':
            await send(event, "您的输入太长了", True)
            return
        mesg = f'{x} 的下联:\n'+'\n'.join(output[:3])
        await send(event, mesg)
