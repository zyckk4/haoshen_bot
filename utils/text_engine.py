# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from PIL import Image, ImageDraw, ImageFont


def text_to_img(text: str, font_path="statics/fonts/msyh.ttc", font_size=36):
    lst = text.split('\n')
    font = ImageFont.truetype(font_path, font_size)
    x_max, h_max = 0, 0
    for t in lst:
        size_x, size_y = font.getsize(t)
        x_max = max(x_max, size_x)
        h_max = max(h_max, size_y)
    img = Image.new('RGB', (x_max+30, h_max*len(lst)), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    for i in range(len(lst)):
        draw.text((0+2, i*h_max+2), lst[i], fill=0, font=font)

    return img

