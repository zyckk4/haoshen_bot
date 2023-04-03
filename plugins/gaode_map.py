# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import aiohttp
import pandas as pd
from mirai import GroupMessage

from utils.utils import Config, Listen, send

plugin = Listen(
    'gaode_map',
    '高德地图API,输入"</经纬|/天气|/天气预报> 城市"以查询'
)


@plugin.group(15)
async def gaode_map(event: GroupMessage):
    keyword1 = '/经纬'
    if str(event.message_chain).startswith(keyword1):
        x = str(event.message_chain).replace(keyword1, '', 1).strip()
        data = {
            'key': Config.get()['gaode_key'],
            'address': x,
            # 'output': 'JSON'
        }
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url='https://restapi.amap.com/v3/geocode/geo?parameters',
                                   params=data) as resp:
                info = await resp.json()
        if info['status'] == '0':
            await send(event, "请求失败", True)
            return
        info = info['geocodes'][0]
        mesg_to_send = f'{info["formatted_address"]}的经纬度为{info["location"]}'
        await send(event, mesg_to_send)
        return

    keyword2 = '/天气'
    if str(event.message_chain).startswith(keyword2):
        x = str(event.message_chain).replace(keyword2, '', 1)
        if x.startswith('预报'):
            x = x.replace('预报', '', 1)
            i = 1
        else:
            i = 0
        if x.startswith(' '):
            x = x.replace(' ', '', 1)
        path = 'statics/AMap_adcode_citycode/AMap_adcode_citycode_20210406.xlsx'
        xlsx_data = pd.read_excel(path, index_col='中文名')
        try:
            adcode = int(xlsx_data.loc[x]['adcode'])
        except KeyError:
            await send(event, '没有找到你搜的城市', True)
            return
        data = {
            'key': Config.get()['gaode_key'],
            'city': adcode,
            'extensions': 'base',
            # 'output': 'JSON'
        }
        if i == 1:
            data['extensions'] = 'all'
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url='https://restapi.amap.com/v3/weather/weatherInfo?parameters',
                                   params=data) as resp:
                info = await resp.json()

        if info['status'] == '0':
            await send(event, "请求失败", True)
            return
        if i == 0:
            info = info['lives'][0]
            mesg_to_send = f'{x}：天气{info["weather"]}，气温{info["temperature"]}°C，{info["winddirection"]}风{info["windpower"]}级，空气湿度{info["humidity"]}'
        else:
            info = info['forecasts'][0]
            mesg_to_send = f'{x}近三天天气预报\n'
            for j in range(3):
                c = info['casts'][j]
                mesg_to_send += f'{c["date"]}：白天{c["dayweather"]},气温{c["daytemp"]}°C,{c["daywind"]}风{c["daypower"]}级；夜晚{c["nightweather"]},气温{c["nighttemp"]}°C,{c["nightwind"]}风{c["nightpower"]}级；'
                if j != 2:
                    mesg_to_send += '\n'
        await send(event, mesg_to_send)
