# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 21:16:29 2022

@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from mirai import Face, MessageEvent
from utils.utils import Listen, send


plugin = Listen(
    'abbr_search',
    '一个查询英文缩写意思的插件,输入"/缩 内容"以查询'
)


@plugin.all_mesg()
async def abbr_search(event: MessageEvent):
    if str(event.message_chain).startswith("/缩"):
        x = str(event.message_chain).replace("/缩", '', 1).strip()
        data = {'text': x}
        headers = {
            'referer': 'https://lab.magiconch.com/nbnhhsh/?from=home',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
        }
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url='https://lab.magiconch.com/api/nbnhhsh/guess',
                                        json=data, headers=headers) as resp:
                    word = (await resp.json())[0]['trans']
        except:
            await send(event, ["请求失败了", Face(face_id=226)], True)
            return
        await send(event, f"'{x}'查询到以下意思："+str(word).replace("'", ""))
        return
