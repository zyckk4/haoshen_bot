# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.utils import Listen,send
from statics.abstract_message_transformer_data import pinyin, emoji

@Listen.all_mesg()
async def abstract_message_transformer(event):
    if not str(event.message_chain).startswith('/抽象'):
        return
    x = str(event.message_chain).replace('/抽象', '', 1).strip()

    def get_pinyin(char: str):
        if char in pinyin:
            return pinyin[char]
        else:
            return "None"
    result = ""
    length = len(x)
    index = 0
    while index < length:
        if index < length - 1 and (get_pinyin(x[index]) + get_pinyin(x[index + 1])) in emoji:
            result += emoji[get_pinyin(x[index]) +
                            get_pinyin(x[index + 1])]
            index += 1
        elif get_pinyin(x[index]) in emoji:
            result += emoji[get_pinyin(x[index])]
        else:
            result += x[index]
        index += 1
    await send(event, result, True)