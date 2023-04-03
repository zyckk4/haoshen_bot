# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import time
from io import BytesIO

import aiohttp
import imageio
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from mirai import Image, MessageEvent, Plain
from PIL import Image as IMG
from PIL import ImageSequence, UnidentifiedImageError
from realesrgan import RealESRGANer

from utils.utils import Listen, my_filter, send

plugin = Listen(
    'super_resolution',
    '图片超分,输入“/超分+图片”以超分'
)
handling = False


@plugin.all_mesg()
async def super_resolution(event: MessageEvent):
    global handling
    if str(event.message_chain).startswith('/超分'):
        if handling:
            await send(event, ['当前已有超分任务正在进行！'], True)
            return
        text = str(event.message_chain.get_first(Plain)).replace('/超分', '', 1)
        if text.startswith(' '):
            text = text.replace(' ', '', 1)
        if event.message_chain.count(Image) == 0:
            await send(event, "请在60s内发送图片", True)

            def waiter(event2: MessageEvent):
                if event.sender.id == event2.sender.id:
                    if event2.message_chain.count(Image) == 1:
                        img = event2.message_chain.get(Image)
                        return img
                    elif str(event2.message_chain) == "取消" or str(event2.message_chain) == "cancel":
                        return

            img = await my_filter(waiter, 'A', timeout=60)

            if img is None:
                await send(event, "请求已取消！", True)
                return
        elif event.message_chain.count(Image) >= 2:
            await send(event, "一次只能制作一张图", True)
            return
        else:
            img = event.message_chain.get(Image)
        handling = True
        async with aiohttp.ClientSession() as session:
            async with session.get(url=img[0].url) as resp:
                img_content = await resp.read()

        start = time.time()
        await send(event, "请稍等..", True)
        try:
            img = await do_super_resolution(img_content)
        except ValueError as e:
            await send(event, str(e))
            return
        except UnidentifiedImageError:
            await send(event, "加载此图片出现错误，试试换一张图片吧")
            return
        finally:
            handling = False
        end = time.time()
        use_time = round(end - start, 2)
        await send(event, [f"超分完成！处理用时：{use_time}s"], img_bytes=img)


async def do_super_resolution(
    image_data: bytes, resize: bool = False, is_gif: bool = False
):
    image = IMG.open(BytesIO(image_data))
    image_size = image.size[0] * image.size[1]

    max_size = 2073600

    upsampler = RealESRGANer(
        scale=4,
        model_path="statics/RealESRGAN_x4plus_anime_6B.pth",
        model=RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=6,
            num_grow_ch=32,
            scale=4,
        ),
        tile=100,
        tile_pad=10,
        pre_pad=0,
        half=False,
    )

    if image_size > max_size:
        if not resize:
            raise ValueError(
                "图片尺寸过大！请发送1080p以内即像素数小于 1920×1080=2073600的照片！\n",
                f"此图片尺寸为：{image.size[0]}×{image.size[1]}={image_size}！"
            )
        length = 1
        for b in str(max_size / image_size).split(".")[1]:
            if b == "0":
                length += 1
            else:
                break
        magnification = round(max_size / image_size, length + 1)
        image = image.resize(
            (round(image.size[0] * magnification),
             round(image.size[1] * magnification))
        )
    outputs = []
    output = None
    result = BytesIO()
    if is_gif:
        for i in ImageSequence.Iterator(image):
            image_array: np.ndarray = np.array(i)
            output = upsampler.enhance(image_array, 2)[0]
            outputs.append(output)
    else:
        image_array: np.ndarray = np.array(image)
        output = upsampler.enhance(image_array, 2)[0]

    if is_gif:
        imageio.mimsave(
            result, outputs[1:], format="gif", duration=image.info["duration"] / 1000
        )
    else:
        img = IMG.fromarray(output)
        img.save(result, format="PNG")  # format: PNG / JPEG

    del upsampler
    return result.getvalue()
