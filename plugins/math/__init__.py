# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from asyncio import exceptions as e
from urllib.request import quote
import aiohttp
from mirai import Face, MessageEvent
from .get_latex import get_latex
from utils.utils import Listen, send, Config


plugin = Listen(
    'math',
    '数学相关功能'
)


@plugin.all_mesg()
async def get_latex_pic(event: MessageEvent):
    """LaTeX图片生成"""
    keyword = [",,", '/latex', '/LaTeX']
    for k in keyword:
        if str(event.message_chain).startswith(k):
            x = str(event.message_chain).replace(k, '', 1)
            if x == '':
                await send(event, '不能为空！', True)
                return
            try:
                img = await get_latex(x, 7)
            except e.TimeoutError:
                await send(event, ["连接超时", Face(face_id=18)], True)
                return
            except Exception:
                await send(event, ["错误！", Face(face_id=18)], True)
                return
            await send(event, [], PIL_image=img)
            return


@plugin.all_mesg()
async def get_wa(event: MessageEvent):
    if str(event.message_chain).startswith('/wa'):
        x = str(event.message_chain).replace('/wa', '', 1).strip()
        url = f"https://api.wolframalpha.com/v1/simple?i={quote(x)}&appid={Config.get()['wa_appid']}"
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        img = await resp.read()
                        await send(event, [], img_bytes=img)
                    else:
                        await send(event, await resp.text())
        except e.TimeoutError:
            await send(event, ["连接超时", Face(face_id=18)], True)
