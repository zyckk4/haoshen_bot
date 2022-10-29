# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 18:03:56 2022

@author: zyckk4  https://github.com/zyckk4
"""
from io import BytesIO
import aiohttp
from PIL import Image as IMG,ImageFont,ImageDraw
from mirai import Plain,At,Image,MessageEvent
from utils.utils import Listen,send,my_filter

plugin = Listen(
    'fun_image',
    r'趣图制作插件,输入"/制图"以开始'
)


@plugin.all_mesg()
async def fun_image(event:MessageEvent):
    if str(event.message_chain).startswith('/制图'):
        text=str(event.message_chain.get(Plain)[0]).replace('/制图','',1)
        sign=0
        if text.startswith('b'):
            text=text.replace('b','',1)
            sign=1
        if text.startswith(' '):
            text=text.replace(' ','',1)
        if event.message_chain.count(Image)==0:
            await send(event,"请在60s内发送图片",True)
            def waiter(event2):
                if event.sender.id==event2.sender.id:
                    if event2.message_chain.count(Image)==1:
                        img=event2.message_chain.get(Image)
                        return img
                    elif str(event2.message_chain)=="取消" or str(event2.message_chain)=="cancel":
                        return
                    
            img=await my_filter(waiter,'G',timeout=60)
            
            if img is None:
                await send(event,"请求已取消！",True)
                return
        elif event.message_chain.count(Image)>=2:
            await send(event,"一次只能制作一张图",True)
            return
        else:
            img=event.message_chain.get(Image)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=img[0].url) as resp:
                img_content=await resp.read()
        try:
            if sign:
                img=custom_pic_add_text(text,img_content,font_color=(255,255,255),bg_color=0)
            else:
                img=custom_pic_add_text(text,img_content)
        except ValueError as e:
            await send(event,str(e))
            return
        await send(event,[],PIL_image=img)
        return
    
    elif str(event.message_chain).startswith('/精神支柱'):
        if event.message_chain.count(At)>=2:
            await send(event,'一次只能选择一个人！',True)
            return
        elif event.message_chain.count(At)==1:
            img_url=get_user_image_url(event.message_chain.get(At)[0].target)
        else:
            if event.message_chain.count(Image)>=2:
                await send(event,'一次只能选择一张图片！',True)
                return
            elif event.message_chain.count(Image)==1:
                img_url=event.message_chain.get(Image)[0].url
            else:
                x=str(event.message_chain).replace('/精神支柱','',1)
                try:
                    qqid=int(x)
                except ValueError:
                    await send(event,"指令错误！")
                    return
                img_url=get_user_image_url(qqid)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=img_url) as resp:
                img_content=await resp.read()
        img=mental_support_pic(img_content)
        await send(event,[],PIL_image=img)
        return
    
    func=[gossip_pic,crazy_fan_pic,xibao_pic]
    kw=['/低语','/狂粉','/喜报']
    for i in range(len(kw)):
        if str(event.message_chain).startswith(kw[i]):
            x=str(event.message_chain).replace(kw[i],'',1)
            if x.startswith(' '):
                x=x.replace(' ','',1)
            try:
                img=func[i](x)
            except ValueError as e:
                await send(event,str(e))
                return
            await send(event,[],PIL_image=img)
            break
        
def text_b(coord,draw,text,font,shadowcolor,fillcolor,bw=1,is_thin=True):
    '''draw text with boarder'''
    x=coord[0];y=coord[1]
    if is_thin:
        # thin border
        draw.text((x - bw, y), text, font=font, fill=shadowcolor)
        draw.text((x + bw, y), text, font=font, fill=shadowcolor)
        draw.text((x, y - bw), text, font=font, fill=shadowcolor)
        draw.text((x, y + bw), text, font=font, fill=shadowcolor)
    else:
        # thicker border
        draw.text((x - bw, y - bw), text, font=font, fill=shadowcolor)
        draw.text((x + bw, y - bw), text, font=font, fill=shadowcolor)
        draw.text((x - bw, y + bw), text, font=font, fill=shadowcolor)
        draw.text((x + bw, y + bw), text, font=font, fill=shadowcolor)
    # now draw the text over it
    draw.text((x, y), text, font=font, fill=fillcolor)
    
def gossip_pic(input_str,path='statics/fun_img/gossip.jpg',
               font="statics/fonts/msyh.ttc",font_size=36,fill_color=0):
    font = ImageFont.truetype(font,size=font_size)
    img=IMG.open(path)
    w,h=img.size
    total_font_size = font.getsize(input_str)
    if total_font_size[0]>w:
        raise ValueError("请适当缩减字符串长度！")
    draw=ImageDraw.Draw(img)
    draw.text(((w-total_font_size[0])//2,h-50),input_str,font=font,fill=fill_color)
    return img

def crazy_fan_pic(input_str,path='statics/fun_img/crazy_fan.jpg',
               font="statics/fonts/msyh.ttc",font_size=48,font_color=0):
    font = ImageFont.truetype(font,size=font_size)
    img=IMG.open(path)
    w,h=img.size
    total_font_size = font.getsize(input_str)
    if total_font_size[0]>200:
        raise ValueError("请适当缩减字符串长度！")
    draw=ImageDraw.Draw(img)
    #text_b(((w-total_font_size[0])//2,98-total_font_size[1]//2),draw,input_str,font,(255,0,0),fill_color)
    draw.text(((w-total_font_size[0])//2,98-total_font_size[1]//2),input_str,font=font,fill=font_color)
    return img

def xibao_pic(input_str,path='statics/fun_img/xibao.png',
              font="statics/fonts/msyh.ttc",font_size=48,font_color=(255,0,0)):
    font = ImageFont.truetype(font,size=font_size)
    img=IMG.open(path)
    w,h=img.size
    total_font_size = font.getsize(input_str)
    if total_font_size[0]>w-10:
        raise ValueError("请适当缩减字符串长度！")
    draw=ImageDraw.Draw(img)
    draw.text(((w-total_font_size[0])//2,(h-total_font_size[1])//2),input_str,font=font,fill=font_color)
    return img

def custom_pic_add_text(input_str,img_content,
                        font="statics/fonts/msyh.ttc",font_size=48,font_color=0,bg_color=(255,255,255)):
    img=IMG.open(BytesIO(img_content))
    w,h=img.size
    font = ImageFont.truetype(font,size=font_size)
    total_font_size = font.getsize(input_str)
    if total_font_size[0]>w-10:
        raise ValueError("请适当缩减字符串长度！")
    new_img=IMG.new('RGB',(w,h+total_font_size[1]+8),bg_color)
    new_img.paste(img,(0,0))
    draw=ImageDraw.Draw(new_img)
    draw.text(((w-total_font_size[0])//2,h+4),input_str,font=font,fill=font_color)
    return new_img
    
def mental_support_pic(img_content,path='statics/fun_img/support.png'):
    user_img=IMG.open(BytesIO(img_content)).convert("RGBA")
    new_img=IMG.new('RGBA', (1293, 1164), (255, 255, 255, 0))
    ori_img=IMG.open(path)
    user_img = user_img.resize((815, 815), IMG.ANTIALIAS).rotate(23, expand=True)
    new_img.paste(user_img, (-172, -17))
    new_img.paste(ori_img, mask=ori_img)
    new_img = new_img.convert('RGB')
    return new_img

    
def get_user_image_url(qqid):
    return f'https://q4.qlogo.cn/g?b=qq&nk={qqid}&s=640'
        
