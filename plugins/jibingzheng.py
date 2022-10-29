# -*- coding: utf-8 -*-
"""
Created on Sat Jul 23 21:25:15 2022

@author: zyckk4  https://github.com/zyckk4
"""
from io import BytesIO
import aiohttp
from PIL import Image as IMG, ImageDraw, ImageFont
from mirai import Image, At, GroupMessage
from utils.utils import Listen, send

plugin = Listen(
    'jibingzheng',
    r'济兵证制作插件,输入"</计兵证|土木兵证> <@某人|图片>"以制作'
)


@plugin.group()
async def make_tongji_img(event:GroupMessage):
    if str(event.message_chain).startswith('/计兵证'):
        if event.message_chain.count(At) > 0:
            at = event.message_chain.get(At)[0]
            await send(event, [], PIL_image=await Jbz.get_jbz_by_qqid(at.target))
            return
        elif event.message_chain.count(Image) > 0:
            img = event.message_chain.get(Image)[0]
            await send(event, [], PIL_image=await Jbz.get_jbz_by_url(img.url))
            return
        else:
            await send(event, [], PIL_image=await Jbz.get_jbz_by_qqid(event.sender.id, jbz_id=event.sender.member_name))
            return
        
    elif str(event.message_chain).startswith('/土木兵证'):
        if event.message_chain.count(At) > 0:
            at = event.message_chain.get(At)[0]
            await send(event, [], PIL_image=await Tmbz.get_tmbz_by_qqid(at.target))
            return
        elif event.message_chain.count(Image) > 0:
            img = event.message_chain.get(Image)[0]
            await send(event, [], PIL_image=await Tmbz.get_tmbz_by_url(img.url))
            return
        else:
            await send(event, [], PIL_image=await Tmbz.get_tmbz_by_qqid(event.sender.id, tmbz_id=event.sender.member_name))
            return
        
async def download_img(url) -> IMG:
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            img_content = await resp.read()
    return IMG.open(BytesIO(img_content))

class Jbz:
    @staticmethod
    def make_jbz(avatur: IMG, jbz_no, jbz_id):
        '''制作计兵证'''
        img = IMG.open('statics/fun_img/jibingzheng/jbz.jpg', 'r')
        img.paste(avatur.resize((120,120)), (400, 20))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('statics/fonts/msyh.ttc', size=32)
        draw.text((76, 95), f'No.{jbz_no}', font=font, fill=0)
        draw.text((76, 140), f'ID: {jbz_id}', font=font, fill=0)
        return img
    
    @staticmethod
    async def get_jbz_by_url(url, jbz_no=114514, jbz_id='啊啊啊'):
        avatur = await download_img(url)
        return Jbz.make_jbz(avatur,jbz_no,jbz_id)
    
    @staticmethod
    async def get_jbz_by_qqid(qqid, jbz_no=114514, jbz_id='啊啊啊'):
        return await Jbz.get_jbz_by_url(f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640',jbz_no,jbz_id)

class Tmbz:
    @staticmethod
    def make_tmbz(avatur: IMG, tmbz_no, tmbz_id):
        '''制作土木兵证 '''
        img = IMG.open('statics/fun_img/jibingzheng/tmbz.jpg', 'r')
        img.paste(avatur.resize((120,120)), (700, 50))
        draw = ImageDraw.Draw(img)
        font1 = ImageFont.truetype('statics/fonts/msyh.ttc', size=42)
        font2 = ImageFont.truetype('statics/fonts/msyh.ttc', size=34)
        draw.text((362, 120), f'No.{tmbz_no}', font=font1, fill=0)
        draw.text((362, 200), f'ID: {tmbz_id}', font=font2, fill=0)
        return img
    
    @staticmethod
    async def get_tmbz_by_url(url, tmbz_no=114514, tmbz_id='啊啊啊'):
        avatur = await download_img(url)
        return Tmbz.make_tmbz(avatur,tmbz_no,tmbz_id)
    
    @staticmethod
    async def get_tmbz_by_qqid(qqid, tmbz_no=114514, tmbz_id='啊啊啊'):
        return await Tmbz.get_tmbz_by_url(f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640',tmbz_no,tmbz_id)
    
    