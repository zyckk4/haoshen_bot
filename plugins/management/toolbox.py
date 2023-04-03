# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import asyncio
import random

from mirai import At, AtAll, FriendMessage, GroupMessage, Image

from utils.utils import (Config, Listen, is_admin, mute, mute_all, my_filter,
                         send, unmute, unmute_all)

plugin = Listen(
    'toolbox',
    '工具箱',
    True
)


@plugin.friend()
async def owner_control(event: FriendMessage):
    """主人控制"""
    if event.sender.id != Config.bot_owner_qq():
        return
    if str(event.message_chain).startswith('/send'):
        x = str(event.message_chain).replace('/send', '', 1).strip()
        try:
            group_id = int(x)
        except:
            await send(event, "指令错误")
            return
        await send(event, "请在60s内输入你想发的消息")

        def waiter(event2):
            if event2.sender.id == event.sender.id:
                return event2.message_chain
            
        mesg_chain = await my_filter(waiter, 'F', 60)
        
        await send(group_id, mesg_chain)
        await send(event, "发送成功", True)


@plugin.group()
async def about_mute(event: GroupMessage):
    """禁言相关"""
    if str(event.message_chain) == '快来禁言我':
        ran_mutetime = random.randint(180, 600)
        if not event.sender.permission == "MEMBER":
            await send(event, "草，劳资禁言不了你", True)
        else:
            await mute(event, event.sender.id, ran_mutetime)
            await send(event, '群员 '+event.sender.member_name+' 已被禁言%d分钟%d秒' % (ran_mutetime/60, ran_mutetime % 60))

    elif str(event.message_chain).startswith('/禁言'):
        if not await is_admin(event):
            await send(event, "呜呜，我没有权限，帮不了你", True)
            return
        if event.sender.permission == "MEMBER":
            await send(event, "你这刁民还敢禁言？", True)
            ran_mutetime = random.randint(180, 300)
            await mute(event, event.sender.id, ran_mutetime)
            return
        if AtAll in event.message_chain:
            await mute_all(event)
            await send(event, "全员禁言已开启", True)
            return
        if event.message_chain.count(At) == 0:
            await send(event, "需at你想禁言的成员!", True)
            return
        lst_id = [at.target for at in event.message_chain.get(At)]
        ct = 0
        for _id in lst_id:
            try:
                await mute(event, _id, random.randint(180, 300))
            except:
                await send(event, f"呜呜，我没权限禁言成员{_id}")
                ct += 1
        await send(event, f"禁言{len(lst_id)-ct}个成员成功,{ct}个成员失败", True)

    elif str(event.message_chain).startswith('/解禁'):
        if not await is_admin(event):
            await send(event, "呜呜，我没有权限，帮不了你", True)
            return
        if event.sender.permission == "MEMBER":
            await send(event, "你这刁民还敢解禁？", True)
            ran_mutetime2 = random.randint(180, 300)
            await mute(event, event.sender.id, ran_mutetime2)
            return
        if AtAll in event.message_chain:
            await unmute_all(event)
            await send(event, "全员禁言已关闭", True)
            return
        if event.message_chain.count(At) == 0:
            await send(event, "需at你想解禁的成员!", True)
            return
        lst_id = [at.target for at in event.message_chain.get(At)]
        for _id in lst_id:
            try:
                await unmute(event, _id)
            except:
                await send(event, f"呜呜，我没权限解禁成员{_id}")
                ct += 1
        await send(event, "解禁成功！", True)

    elif str(event.message_chain) == '开启全员禁言':
        if event.sender.permission == "MEMBER" and event.sender.id != Config.bot_owner_qq():
            await send(event, [At(event.sender.id), '你这刁民还敢开全员禁言？？'])
            ran_mutetime = random.randint(180, 300)
            await mute(event, event.sender.id, ran_mutetime)
        else:
            await mute_all(event)
            if event.sender.permission == "OWNER":
                await send(event, '全员禁言已开启，尊敬的群主大人', True)
            elif event.sender.id == Config.bot_owner_qq():
                await send(event, '全员禁言已开启，亲爱的,但是你只能禁言10秒', True)
                await asyncio.sleep(10)
                await unmute_all(event)

    elif str(event.message_chain) == '关闭全员禁言':
        await unmute_all(event)
        if event.sender.permission == "OWNER":
            await send(event, '全员禁言已关闭，亲爱的群主大人', True)

str_pre = {}
str_photo_pre = {}
count = {}


@plugin.group()
async def about_repeat(event: GroupMessage):
    """复读相关"""
    global str_pre, str_photo_pre, count
    if event.group.id in Config.repeat_banned_group():
        if event.group.id not in str_pre:
            count[event.group.id] = 0
            str_pre[event.group.id] = None
            str_photo_pre[event.group.id] = None
        if str(event.message_chain) == str_pre[event.group.id] and event.message_chain.get(Image) == str_photo_pre[event.group.id]:
            if count[event.group.id] >= 2:
                if event.sender.permission == "ADMINISTRATOR":
                    await send(event.sender.group.id, '臭管理带头复读鲨不掉呜呜')
                elif event.sender.permission == "OWNER":
                    await send(event, '臭群主带头复读，我要起义！')
                else:
                    await mute(event, event.sender.id, 600)
            else:
                count[event.group.id] += 1
        else:
            count[event.group.id] = 0
            str_pre[event.group.id] = str(event.message_chain)
            str_photo_pre[event.group.id] = event.message_chain.get(Image)
