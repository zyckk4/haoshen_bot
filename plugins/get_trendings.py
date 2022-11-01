# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from bs4 import BeautifulSoup
from mirai import MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'get_news',
    '获取知乎和微博热榜的插件,输入"/知乎热榜"或"/微博热榜"以查询'
)


@plugin.all_mesg()
async def get_trendings(event: MessageEvent):
    if str(event.message_chain) == '/知乎热榜':
        try:
            mesg = await Trending.get_zhihu_trending()
        except:
            mesg = "请求超时！"
        await send(event, mesg)
    elif str(event.message_chain) == '/微博热榜':
        try:
            mesg = await Trending.get_weibo_trending()
        except:
            mesg = "请求超时！"
        await send(event, mesg)
# =============================================================================
#     elif str(event.message_chain)=='/github热榜':
#         try:
#             mesg=await Trending.get_github_trending()
#         except:
#             mesg="请求超时！"
#         await send(event,mesg)
# =============================================================================


class Trending:

    @staticmethod
    async def get_weibo_trending():
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url="http://api.weibo.cn/2/guest/search/hot/word") as resp:
                info = await resp.json()
        data = info["data"]
        text_list = ["微博实时热榜:"]
        index = 0
        for i in data:
            index += 1
            text_list.append(f"\n{index}. {i['word'].strip()}")
        text = "".join(text_list).replace("#", "")
        return text

    @staticmethod
    async def get_zhihu_trending():
        zhihu_hot_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true"
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url=zhihu_hot_url, headers=headers) as resp:
                info = await resp.json()
        data = info["data"]
        text_list = ["知乎实时热榜:"]
        index = 0
        for i in data:
            index += 1
            text_list.append(f"\n{index}. {i['target']['title'].strip()}")
        text = "".join(text_list).replace("#", "")
        return text

    @staticmethod
    async def get_github_trending():
        url = "https://github.com/trending"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.141 Safari/537.36 "
        }
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url=url, headers=headers) as resp:
                html = await resp.read()
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("article", {"class": "Box-row"})

        text_list = ["github实时热榜:\n"]
        index = 0
        for i in articles:
            try:
                index += 1
                title = i.find('h1').get_text().replace(
                    '\n', '').replace(' ', '').replace('\\', ' \\ ')
                text_list.append(f"\n{index}. {title}\n")
                text_list.append(f"\n    {i.find('p').get_text().strip()}\n")
            except:
                pass

        text = "".join(text_list).replace("#", "")
        return text
