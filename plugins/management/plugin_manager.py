# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
from mirai import MessageEvent
from utils.utils import Listen, send, Config, PLUGINS, STATIC_PLUGINS

plugin = Listen(
    'plugin_manager',
    '插件开关',
    True
)


@plugin.all_mesg()
async def get_plugin_list(event: MessageEvent):
    if str(event.message_chain) == '/功能列表':
        mesg = ["功能列表:"] + [f"\n{i}.{PLUGINS[i].name}: {PLUGINS[i].flag}"
                            for i in range(len(PLUGINS))]
        await send(event, mesg)
    elif str(event.message_chain) == '/静态插件列表':
        mesg = ["功能列表:"] + [f"\n{i}.{STATIC_PLUGINS[i].name}: {STATIC_PLUGINS[i].flag}"
                            for i in range(len(STATIC_PLUGINS))]
        await send(event, mesg)


@plugin.all_mesg()
async def get_plugin_info(event: MessageEvent):
    if str(event.message_chain) == '/随机功能':
        plugin = random.choice([i for i in PLUGINS if i.flag])
        await send(event, plugin.name+'插件: '+plugin.description)
    elif str(event.message_chain).startswith('/查功能'):
        x = str(event.message_chain).replace('/查功能', '').strip()
        if x.isdigit() and 0 <= int(x) < len(PLUGINS):
            plugin = PLUGINS[int(x)]
            await send(event, plugin.name+'插件: '+plugin.description, True)
        else:
            await send(event, "指令错误", True)


@plugin.all_mesg()
async def plugin_management(event: MessageEvent):
    if event.sender.id == Config.bot_owner_qq() and \
            str(event.message_chain).startswith('/关插件'):
        x = str(event.message_chain).replace('/关插件', '').strip()
        if x.isdigit() and 0 <= int(x) < len(PLUGINS):
            PLUGINS[int(x)].flag ^= 1
            await send(
                event,
                f"{PLUGINS[int(x)].name}插件开关状态已经设置为:{PLUGINS[int(x)].flag}",
                True
            )
        else:
            await send(event, "指令错误", True)
