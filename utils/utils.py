# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import base64
import traceback
from io import BytesIO
from typing import Callable, List, Literal, Optional, Type, Union

from mirai import (Event, FriendMessage, GroupMessage, Image, MessageEvent,
                   Mirai, TempMessage)
from mirai.models import Entity, MemberJoinEvent, NudgeEvent
from mirai.exceptions import ApiError
from mirai_extensions.trigger import Filter, InterruptControl
from PIL.Image import Image as IMG

from utils.instance import core_instance

PLUGINS: List["Listen"] = []
STATIC_PLUGINS: List["Listen"] = []


class Listen:
    def __init__(
        self,
        plugin_name: str,
        plugin_description: str,
        is_static: bool = False
    ):
        self.name = plugin_name
        self.description = plugin_description
        self.flag = True
        self.is_static = is_static
        if is_static:
            STATIC_PLUGINS.append(self)
        else:
            PLUGINS.append(self)

    def listen(
        self,
        event_type: Type[Event],
        priority: int = 0
    ):
        bot: Mirai = core_instance.get().bot

        def deco(func):
            async def new_func(event):
                if not self.flag:
                    return
                try:
                    await func(event)
                except Exception:
                    await send(Config.bot_owner_qq(), traceback.format_exc(), is_friend_id=True)
                    raise
            bot.on(event_type, priority)(new_func)
            return func
        return deco

    def group(self, priority: int = 0):
        return self.listen(GroupMessage, priority)

    def friend(self, priority: int = 0):
        return self.listen(FriendMessage, priority)

    def temp(self, priority: int = 0):
        return self.listen(TempMessage, priority)

    def all_mesg(self, priority: int = 0):
        return self.listen(MessageEvent, priority)

    def nudge(self, priority: int = 0):
        return self.listen(NudgeEvent, priority)

    def member_join(self, priority: int = 0):
        return self.listen(MemberJoinEvent, priority)


async def my_filter(
    func: Callable,
    mesg_type: Literal['F', 'G', 'T', 'A'],
    timeout: float = 0,
    priority: int = 0
):
    _TYPE = {'F': FriendMessage, 'G': GroupMessage,
             'T': TempMessage, 'A': MessageEvent}
    if mesg_type not in _TYPE:
        raise KeyError('mesg_type应为F,G,T,A中一种')
    custom_filter = Filter(_TYPE[mesg_type], func=func)
    inc: InterruptControl = core_instance.get().inc
    return await inc.wait(custom_filter, timeout, priority)


async def send(
    arg: Union[int, NudgeEvent, MessageEvent, Entity],
    mesg_chain: List,
    quote: bool = False,
    PIL_image: Union[IMG, List[IMG], None] = None,
    img_bytes: Union[bytes, List[bytes], None] = None,
    fmt: str = 'PNG',
    is_friend_id: bool = False
) -> Optional[int]:
    """发送消息大封装

    arg可以为GroupMessage等event,也可以为NudgeEvent,也可以为群号,好友qq号
    """
    bot: Mirai = core_instance.get().bot

    if PIL_image is not None:
        if isinstance(PIL_image, list):
            for img in PIL_image:
                mesg_chain.append(Image(base64=img_to_base64(img, fmt)))
        else:
            mesg_chain.append(Image(base64=img_to_base64(PIL_image, fmt)))

    if img_bytes is not None:
        if isinstance(img_bytes, list):
            for bt in img_bytes:
                mesg_chain.append(Image(base64=base64.b64encode(bt)))
        else:
            mesg_chain.append(Image(base64=base64.b64encode(img_bytes)))

    if isinstance(arg, int):
        if is_friend_id:
            await bot.send_friend_message(arg, mesg_chain)
        else:
            await bot.send_group_message(arg, mesg_chain)
        return

    if isinstance(arg, NudgeEvent):
        entity = await bot.get_entity(arg.subject)
        return await bot.send(entity, mesg_chain, quote)

    return await bot.send(arg, mesg_chain, quote)


async def send_nudge(target: int, subject: int, kind: Literal['Friend', 'Group', 'Stranger']):
    """发送头像戳一戳消息。
    
    Args:
        target (`int`): 戳一戳的目标 QQ 号，可以为 bot QQ 号。
        subject (`int`): 戳一戳接受主体（上下文），戳一戳信息会发送至该主体，为群号或好友 QQ 号。
        kind (`Literal['Friend','Group','Stranger']`): 上下文类型，可选值 `Friend`, `Group`, `Stranger`。
    """
    bot: Mirai = core_instance.get().bot
    try:
        await bot.send_nudge(target, subject, kind)
    except ApiError:
        pass


async def respond_nudge(event: NudgeEvent):
    """戳回去刚刚戳bot的人"""
    await send_nudge(event.from_id, event.subject.id, event.subject.kind)


async def mute(group_id: Union[GroupMessage, int], member_id: int, time: int):
    """禁言"""
    bot: Mirai = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.mute(group_id, member_id, time)


async def unmute(group_id: Union[GroupMessage, int], member_id: int):
    """解除禁言"""
    bot: Mirai = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.unmute(group_id, member_id)


async def mute_all(group_id: Union[GroupMessage, int]):
    """全体禁言"""
    bot: Mirai = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.mute_all(group_id)


async def unmute_all(group_id: Union[GroupMessage, int]):
    """解除全员禁言"""
    bot: Mirai = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.unmute_all(group_id)


async def is_admin(event: GroupMessage) -> bool:
    """判断bot是否为管理员"""
    bot: Mirai = core_instance.get().bot
    return await bot.is_admin(event.group)


def img_to_base64(img: IMG, fmt: str) -> bytes:
    """将PIL.Image格式的图片转为base64码"""
    bt = BytesIO()
    img.save(bt, format=fmt)
    return base64.b64encode(bt.getvalue())


class Config:

    @staticmethod
    def get() -> dict:
        return core_instance.get().config

    @staticmethod
    def bot_qq() -> int:
        return core_instance.get().config['bot_qq']

    @staticmethod
    def bot_owner_qq() -> int:
        return core_instance.get().config['bot_owner_qq']

    @staticmethod
    def repeat_banned_group() -> int:
        return core_instance.get().config['repeat_banned_group']
