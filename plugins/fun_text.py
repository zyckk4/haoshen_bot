# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from mirai import MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'fun_text',
    '趣味文本,输入"/毒鸡汤|彩虹屁"以获取'
)


@plugin.all_mesg()
async def poison_chicken_soup(event: MessageEvent):
    if str(event.message_chain) == '/毒鸡汤':
        url = 'https://api.shadiao.pro/du'
    elif str(event.message_chain) == '/彩虹屁':
        url = 'https://api.shadiao.pro/chp'
    else:
        return
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url=url, headers=headers) as resp:
                info = await resp.json()
    except Exception:
        await send(event, "连接失败！", True)
        return
    await send(event, info['data']['text'])
