# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send,my_filter
from mirai import Image,Plain
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sys
import asyncio

def load_chrome():
    # 设置selenium使用chrome的无头模式
    chrome_options = Options()
    # 无界面模式
    chrome_options.add_argument('--headless')
    if sys.platform in ['linux','linux2']:
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
    # 在启动浏览器时加入配置
    wd = webdriver.Chrome(options=chrome_options)
    # 等待加载，最多等待10秒
    wd.implicitly_wait(10)
    return wd

@Listen.all_mesg(15)
async def search(event):
    keyword1=['/百科','/mcwiki','/oeis']
    for i in range(len(keyword1)):
        if str(event.message_chain).startswith(keyword1[i]):
            wd=load_chrome()
            str_search=str(event.message_chain).replace(keyword1[i],'',1)
            if str_search.startswith(' '):
                str_search=str_search.replace(' ','',1)
            url=['https://baike.baidu.com/item/',
                 'https://wiki.biligame.com/mc/',
                 'https://oeis.org/search?q='
                 ]
            wd.get(url[i]+str_search)
            all_hd=wd.window_handles
            width = wd.execute_script("return document.documentElement.scrollWidth")
            height = wd.execute_script("return document.documentElement.scrollHeight")
            if height>30*width:
                height=30*width
                await send(event,'由于太长，无法发出完整屏幕截图，仅截取前面部分',True)
            wd.set_window_size(width, height)
            cur_url=wd.current_url
            await asyncio.sleep(1)
            img = wd.get_screenshot_as_base64()
            await send(event,[Image(base64=img),Plain(cur_url)])
            
            def waiter(event2):
                if event.sender.id==event2.sender.id and str(event2.message_chain).startswith('//'):
                    mesg=str(event2.message_chain).replace('//','',1)
                    return mesg
                
            mes=await my_filter(waiter,'A',timeout=60)
            
            if mes is not None:
                element=wd.find_element(By.PARTIAL_LINK_TEXT,mes)
                element.click()
                all_hd2=wd.window_handles
                if all_hd2!=all_hd:
                    new_hd=[hd for hd in all_hd2 if hd not in all_hd]
                    wd.switch_to.window(new_hd[0])
                await asyncio.sleep(1)
                width = wd.execute_script("return document.documentElement.scrollWidth")
                height = wd.execute_script("return document.documentElement.scrollHeight")
                wd.set_window_size(width, height)
                cur_url=wd.current_url
                img = wd.get_screenshot_as_base64()
                await send(event,[Image(base64=img),Plain(cur_url)])
            return
        