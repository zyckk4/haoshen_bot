# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import re
from asyncio import exceptions as e
from io import BytesIO
from urllib.request import quote

import aiohttp
import numpy as np
from cairosvg import svg2png
from mirai import Face, MessageEvent
from PIL import Image

from utils.utils import Listen, send

plugin = Listen(
    'get_latex',
    'LaTeX图片生成功能'
)


@plugin.all_mesg()
async def get_latex_pic(event: MessageEvent):
    """LaTeX图片生成"""
    keyword = ('/latex', '/LaTeX')
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


def get_url(x, is_svg=True):
    try:
        x = quote(x)
        return f'https://i.upmath.me/svg/{x}' if is_svg else f'https://i.upmath.me/png/{x}'
    except Exception:
        return -1


async def get_latex(input_str, k, is_svg=True):
    url = get_url(input_str, is_svg)
    if not is_svg:
        return url
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
        async with session.get(url=url, headers=headers) as resp:
            svg = await resp.text()
    compile1 = re.compile(r'width="\d+" height="\d+"')
    compile2 = re.compile(r'\d+')
    pic_size = compile1.findall(svg)[0]
    num_result = compile2.findall(pic_size)
    svg = re.sub(f'width="{num_result[0]}"',
                 f'width="{str(k*int(num_result[0]))}"', svg, 1)
    svg = re.sub(
        f'height="{num_result[1]}"', f'height="{str(k*int(num_result[1]))}"', svg, 1)
    bt = svg2png(bytestring=svg)
    a = np.array(Image.open(BytesIO(bt)))
    zeros = np.where(a[:, :, -1] == 0)
    a[zeros[0], zeros[1], :] = 255
    return Image.fromarray(a).convert("RGBA")
