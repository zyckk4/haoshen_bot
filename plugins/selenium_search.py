# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import asyncio
import random
import sys

from mirai import Image, MessageEvent, Plain
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils.utils import Listen, my_filter, send

plugin = Listen(
    'selenium_search',
    'selenium相关功能'
)


def load_chrome():
    # 设置selenium使用chrome的无头模式
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    if sys.platform in ['linux', 'linux2']:
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
    # 在启动浏览器时加入配置
    wd = webdriver.Chrome(options=chrome_options)
    # 设置最大等待时间
    wd.implicitly_wait(10)
    wd.set_page_load_timeout(10)
    return wd


@plugin.all_mesg(15)
async def search(event: MessageEvent):
    keyword1 = ('/百科', '/百度纯几吧搜', '/mcwiki', '/oeis', '/萌娘百科')
    for i in range(len(keyword1)):
        if str(event.message_chain).startswith(keyword1[i]):
            wd = load_chrome()
            str_search = str(event.message_chain).replace(keyword1[i], '', 1)
            if str_search.startswith(' '):
                str_search = str_search.replace(' ', '', 1)
            url = (
                'https://baike.baidu.com/item/',
                'https://tieba.baidu.com/f/search/res?ie=utf-8&kw=%E7%BA%AF%E5%87%A0%E4%BD%95&qw=',
                'https://wiki.biligame.com/mc/',
                'https://oeis.org/search?q=',
                'https://zh.moegirl.org.cn/'
            )
            try:
                wd.get(url[i]+str_search)
            except TimeoutException:
                await send(event, '请求超时！请稍后重试', True)
                return
            all_hd = wd.window_handles
            width = wd.execute_script(
                'return document.documentElement.scrollWidth')
            height = wd.execute_script(
                'return document.documentElement.scrollHeight')
            if height > 30*width:
                height = 30*width
                await send(event, '由于太长，无法发出完整屏幕截图，仅截取前面部分', True)
            wd.set_window_size(width, height)
            cur_url = wd.current_url
            await asyncio.sleep(1)
            img = wd.get_screenshot_as_base64()
            await send(event, [Image(base64=img), Plain(cur_url)])

            def waiter(event2):
                if event.sender.id == event2.sender.id and str(event2.message_chain).startswith('//'):
                    mesg = str(event2.message_chain).replace('//', '', 1)
                    return mesg

            mes = await my_filter(waiter, 'A', timeout=60)

            if mes is not None:
                element = wd.find_element(By.PARTIAL_LINK_TEXT, mes)
                element.click()
                all_hd2 = wd.window_handles
                if all_hd2 != all_hd:
                    new_hd = [hd for hd in all_hd2 if hd not in all_hd]
                    wd.switch_to.window(new_hd[0])
                await asyncio.sleep(1)
                width = wd.execute_script(
                    'return document.documentElement.scrollWidth')
                height = wd.execute_script(
                    'return document.documentElement.scrollHeight')
                wd.set_window_size(width, height)
                cur_url = wd.current_url
                img = wd.get_screenshot_as_base64()
                await send(event, [Image(base64=img), Plain(cur_url)])
            return

    keyword2 = '/纯几何吧'
    if str(event.message_chain).startswith(keyword2):
        x = str(event.message_chain).replace(keyword2, '', 1).strip()
        if not x.isdigit():
            await send(event, '指令格式为"/纯几何吧 <题号>"', True)
            return
        try:
            with open('./statics/cjhb.txt', 'r') as f:
                info = f.read().split('\n')
        except FileNotFoundError:
            await send(event, '缺少cjhb.txt数据文件', True)
            return
        try:
            index = info.index(x)
        except ValueError:
            await send(event, '题号超出范围！', True)
            return
        pid = info[index+1].split()
        if not pid:
            await send(event, f'未查找到纯几何吧{x}的信息！', True)
            return
        if len(pid) >= 2:
            pid = ['https://tieba.baidu.com/p'+k for k in pid]
            await send(event, [f'纯几何吧{x}查询到{len(pid)}个结果:\n', '\n'.join(pid)])
            return

        wd = load_chrome()
        try:
            wd.get('https://tieba.baidu.com/p'+pid[0])
        except TimeoutException:
            await send(event, '请求超时！请稍后重试', True)
            return
        width = wd.execute_script(
            'return document.documentElement.scrollWidth')
        height = wd.execute_script(
            'return document.documentElement.scrollHeight')
        wd.set_window_size(width, height)
        cur_url = wd.current_url
        await asyncio.sleep(0.5)
        img = wd.get_screenshot_as_base64()
        await send(event, [Image(base64=img), f'纯几何吧{x}: ', cur_url])

    keyword3 = '来道平几'
    if str(event.message_chain) == keyword3:
        try:
            with open('./statics/cjhb.txt', 'r') as f:
                info = f.read().split('\n')
        except FileNotFoundError:
            await send(event, '缺少cjhb.txt数据文件', True)
            return
        while True:
            num = random.randint(1, len(info)-1)
            if num % 2 == 0:
                continue
            if len(info[num].split()) == 0:
                continue
            break
        pid = random.choice(info[num].split())

        wd = load_chrome()
        try:
            wd.get('https://tieba.baidu.com/p'+pid)
        except TimeoutException:
            await send(event, '请求超时！请稍后重试', True)
            return
        width = wd.execute_script(
            'return document.documentElement.scrollWidth')
        height = wd.execute_script(
            'return document.documentElement.scrollHeight')
        wd.set_window_size(width, height)
        cur_url = wd.current_url
        await asyncio.sleep(0.5)
        img = wd.get_screenshot_as_base64()
        await send(event, [Image(base64=img), f'纯几何吧{info[num-1]}: ', cur_url])
