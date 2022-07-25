# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen, send
import aiohttp
from mirai import Face

@Listen.all_mesg() 
async def abbr_search(event):
    if str(event.message_chain).startswith("/缩"):
        x=str(event.message_chain).replace("/缩",'',1).strip()
        data = {'text': x }
        headers={
            'referer':'https://lab.magiconch.com/nbnhhsh/?from=home'
            }
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url='https://lab.magiconch.com/api/nbnhhsh/guess',
                                        json=data,headers=headers) as resp:
                     word = (await resp.json())[0]['trans']
        except:
            await send(event,["请求失败了",Face(face_id=226)],True)
            return
        await send(event,f"'{x}'查询到以下意思："+str(word).replace("'",""))
        return


    
    
    