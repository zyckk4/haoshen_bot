# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from io import BytesIO

import aiohttp
import numpy as np
import paddle
from mirai import Image, MessageEvent
from PIL import Image as IMG

from utils.utils import Listen, my_filter, send

plugin = Listen(
    'number_recognition',
    '数字识别,输入"/数字识别"以开始'
)


@plugin.all_mesg()
async def number_recognition(event: MessageEvent):
    if str(event.message_chain).startswith('/数字识别'):
        await send(event, ["请在图片上写一个阿拉伯数字"],
                   PIL_image=IMG.new("RGB", (280, 280), 0))

        def waiter(event2):
            if event.sender.id == event2.sender.id:
                if event2.message_chain.count(Image) == 1:
                    img = event2.message_chain.get(Image)
                    return img, event2
                elif str(event2.message_chain) == "取消" or str(event2.message_chain) == "cancel":
                    return

        img = await my_filter(waiter, 'A', timeout=60)

        if img is None:
            await send(event, "请求已取消！", True)
            return
        img, event2 = img
        async with aiohttp.ClientSession() as session:
            async with session.get(url=img[0].url) as resp:
                img_content = await resp.read()
        num = recognize_number(img_content)
        await send(event2, f"您写的数字是：{num}", True)


def recognize_number(img_content):
    img_origin = IMG.open(BytesIO(img_content))
    img = np.array(img_origin.resize((28, 28)))[:, :, 0]
    lenet = paddle.vision.models.LeNet(num_classes=10)
    model = paddle.Model(lenet)
    model.load('./statics/mnist')
    # 将图片shape从28*28变为1*1*28*28，增加batch维度，以匹配模型输入格式要求
    img_batch = np.expand_dims(img.astype('float32'), axis=0)
    img_batch = np.expand_dims(img_batch.astype('float32'), axis=0)
    out = model.predict_batch(img_batch)[0]
    return out.argmax()
