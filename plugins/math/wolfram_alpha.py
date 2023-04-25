from asyncio import exceptions as e
from urllib.request import quote

import aiohttp
from mirai import Face, MessageEvent

from utils.utils import Config, Listen, send

plugin = Listen(
    'wolfram_alpha',
    '数学相关功能'
)


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
