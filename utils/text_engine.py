# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from PIL import Image, ImageDraw, ImageFont


def text_to_img(text: str,
                font_path: str = './statics/fonts/msyh.ttc',
                font_size: int = 18,
                top_margin: int = 10,
                bottom_margin: int = 10,
                left_margin: int = 10,
                right_margin: int = 10,
                line_spacing: int = 0,
                font_color=(0, 0, 0),
                bg_color=(255, 255, 255)
                ) -> Image:
    """将文字转为PIL图片"""
    lines = text.split('\n')
    font = ImageFont.truetype(
        font_path, font_size) if font_path else ImageFont.load_default()

    max_width, max_height = 0, 0
    for line in lines:
        width, height = font.getbbox(line)[2], font.getbbox(line)[3]
        max_width = max(max_width, width)
        max_height = max(max_height, height)

    image = Image.new("RGB",
                      (max_width + left_margin + right_margin,
                       (max_height + line_spacing)*len(lines) +
                       top_margin + bottom_margin - line_spacing),
                      bg_color)
    draw = ImageDraw.Draw(image)

    y_text = top_margin
    for line in lines:
        draw.text((left_margin, y_text), line, fill=font_color, font=font)
        y_text += max_height + line_spacing

    return image
