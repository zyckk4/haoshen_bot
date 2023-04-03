# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import aiohttp
from mirai import MessageEvent

from utils.utils import Listen, send

plugin = Listen(
    'geng_search',
    '搜梗,输入"/搜梗 内容"以查询'
)

# TODO: 坏了要修
@plugin.all_mesg()
async def geng_search(event: MessageEvent):
    if str(event.message_chain).startswith("/搜梗"):
        x = str(event.message_chain).replace("/搜梗", '', 1).strip()
        data = {"phrase": x, "page": 1}
        headers = {
            'Host': 'api.jikipedia.com',
            'Origin': 'https://jikipedia.com',
            'Referer': 'https://jikipedia.com/',
            "Content-Type": "application/json;charset=UTF-8",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url='https://api.jikipedia.com/go/search_definitions', json=data, headers=headers) as resp:
                    info = await resp.json()
        except Exception:
            await send(event, "连接失败！", True)
            return
        if 'category' in info and info['category'] == "ban_enabled":
            await send(event, "请求过多，已达到访问上限，请稍后再试")
            return
        result = info['data'][0]
        await send(event, [f"{result['term']['title']}\n\n",
                           f"标签：{'、'.join(tag['name'] for tag in result['tags'])}\n\n",
                           f"释义：{result['content']}"])
