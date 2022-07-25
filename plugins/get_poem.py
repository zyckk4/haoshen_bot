# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send
from mirai import Face
import aiohttp

@Listen.all_mesg()
async def get_poem(event):
    kw=['/作诗','/藏头诗','/词']
    for i in range(len(kw)):
        if str(event.message_chain).startswith(kw[i]):
            x=str(event.message_chain).replace(kw[i],'',1).strip()
            num=5
            if i==len(kw)-1:
                num=2
            elif x.startswith('7'):
                x.replace('7','')
                num=7
            try:
                output=await req_poem(i,num,x)
            except:
                await send(event,["连接失败了",Face(face_id=8)],True)
                return
            if output==-1:
                await send(event,["错误",Face(face_id=8)],True)
            else:
                cont=output['output'][0] if i==2 else output['output']
                mesg='\n'.join(cont)
                if i==0:
                    sc=output['score']
                    mesg+=f'\n诗歌评分:\n通顺{sc[0]},连贯{sc[1]},新颖{sc[2]},意境{sc[3]}'
                await send(event,mesg)
            return
    
async def req_poem(tp,num:int,theme:str):
    """ tp=0为绝句，tp=1为藏头诗，tp=2为宋词，num表示五或七言"""
    # 'cipai':
    if tp==2:
        data={
            'cipai':num,
            'poem':theme
            }
    elif tp==1:
        data={
            'yan': num,
            'poem':theme,
            'sentiment':-1
            }
    else:
        data={
            'yan': num,
            'poem':theme,
            }
    x=['send_jueju','send_arousic','send_songci']
    y=['get_jueju','get_arousic','get_songci']
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.141 Safari/537.36 "
        }
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),timeout=timeout) as session:
        async with session.post(url=f'http://166.111.5.188:12315/jiugepoem/task/{x[tp]}'
                               , json=data,headers=headers) as resp:
            info=await resp.json()
    cele_id=info['celery_id']
    data2={ 'celery_id':cele_id}
    while True:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),timeout=timeout) as session:
            async with session.post(url=f'http://166.111.5.188:12315/jiugepoem/task/{y[tp]}'
                                   , json=data2,headers=headers) as resp:
                info=await resp.json()
        if info['output']=='':
            try:
                if info['status']=='PENDING':
                    continue
                else:
                    return -1
            except:
                return -1
        else:
            return info