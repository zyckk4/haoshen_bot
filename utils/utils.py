# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.instance import core_instance
from mirai import FriendMessage, GroupMessage, TempMessage, MessageEvent, Image
from mirai.models import NudgeEvent, MemberJoinEvent
from mirai_extensions.trigger import Filter
from io import BytesIO
import base64


class Listen:

    @staticmethod
    def group(priority=0):
        bot = core_instance.get().bot
        return bot.on(GroupMessage, priority)

    @staticmethod
    def friend(priority=0):
        bot = core_instance.get().bot
        return bot.on(FriendMessage, priority)

    @staticmethod
    def temp(priority=0):
        bot = core_instance.get().bot
        return bot.on(TempMessage, priority)

    @staticmethod
    def all_mesg(priority=0):
        bot = core_instance.get().bot
        return bot.on(MessageEvent, priority)

    @staticmethod
    def nudge(priority=0):
        bot = core_instance.get().bot
        return bot.on(NudgeEvent, priority)

    @staticmethod
    def member_join(priority=0):
        bot = core_instance.get().bot
        return bot.on(MemberJoinEvent, priority)


async def my_filter(func, mesg_type, timeout=0, priority=0):
    TYPE = {'F': FriendMessage, 'G': GroupMessage,
            'T': TempMessage, 'A': MessageEvent}
    if mesg_type not in TYPE:
        raise KeyError('mesg_type应为F,G,T,A中一种')
    custom_filter = Filter(TYPE[mesg_type], func=func)
    inc = core_instance.get().inc
    return await inc.wait(custom_filter, timeout, priority)


async def send(arg, mesg_chain, quote=False, PIL_image=None, img_bytes=None, fmt='PNG', is_friend_id=False):
    """发送消息大封装

    arg可以为GroupMessage等event,也可以为NudgeEvent,也可以为群号,好友qq号
    """
    bot = core_instance.get().bot

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
            return await bot.send_friend_message(arg, mesg_chain)
        return await bot.send_group_message(arg, mesg_chain)

    if isinstance(arg, NudgeEvent):
        entity = await bot.get_entity(arg.subject)
        return await bot.send(entity, mesg_chain, quote)

    return await bot.send(arg, mesg_chain, quote)


async def send_nudge(target, subject, kind):
    """发送头像戳一戳消息。
     Args:
         target (`int`): 戳一戳的目标 QQ 号，可以为 bot QQ 号。
         subject (`int`): 戳一戳接受主体（上下文），戳一戳信息会发送至该主体，为群号或好友 QQ 号。
         kind (`Literal['Friend','Group','Stranger']`): 上下文类型，可选值 `Friend`, `Group`, `Stranger`。
     """
    bot = core_instance.get().bot
    return await bot.send_nudge(target, subject, kind)


async def respond_nudge(event: NudgeEvent):
    """戳回去刚刚戳bot的人 """
    return await send_nudge(event.from_id, event.subject.id, event.subject.kind)


async def mute(group_id, member_id, time):
    """禁言"""
    bot = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.mute(group_id, member_id, time)


async def unmute(group_id, member_id):
    """解除禁言"""
    bot = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.unmute(group_id, member_id)


async def mute_all(group_id):
    """全体禁言"""
    bot = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.mute_all(group_id)


async def unmute_all(group_id):
    """解除全员禁言"""
    bot = core_instance.get().bot
    if isinstance(group_id, GroupMessage):
        group_id = group_id.sender.group.id

    return await bot.unmute_all(group_id)


async def is_admin(event: GroupMessage):
    """判断bot是否为管理员"""
    bot = core_instance.get().bot
    return await bot.is_admin(event.group)


def img_to_base64(img, fmt):
    """将PIL.Image格式的图片转为base64码
    """
    bt = BytesIO()
    img.save(bt, format=fmt)
    return base64.b64encode(bt.getvalue())


class Config:

    @staticmethod
    def get():
        return core_instance.get().config

    @staticmethod
    def bot_qq():
        return core_instance.get().config['bot_qq']

    @staticmethod
    def bot_owner_qq():
        return core_instance.get().config['bot_owner_qq']

    @staticmethod
    def repeat_banned_group():
        return core_instance.get().config['repeat_banned_group']
