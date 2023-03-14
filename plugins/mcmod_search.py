# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from lxml import etree
from mirai import Face, MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'mcmod_search',
    '我的世界模组搜索,输入"/mcmod 内容"以搜索'
)


@plugin.all_mesg()
async def mod_search(event: MessageEvent):
    if str(event.message_chain).startswith('/mcmod'):
        x = str(event.message_chain).replace('/mcmod', '', 1).strip()
        try:
            mod_name, mod_url = await search(x)
        except Exception:
            await send(event, "连接超时")
            return
        num = len(mod_name)
        if num == 0:
            await send(event, ['没搜到捏！', Face(face_id=18)], True)
            return
        if num > 15:
            mesg = '在mcmod中搜索到很多mod,以下展示前15个'
            num = 15
        else:
            mesg = f'在mcmod中搜索到{num}个mod'
        for i in range(num):
            mesg += '\n'+mod_name[i]+':\n'+mod_url[i]
        await send(event, mesg)


async def search(key):
    url = f'https://search.mcmod.cn/s?key={key}&filter=1&mold=0'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.141 Safari/537.36 "
    }
    timeout = aiohttp.ClientTimeout(total=5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url=url, headers=headers) as resp:
            resp.encoding = 'utf-8'
            info = await resp.text()

    html = etree.HTML(info)
    mod_url = html.xpath(
        '/html/body/div/div/div[2]/div/div[4]/div//div[@class="result-item"]/div[1]/a/@href')
    mod_name = [''.join(html.xpath(
        f'/html/body/div/div/div[2]/div/div[4]/div//div[{i+1}]/div[1]/a/text()')) for i in range(len(mod_url))]
    return mod_name, mod_url
