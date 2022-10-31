# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
import os
from datetime import datetime
from mirai import At, Dice, Face, Image, GroupMessage, MessageEvent
from mirai.models import NudgeEvent, MemberJoinEvent
from utils.utils import Listen, my_filter, send, send_nudge, respond_nudge,\
    mute, Config

plugin = Listen(
    'toolbox',
    '工具箱'
)


@plugin.all_mesg()
async def give_time(event: MessageEvent):
    '''报时'''
    if str(event.message_chain) == '报时':
        await send(event, f"当前时间：{datetime.now().strftime('%X')}")


@plugin.nudge()
async def on_nudge_message(event: NudgeEvent):
    '''戳一戳互动'''
    if event.subject.kind == 'Group' and event.subject.id in Config.get()['nudge_banned_group']:
        return
    if event.from_id != Config.bot_qq() and event.target == Config.bot_qq():
        ran = random.randint(0, 4)
        Re = ['别戳我嘛~', [At(event.from_id), ' 你好坏坏~我好爱爱~'],
              '别戳~好痛痛~~', '检测到未知的外部撞击！']
        if ran == 4:
            await respond_nudge(event)
            await send(event, '你戳戳我，我戳戳你')
        else:
            await send(event, Re[ran])


@plugin.all_mesg()
async def play_dice(event: MessageEvent):
    '''丢骰子'''
    if "丢色子" == str(event.message_chain) or "丢骰子" == str(event.message_chain):
        ran = random.randint(1, 6)
        await send(event, Dice(ran))
    if str(event.message_chain).startswith('丢'):
        x = str(event.message_chain).replace('丢', '', 1)
        enum = ('1', '2', '3', '4', '5', '6', '一', '二', '三', '四', '五', '六', '壹',
                '贰', '叁', '肆', '伍', '陆', 'one', 'two', 'three', 'four', 'five', 'six')
        for i in range(len(enum)):
            if x == enum[i]:
                await send(event, Dice(i % 6 + 1))
                return


@plugin.member_join()
async def welcome_new_member(event: MemberJoinEvent):
    '''欢迎新成员'''
    await send(event.member, [At(event.member.id), ",热烈欢迎 "+event.member.member_name+" 加入本群！"]
               + [Face(face_id=99)]*3)
    await send_nudge(event.member.id, event.member.group.id, 'Group')


@plugin.group()
async def interact_with_owner(event: GroupMessage):
    '''和主人互动'''
    if At(Config.bot_qq()) in event.message_chain and event.sender.id == Config.bot_owner_qq():
        reply = ("是的主人", "好的主人")
        await send(event, random.choice(reply), True)


@plugin.group()
async def hit_xiaobing(event: GroupMessage):
    '''揍小冰'''
    if str(event.message_chain) == '揍小冰':
        try:
            await mute(event.sender.group.id, 2854196306, 600)
        except:
            await send(event, "这群没有小冰啊让我怎么揍", True)
        else:
            await send(event, "好，小冰已经被揍哑巴了，哈哈哈哈", True)


@plugin.group()
async def pin_picture(event: GroupMessage):
    '''pin图功能'''
    path = f'data/pin_image/pin{event.group.id}'
    lst_path = [path+'.png', path+'.jpg', path+'.jpeg', path+'.gif']
    if str(event.message_chain).startswith('/pin'):
        for p in lst_path:
            if os.path.exists(p):
                await send(event, ["已有pin的图片！", Image(path=p)], True)
                return
        if event.message_chain.count(Image) == 0:
            await send(event, "请在30s内发送你想pin的图片", True)

            def waiter(event2):
                if event.sender.id == event2.sender.id and event2.message_chain.count(Image) == 1:
                    lst_pic = event2.message_chain.get(Image)
                    return lst_pic

            lst_pic = await my_filter(waiter, 'G', 30)

            if lst_pic is None:
                return
        elif event.message_chain.count(Image) >= 2:
            await send(event, "只能pin一张图片哦", True)
            return
        else:
            lst_pic = event.message_chain.get(Image)
        await lst_pic[0].download(lst_path[0])
        await send(event, 'pin图片成功!')

    elif str(event.message_chain) == '看pin':
        for p in lst_path:
            if os.path.exists(p):
                await send(event, Image(path=p), True)
                return
        await send(event, ["本群当前没有pin的图片", Face(face_id=22)], True)

    elif str(event.message_chain) == '删pin':
        for p in lst_path:
            if os.path.exists(p):
                os.remove(p)
                await send(event, "删除pin图片成功", True)
                return
        await send(event, ["本群当前没有pin的图片", Face(face_id=22)], True)
