# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from mirai import GroupMessage, FriendMessage, Shutdown
from utils.instance import core_instance
from utils.utils import Listen

plugin = Listen(
    'logger',
    '日志',
    True
)


@plugin.group()
async def group_message_logger(event: GroupMessage):
    core_instance.get().logger.info(
        f"群 <{event.group.name}> 中成员 <{event.sender.member_name}> 的消息："
        f"{str(event.message_chain)}"
    )


@plugin.friend()
async def friend_message_logger(event: FriendMessage):
    core_instance.get().logger.info(
        f"好友 <{event.sender.nickname}> 的消息："
        f"{str(event.message_chain)}"
    )


@plugin.listen(Shutdown)
async def save_log(event: Shutdown):
    core_instance.get().logger.info("bot关闭")
