# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 16:28:57 2022

@author: zyckk4  https://github.com/zyckk4
"""
import aiohttp
from mirai import Image, MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'bilibili_bangumi',
    'b站番剧查询插件,输入"/b站新番"以查询'
)


@plugin.all_mesg()
async def get_bilibili_new_bangumi(event: MessageEvent):
    if str(event.message_chain) == '/b站新番':
        data = (await get_formatted_new_bangumi_json())[0]
        mesg_chain = []
        for d in data:
            mesg_chain.append(d['title']+' '+d['pub_index']+' '+d['pub_time'])
            mesg_chain.append(Image(url=d['cover']))
        await send(event, mesg_chain)


async def get_new_bangumi_json() -> dict:
    """
    Get json data from bilibili

    Args:

    Examples:
        data = await get_new_bangumi_json()

    Return:
        dict:data get from bilibili
    """
    url = "https://bangumi.bilibili.com/web_api/timeline_global"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate",
        "accept-language": "zh-CN,zh;q=0.9",
        "origin": "https://www.bilibili.com",
        "referer": "https://www.bilibili.com/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36 "
    }
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
        async with session.post(url=url, headers=headers) as resp:
            result = await resp.json()
    return result


async def get_formatted_new_bangumi_json(day=1):
    """
    Format the json data

    Examples:
        data = get_formatted_new_bangumi_json()

    Returns:
        {
            "title": str,
            "cover": str,
            "pub_index": str,
            "pub_time": str,
            "url": str
        }
    """
    all_bangumi_data = await get_new_bangumi_json()
    all_bangumi_data = all_bangumi_data["result"][-7:]
    formatted_bangumi_data = list()

    for bangumi_data in all_bangumi_data:
        temp_bangumi_data_list = list()
        for data in bangumi_data["seasons"]:
            temp_bangumi_data_dict = dict()
            temp_bangumi_data_dict["title"] = data["title"]
            temp_bangumi_data_dict["cover"] = data["cover"]
            temp_bangumi_data_dict["pub_index"] = data["delay_index"] + \
                " (本周停更)" if data["delay"] else data["pub_index"]
            temp_bangumi_data_dict["pub_time"] = data["pub_time"]
            temp_bangumi_data_dict["url"] = data["url"]
            temp_bangumi_data_list.append(temp_bangumi_data_dict)
        formatted_bangumi_data.append(temp_bangumi_data_list)

    return formatted_bangumi_data[:day]
