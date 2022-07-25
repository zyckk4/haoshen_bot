# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from utils.utils import Listen, my_filter, send, send_nudge, respond_nudge,\
    mute, unmute, mute_all, unmute_all, is_admin, Config
from mirai import At, Dice, Face, Image, AtAll
from datetime import datetime
import random
import asyncio
import os


@Listen.all_mesg()
async def give_time(event):
    '''报时'''
    if str(event.message_chain) == '报时':
        await send(event, f"当前时间：{datetime.now().strftime('%X')}")

 
@Listen.nudge()
async def on_nudge_message(event):
    '''戳一戳互动'''
    if event.from_id != Config.bot_qq() and event.target == Config.bot_qq():
        ran = random.randint(0, 4)
        Re = ['别戳我嘛~', [At(event.from_id), ' 你好坏坏~我好爱爱~'],
              '别戳~好痛痛~~', '检测到未知的外部撞击！']
        if ran == 4:
            await respond_nudge(event)
            await send(event, '你戳戳我，我戳戳你')
        else:
            await send(event, Re[ran])


@Listen.all_mesg()
async def play_dice(event):
    '''丢骰子'''
    if "丢色子" == str(event.message_chain) or "丢骰子" == str(event.message_chain):
        ran = random.randint(1, 6)
        await send(event, Dice(ran))
    if str(event.message_chain).startswith('丢'):
        x = str(event.message_chain).replace('丢', '', 1)
        enum = ['1', '2', '3', '4', '5', '6', '一', '二', '三', '四', '五', '六', '壹',
                '贰', '叁', '肆', '伍', '陆', 'one', 'two', 'three', 'four', 'five', 'six']
        for i in range(24):
            if x == enum[i]:
                await send(event, Dice(i % 6+1))
                return



@Listen.member_join()
async def welcome_new_member(event):
    '''欢迎新成员'''
    await send(event.member, [At(event.member.id), ",热烈欢迎 "+event.member.member_name+" 加入本群！"]
               + [Face(face_id=99)]*3)
    await send_nudge(event.member.id, event.member.group.id, 'Group')


@Listen.group()
async def interact_with_owner(event):
    '''和主人互动'''
    if At(Config.bot_qq()) in event.message_chain and event.sender.id == Config.bot_owner_qq():
        reply = ["是的主人", "好的主人"]
        await send(event, random.choice(reply), True)


@Listen.friend()
async def owner_control(event):
    '''主人控制'''
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



@Listen.group()
async def hit_xiaobing(event):
    '''揍小冰'''
    if str(event.message_chain) == '揍小冰':
        try:
            await mute(event.sender.group.id, 2854196306, 600)
        except:
            await send(event, "这群没有小冰啊让我怎么揍", True)
        else:
            await send(event, "好，小冰已经被揍哑巴了，哈哈哈哈", True)


@Listen.group()
async def about_mute(event):
    '''禁言相关'''
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


@Listen.group()
async def about_repeat(event):
    '''复读相关'''
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


@Listen.group()
async def pin_picture(event):
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
            lst_pic = await my_filter(waiter, 'F', 30)

            if lst_pic is None:
                return
            elif event.message_chain.count(Image) >= 2:
                await send(event, "只能pin一张图片哦")
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
