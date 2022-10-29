# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import re
import aiohttp
from lxml import etree
from mirai import MessageEvent
from mirai.models import ForwardMessageNode, Forward
from utils.utils import Listen, send, Config

plugin = Listen(
    'math.ETC_search',
    'ETC搜索,输入"/查ETC 坐标“以查询该6_9_13坐标对应的特征点;输入"/ETC 编号"查询对应编号的特征点'
)


@plugin.all_mesg()
async def ETC_search(event: MessageEvent):
    if str(event.message_chain).startswith('/查ETC') or str(event.message_chain).startswith('/查etc'):
        x = str(event.message_chain).replace(
            '/查ETC', '').replace('/查etc', '').strip()
        preci = -1
        if x.startswith('preci='):
            ind = x.find(',')
            if ind == -1:
                await send(event, '指令错误')
                return
            try:
                preci = float(x[6:ind])
            except:
                await send(event, '指令错误')
                return
            if preci > 1 or preci <= 0:
                await send(event, '精度应为0~1!')
                return
            x = x.replace(x[:ind+1], '', 1)
        try:
            coord = float(x)
        except:
            await send(event, '指令错误')
            return
        try:
            mesg = await search(1, coord, preci)
        except:
            await send(event, "请求超时", True)
            return
        await send(event, mesg)


@plugin.all_mesg()
async def ETC_search2(event: MessageEvent):
    if str(event.message_chain).startswith('/ETC'):
        x = str(event.message_chain).replace('/ETC', '').strip()
        try:
            num = int(x)
        except:
            await send(event, '指令错误')
            return
        try:
            mesg = await get_center_info(num)
        except:
            await send(event, "请求超时", True)
            return
        # print(len(mesg))
        if len(mesg) > 15000:
            d = len(mesg)//14000
            for i in range(d):
                await send(event, Forward(node_list=[ForwardMessageNode(
                    sender_id=Config.bot_qq(), sender_name='ETC', message_chain=mesg[i*14000:(i+1)*14000])]))
            await send(event, Forward(node_list=[ForwardMessageNode(
                sender_id=Config.bot_qq(), sender_name='ETC', message_chain=mesg[d*14000:])]))
        else:
            await send(event, Forward(node_list=[ForwardMessageNode(
                sender_id=Config.bot_qq(), sender_name='ETC', message_chain=mesg)]))


async def search(mode, c, preci_set=-1, is_local=True):
    if is_local:
        fn = ['6_9_13.html', '9_13_6.html', '13_6_9.html']
        with open('statics/ETC/'+fn[mode-1], 'r') as f:
            info = f.read()
    else:
        url = ['https://faculty.evansville.edu/ck6/encyclopedia/Search_6_9_13.html',
               'https://faculty.evansville.edu/ck6/encyclopedia/Search_9_13_6.html',
               'https://faculty.evansville.edu/ck6/encyclopedia/Search_13_6_9.html']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
        }
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url=url[mode-1], headers=headers) as resp:
                info = await resp.text()
    html = etree.HTML(info)
    if preci_set == -1:
        preci1 = 0.00001
        preci2 = 0.01
        centers = search_center(html, c, preci1)
        if centers == []:
            centers = search_center(html, c, preci2)
            if centers == []:
                return f'No such element!(precision={preci2})'
            mesg = f'Precision={preci2}:\n'+','.join(centers)
        else:
            mesg = f'Precision={preci1}:\n'+','.join(centers)
    else:
        centers = search_center(html, c, preci_set)
        if centers == []:
            return f'No such element!(precision={preci_set})'
        mesg = f'Precision={preci_set}:\n'+','.join(centers)
    return mesg


async def get_center_html(part, num2, is_local=True):
    if is_local:
        with open(f'statics/ETC/ETCPart{part}.html') as f:
            text = f.read()
    else:
        url = f'http://faculty.evansville.edu/ck6/encyclopedia/ETCPart{part}.html' if part > 1 else \
            'http://faculty.evansville.edu/ck6/encyclopedia/ETC.html'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36'
        }
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url=url, headers=headers) as resp:
                text = await resp.text()
    lst = re.split(
        r'<h3 id="X\d+">|<h3 id="X\d+" class="auto-style4">|<h3 id="X\d+" style="color: #000000"|<h2>This is the end of PART|<H2>End of PART', text)
    return etree.HTML(lst[num2])


async def get_center_info(num):
    part = -1
    num2 = 0
    if 0 <= num <= 1000:
        part = 1
        num2 = num
    elif 1000 < num <= 3000:
        part = 2
        num2 = num-1000
    elif 3000 < num <= 5000:
        part = 3
        num2 = num-3000
    elif 5000 < num <= 7000:
        part = 4
        num2 = num-5000
    elif 7000 < num <= 10000:
        part = 5
        num2 = num-7000
    elif num > 51494 or num < 0:
        return 'Index out of range!'
    else:
        part = (num-1)//2000+1
        num2 = num-(part-1)*2000
    html = await get_center_html(part, num2)
    return html.xpath('string(.)').strip()


def search_center(html, c, precision):
    lst_ret = html.xpath(
        f'//tr[td[2]-{c}<{precision} and td[2]-{c}>-{precision}]/td[1]')
    if lst_ret == []:
        return []
    lst_center = lst_ret.copy()
    for i in range(len(lst_ret)):
        lst_center[i] = f'X({lst_ret[i].text})'
    return lst_center
