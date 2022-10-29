# -*- coding: utf-8 -*-
"""
@author: ForeverHaibara  https://github.com/ForeverHaibara
Credits to https://github.com/PaddlePaddle/PaddleHub
"""
import time
import asyncio
import aiohttp
from mirai import Image, MessageEvent
from utils.utils import Listen, send

plugin = Listen(
    'AI_draw',
    '文心大模型AI画画插件,输入"/AI画画 风格 内容"以查询'
)


@plugin.all_mesg()
async def AI_draw_ernievilg(event: MessageEvent):
    """
    指令: /AI画画 + 风格 + 内容
    如: /AI画画 卡通 二次元美少女, 古风, 唯美, 柔软
    """
    if str(event.message_chain).startswith('/AI画画') or str(event.message_chain).startswith('/AI绘画'):
        splits = str(event.message_chain).split()
        if len(splits) >= 3:
            style = splits[1]
            texts = ' '.join(splits[2:])
            if style == 'low':
                if texts.startswith('poly '):  # 就这个有空格, 把 low poly 拼起来
                    style = 'low poly'
                    texts = texts[5:]

        elif len(splits) <= 2:
            await send(event, '参数错误, 应为 /AI画画 + 风格 + 内容')
            return

        await send(event, "请稍等..", True)

        engine = ErnieVilG()
        try:
            # 6 image urls in the list
            urls = await engine.generate_image(text_prompt=texts, style=style)
            await send(event, ['风格:%s\n内容:%s' % (style, texts)] + [Image(url=url) for url in urls])
        except RuntimeError as e:
            await send(event, str(e), True)
        except asyncio.exceptions.TimeoutError:
            await send(event, '网络连接超时！', True)
        except Exception as e:
            print(str(e))
            await send(event, "发生错误，请联系管理员")


class ErnieVilG:
    def __init__(self, ak=None, sk=None):
        """
        :param ak: ak for applying token to request wenxin api.
        :param sk: sk for applying token to request wenxin api.
        """
        self.ak = ak or 'G26BfAOLpGIRBN5XrOV2eyPA25CE01lE'
        self.sk = sk or 'txLZOWIjEqXYMU3lSm05ViW4p9DWGOWs'
        self.token_host = 'https://wenxin.baidu.com/younger/portal/api/oauth/token'
        self.available_styles = ['古风', '油画', '水彩', '卡通', '二次元', '浮世绘', '蒸汽波艺术', 'low poly',
                                 '像素风格', '概念艺术', '未来主义', '赛博朋克', '写实风格', '洛丽塔风格',
                                 '巴洛克风格', '超现实主义', '探索无限']

    async def _apply_token(self, ak, sk):
        ak = ak or self.ak
        sk = sk or self.sk

        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
            async with session.get(url=self.token_host,
                                   params={'grant_type': 'client_credentials',
                                           'client_id': ak,
                                           'client_secret': sk
                                           }
                                   ) as resp:
                res = await resp.json()

        return res['data']

    def check_style(self, style: str):
        if not style in self.available_styles:
            raise RuntimeError(
                '风格只支持 ' + '、'.join(self.available_styles) + ' 中的一种')
        return style

    async def generate_image(self,
                             text_prompt: str,
                             style: str = "油画",
                             resolution: str = None) -> list:
        """
        调用百度文心大模型接口进行AI作画.
        :param text_promt: 作画内容
        :param style: 作画风格, 暂时只支持 self.available_styles 中的一种
        :param resolution: '1024*1024', '1536*1024' (横), '1024*1536' (竖), 默认为第一种
        """
        token = await self._apply_token(self.ak, self.sk)
        create_url = 'https://wenxin.baidu.com/younger/portal/api/rest/1.0/ernievilg/v1/txt2img?from=paddlehub'
        get_url = 'https://wenxin.baidu.com/younger/portal/api/rest/1.0/ernievilg/v1/getImg?from=paddlehub'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        taskids = []
        style = self.check_style(style)

        # 发送作画请求
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
            async with session.post(url=create_url,
                                    data={'access_token': token,
                                          "text": text_prompt, "style": style, "resolution": resolution},
                                    headers=headers) as resp:
                res = await resp.json()

        if res['code'] == 100 or res['code'] == 110 or res['code'] == 111:
            token = await self._apply_token(self.ak, self.sk)
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
                async with session.post(url=create_url,
                                        data={'access_token': token,
                                              "text": text_prompt, "style": style, "resolution": resolution},
                                        headers=headers) as resp:
                    res = await resp.json()

        if res['msg'] == 'success':
            taskids.append(res['data']["taskId"])
        else:
            # print(res['msg'])
            raise RuntimeError(res['msg'])

        results = {}
        start_time = time.time()
        while len(taskids):  # retries
            # 请求作画结果 直到成功, 一般在 40 秒左右
            if time.time() - start_time > 300:  # 超时停止
                return []

            has_done = []
            for taskid in taskids:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
                    async with session.post(url=get_url,
                                            data={'access_token': token,
                                                  'taskId': {taskid}},
                                            headers=headers) as resp:
                        res = await resp.json()

                if res['code'] == 100 or res['code'] == 110 or res['code'] == 111:
                    token = await self._apply_token(self.ak, self.sk)
                    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
                        async with session.post(url=get_url,
                                                data={'access_token': token,
                                                      'taskId': {taskid}},
                                                headers=headers) as resp:
                            res = await resp.json()

                if res['msg'] == 'success':
                    if res['data']['status'] == 1:
                        has_done.append(res['data']['taskId'])
                    results[res['data']['text']] = {
                        'imgUrls': res['data']['imgUrls']}
                else:
                    # print(res['msg'])
                    raise RuntimeError(res['msg'])

            # do not post requests too frequently, because it takes time to generate images at server

            await asyncio.sleep(3)
            for taskid in has_done:
                taskids.remove(taskid)
        urls = [image['image']
                for image in list(results.values())[0]['imgUrls']]
        return urls
