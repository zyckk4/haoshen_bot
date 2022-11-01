# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from mirai import Image, MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'get_news',
    '日报插件,输入"/日报"以获取'
)


@plugin.all_mesg()
async def get_news(event: MessageEvent):
    if str(event.message_chain) == '/日报':
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url="http://api.2xb.cn/zaob") as resp:
                    info = await resp.json()
        except:
            await send(event, "获取日报失败！", True)
            return
        img_url = info['imageUrl']
        await send(event, Image(url=img_url))
