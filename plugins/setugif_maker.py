# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import random
from io import BytesIO

from mirai import MessageEvent
from PIL import Image as IMG
from PIL import ImageDraw, ImageFont

from utils.utils import Listen, send

plugin = Listen(
    'setugif_maker',
    '"色图"生成,输入"来张色图"试试'
)


@plugin.all_mesg()
async def send_setu(event: MessageEvent):
    if str(event.message_chain) == '来张色图' or str(event.message_chain) == '来张涩图':
        await send(event, [], img_bytes=create_setu())


def create_setu():
    color = (random.randint(0, 255), random.randint(
        0, 255), random.randint(0, 255))

    ccolor = (
        max(color) + min(color) - color[0],
        max(color) + min(color) - color[1],
        max(color) + min(color) - color[2],
    )

    iml = IMG.new("RGB", (300, 300), color)
    imr = IMG.new("RGB", (300, 300), ccolor)

    frames = []

    for _ in range(10):
        img = IMG.new("RGB", (600, 300))
        img.paste(imr, (300, 0))
        img.paste(iml, (0, 0))
        text = ImageDraw.Draw(img)
        FZDBSJWFont = ImageFont.truetype(
            "statics/fonts/simhei.ttf", random.randint(120, 220))
        text.text(
            (random.randint(10, 100), random.randint(10, 100)),
            "色",
            font=FZDBSJWFont,
            fill=ccolor,
        )
        FZDBSJWFont = ImageFont.truetype(
            "statics/fonts/simhei.ttf", random.randint(120, 220))
        text.text(
            (random.randint(320, 380), random.randint(10, 100)),
            "图",
            font=FZDBSJWFont,
            fill=color,
        )
        frames.append(img)

        img = IMG.new("RGB", (600, 300))
        img.paste(iml, (300, 0))
        img.paste(imr, (0, 0))
        text = ImageDraw.Draw(img)
        FZDBSJWFont = ImageFont.truetype(
            "statics/fonts/simhei.ttf", random.randint(120, 220))
        text.text(
            (random.randint(10, 100), random.randint(10, 100)),
            "色",
            font=FZDBSJWFont,
            fill=color,
        )
        FZDBSJWFont = ImageFont.truetype(
            "statics/fonts/simhei.ttf", random.randint(120, 220))
        text.text(
            (random.randint(320, 380), random.randint(10, 100)),
            "图",
            font=FZDBSJWFont,
            fill=ccolor,
        )
        frames.append(img)

        bt = BytesIO()
        frames[0].save(
            bt,
            format="GIF",
            append_images=frames[1:],
            save_all=True,
            duration=120,
            loop=0,
        )
        return bt.getvalue()
