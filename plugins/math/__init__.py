# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send,Config
from mirai import Face
from .get_latex import get_latex
from asyncio import exceptions as e
import aiohttp
from urllib.request import quote


@Listen.all_mesg()
async def get_latex_pic(event):
     keyword=[",,",'/latex','/LaTeX']
     for k in keyword:
         if str(event.message_chain).startswith(k):
             x=str(event.message_chain).replace(k,'',1)
             if x=='':
                 await send(event,'不能为空！',True)
                 return
             try:
                 img=await get_latex(x,7)
             except e.TimeoutError:
                 await send(event,["连接超时",Face(face_id=18)],True)
                 return
             await send(event,[],PIL_image=img)
             return

@Listen.all_mesg()
async def get_wa(event):
    if str(event.message_chain).startswith('/wa'):
        x=str(event.message_chain).replace('/wa','',1).strip()
        url = f"https://api.wolframalpha.com/v1/simple?i={quote(x)}&appid={Config.get()['wa_appid']}"
        timeout=aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    img=await resp.read()
                    await send(event,[],img_bytes=img)
                else:
                    await send(event,await resp.text())
         
