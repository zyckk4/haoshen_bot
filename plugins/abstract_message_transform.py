# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from mirai import MessageEvent
from utils.utils import Listen, send
from statics.abstract_message_transformer_data import pinyin, emoji

plugin = Listen(
    'abstract_message_transform',
    r'一个查询英文缩写意思的插件,输入"/抽象 内容"以查询'
)


@plugin.all_mesg()
async def abstract_message_transformer(event: MessageEvent):
    if not str(event.message_chain).startswith('/抽象'):
        return
    x = str(event.message_chain).replace('/抽象', '', 1).strip()
    if x=='':
        await send(event, "指令格式为'/抽象+内容',内容不能为空", True)
        return
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
