# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import asyncio
import re
from random import randint

from mirai import At, Image, Plain

from utils.utils import Config, my_filter, send
from . import game_basic as gb
from . import minesweeper as ms
from .connect_balls import ConnectBalls
from .connectX import ConnectX
from .get10_AI import AIGet10
from .get_10 import Get10
from .gomoku_v3 import AntiTTT, AntiTTT_with_AI, Gomoku, Katagomo
from .jewishchess import JewishChess
from .mychess import PlayChess
from .nonogram import Nonogram
from .renju_eliminate import RenjuEliminate
from .reversi import Reversi
from .weiqi import Go, KataGo
from .wordle import Wordle

flag_of_ms = {}
flag_of_nn = {}
flag_of_wod = {}
flag_of_wod_single = {}


async def e_send_game_menu(event):
    from utils.text_engine import text_to_img
    await send(event, [], PIL_image=text_to_img(gb.get_game_menu()))


async def e_create_server(event, server_name):
    if event.sender.id == Config.bot_owner_qq():
        mesg = gb.create_server(server_name)
        await send(event, mesg)


async def e_register(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！", True)
    if gb.is_register(event.sender.id, server_name):
        await send(event, "您在当前服已注册！", True)
        return
    await send(event, "请在60s内输入您的昵称", True)

    def waiter(event2):
        if event.sender.id == event2.sender.id:
            nickname = str(event2.message_chain)
            return nickname

    nickname = await my_filter(waiter, 'G', 60)

    if nickname is None:
        await send(event, "注册超时！")
        return
    data = {'nickname': nickname,
            'qqid': event.sender.id,
            'gameid': '',
            'level': 0,
            'exp': 0,
            'LastSignInTime': '1.1.1',
            'money': 0,
            'wordle_win': 0,
            'wordle_lose': 0
            }

    game_id = gb.create_account(event.sender.id, server_name, data)
    await send(event, f'注册成功！您的游戏id是{game_id}')


async def e_check_in(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！", True)
    else:
        if not gb.is_register(event.sender.id, server_name):
            await send(event, "您还未注册！", True)
        else:
            mesg = gb.check_in(event.sender.id, server_name)
            await send(event, mesg, True)


async def e_look_file(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！", True)
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    pf = gb.get_player_file(event.sender.id, server_name)
    mesg = f'玩家昵称：{pf["nickname"]}\n账号id：{pf["gameid"]}\n等级：{pf["level"]}级{pf["exp"]}经验\n财富：{pf["money"]}金币\nwordle胜场：{pf["wordle_win"]}\n负场'
    if pf["wordle_win"] >= pf["wordle_lose"]*1.2:
        mesg += f'：{pf["wordle_lose"]}'
    else:
        mesg += '有点多，不展示'
    await send(event, mesg)


async def e_upgrade(event, server_name):
    mesg = gb.upgrade(event.sender.id, server_name)
    await send(event, mesg)


async def e_get_rich_list(event, server_name):
    rich_list = gb.get_rich_list(server_name)
    mesg = '富豪榜\n'
    for i in range(len(rich_list)):
        mesg += f'第{i+1}名：{rich_list[i]}'
        if i != len(rich_list)-1:
            mesg += '\n'
    await send(event, mesg)


async def e_get_poor_list(event, server_name):
    rich_list = gb.get_poor_list(server_name)
    if rich_list == []:
        await send(event, "当前本服没有负豪！")
        return
    mesg = '负豪榜\n'
    for i in range(len(rich_list)):
        mesg += f'第{i+1}名：{rich_list[i]}'
        if i != len(rich_list)-1:
            mesg += '\n'
    await send(event, mesg)


async def e_get_wordle_list(event, server_name, tp=0):
    # tp=0:胜局榜，tp=1:胜率榜(胜场>10才能上榜)
    wod_list = gb.get_wordle_list(server_name, tp)
    mesg = 'wordle胜局榜\n' if tp == 0 else 'wordle胜率榜\n'
    for i in range(len(wod_list)):
        mesg += f'第{i+1}名：{wod_list[i]}'
        if i != len(wod_list)-1:
            mesg += '\n'
    await send(event, mesg)


async def e_change_nickname(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！")
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    pf = gb.get_player_file(event.sender.id, server_name)
    price = 200
    if pf['money'] < price:
        await send(event, f'改名需要{price}金币，您当前只有{pf["money"]}金币！', True)
        return
    await send(event, f'您当前的昵称是{pf["nickname"]},改名需要花费{price}金币,请在60s内确认是否继续(y/n)')
    mesg = await yes_or_no_filter(event.sender.id, 60)
    if not mesg:
        await send(event, "改名已取消！", True)
        return
    await send(event, [At(event.sender.id), "\n请在120s内输入您的新昵称(直接输入，不需要/)"])

    def waiter(event2):
        if event2.sender.id == event.sender.id:
            return str(event2.message_chain)

    mesg = await my_filter(waiter, 'G', timeout=120)
    if mesg is None:
        await send(event, "超时！改名取消", True)
        return
    data = {'nickname': mesg}
    data2 = {'money': -200}
    gb.add_data(data2, event.sender.id, server_name)
    info = gb.change_data(data, event.sender.id, server_name)
    await send(event, info)
    await send(event, [At(event.sender.id), "改名成功！"])


async def give_money(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！")
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    await send(event, "请@赠送金币的对象+输入赠送金币的数量(20~1000个,手续费5%)")

    def waiter(event2):
        if event2.sender.id == event.sender.id:
            return event2.message_chain

    msg_chain = await my_filter(waiter, 'G', timeout=120)

    if msg_chain is None:
        await send(event, "超时！", True)
        return
    try:
        at = msg_chain.get_first(At)
        plain = msg_chain.get_first(Plain)
        qq_id = at.target
        num = int(str(plain))
    except Exception:
        await send(event, "指令错误！")
        return
    if qq_id == event.sender.id:
        await send(event, "不能给自己赠送！")
        return
    elif num < 20 or num > 1000:
        await send(event, "一次只能赠送20~1000金币！")
        return
    file = gb.get_player_file(event.sender.id, server_name)
    if num > file['money']:
        await send(event, "您没有这么多金币！")
        return
    num2 = num - num//20
    data1 = {'money': -num}
    data2 = {'money': num2}
    mesg = gb.add_data(data2, qq_id, server_name)
    if mesg == "该玩家还未注册！":
        await send(event, [At(event.sender.id), "您赠送的对象还未注册，赠送失败！"])
        return
    gb.add_data(data1, event.sender.id, server_name)
    await send(event, [At(event.sender.id), f"赠送成功,玩家{qq_id}获得{num2}金币！"])


async def e_tf_points_single(event, server_name, timeset='mid', num=1, points=24, extra_operator=False):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！")
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    for i in range(num):
        mesg = ''
        problem = gb.give_twentyfour_problem('simple')
        if timeset == 'easy' or timeset == 'e':
            rantime = randint(38, 55)
        elif timeset == 'mid' or timeset == 'm':
            rantime = randint(18, 35)
        elif timeset == 'hard' or timeset == 'h':
            rantime = randint(6, 12)
            points = randint(15, 30)
            mesg += f'\n{points}点'
        else:
            raise KeyError("timeset错误！")
        mesg += f'\n题目:{problem}\n限时:{rantime}秒'
        await send(event, [At(event.sender.id), mesg])

        def waiter(event2):
            if event.sender.id == event2.sender.id:
                answer = str(event2.message_chain)
                if answer == 'pass' or answer == '放弃' or answer == '过' or answer == '.':
                    return 0
                elif answer == '中止' or answer == 'end':
                    return -1
                if not answer.startswith('(') and not answer.startswith('（'):
                    try:
                        int(answer[0])
                    except:
                        return
                return answer

        answer = await my_filter(waiter, 'G', rantime)

        if answer is None:
            await send(event, [At(event.sender.id), "超时！"])
        elif answer == 0:
            await send(event, "您已放弃本题")
        elif answer == -1:
            await send(event, "已中止本轮游戏！")
            return
        else:
            mesg = gb.twentyfour_points_check(
                event.sender.id, answer, server_name, problem, timeset, points, extra_operator)
            await send(event, mesg)

        if i != num-1:
            await asyncio.sleep(1)
    if num > 1:
        await send(event, [At(event.sender.id), "本轮游戏结束！"])


async def e_tf_points_pk(event, server_name, num=3):
    re = await pk_invite(event, server_name, '24点')
    if re is None:
        return
    id1 = event.sender.id
    id2 = re[2]
    nickname1 = re[0]['nickname']
    nickname2 = re[1]['nickname']
    for i in range(num):
        wintime = {id1: 0, id2: 0}
        pass_request = {id1: 0, id2: 0}
        problem = gb.give_twentyfour_problem('simple')
        rantime = randint(60, 100)
        await send(event, [At(id1), At(id2), f'\n题目:{problem}\n限时:{rantime}秒'])

        def waiter(event2):
            if event2.sender.id == id1 or event2.sender.id == id2:
                answer = str(event2.message_chain)
                if answer == 'pass' or answer == '.':
                    pass_request[event2.sender.id] = 1
                    if pass_request[id1]+pass_request[id2] == 2:
                        pass_request[id1] = 0
                        pass_request[id2] = 0
                        return 0
                else:
                    if not answer.startswith('(') or answer.startswith('（'):
                        try:
                            int(answer[0])
                        except:
                            return
                    mesg = gb.twentyfour_points_check(
                        event.sender.id, answer, server_name, problem, 'mid')
                    if mesg.startswith('回答正确！'):
                        wintime[event2.sender.id] += 1
                        return [mesg, event2.sender.id]

        mesg = await my_filter(waiter, 'G', timeout=rantime)

        if mesg is None:
            await send(event, [At(id1), At(id2), "超时！"])
        elif mesg == 0:
            await send(event, [At(id1), At(id2), "双方同意pass本题！"])
        else:
            await send(event, [At(mesg[1]), mesg[0]])
        continue
    if wintime[id1] > wintime[id2]:
        await send(event, [At(id1), f"恭喜{nickname1}获得本场pk胜利！"])
    elif wintime[id1] < wintime[id2]:
        await send(event, [At(id2), f"恭喜{nickname2}获得本场pk胜利！"])
    else:
        await send(event, [At(id1), At(id2), "本次pk平局！"])


async def nim_game(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！")
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    lst_rand = []
    ans = 0
    for i in range(randint(3, 5)):
        num = randint(1, 9)
        ans ^= num
        lst_rand.append(str(num))
    ans = True if num else False
    rantime = randint(30, 60)
    problem = f'请在{rantime}s内作答,用y/n表示先手必胜或必败。\n问题：'+'，'.join(lst_rand)
    await send(event, problem)

    def waiter(event2):
        if event2.sender.id == event.sender.id:
            if str(event2.message_chain) == 'y':
                return True
            elif str(event2.message_chain) == 'n':
                return False

    mesg = await my_filter(waiter, timeout=rantime)

    if mesg is None:
        await send(event, "超时了！经验+1，金币-5", True)
    elif mesg == ans:
        await send(event, "恭喜答对！经验+10，金币+5", True)
        data = {'exp': 10, 'money': 5}
        gb.add_data(data, event.sender.id, server_name)
    else:
        data = {'exp': 1, 'money': -20}
        gb.add_data(data, event.sender.id, server_name)
        await send(event, "答错了！经验+1，金币-20", True)


async def recite_wushiyin(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！", True)
        return
    mode = -1
    x = str(event.message_chain).replace('/五十音', '', 1).replace(' ', '')
    if x.startswith('平'):
        x = x.replace('平', '')
        mode = 0
    elif x.startswith('片'):
        x = x.replace('片', '')
        mode = 1
    if x == '':
        num = 10
    else:
        try:
            num = int(x)
        except:
            await send(event, "指令错误", True)
            return
        else:
            if num < 3 or num > 20:
                await send(event, "单词数量应为3~20的整数", True)
                return
    pingjm = {
        'あ': ['a'], 'い': ['i', 'yi'], 'う': ['u'], 'え': ['e'], 'お': ['o'],
        'か': ['ka'], 'き': ['ki'], 'く': ['ku'], 'け': ['ke'], 'こ': ['ko'],
        'さ': ['sa'], 'し': ['si', 'shi'], 'す': ['su'], 'せ': ['se'], 'そ': ['so'],
        'た': ['ta'], 'ち': ['ti', 'chi'], 'つ': ['tu', 'tsu'], 'て': ['te'], 'と': ['to'],
        'な': ['na'], 'に': ['ni'], 'ぬ': ['nu'], 'ね': ['ne'], 'の': ['no'],
        'は': ['ha'], 'ひ': ['hi'], 'ふ': ['hu', 'fu'], 'へ': ['he'], 'ほ': ['ho'],
        'ま': ['ma'], 'み': ['mi'], 'む': ['mu'], 'め': ['me'], 'も': ['mo'],
        'や': ['ya'], 'ゆ': ['yu'], 'よ': ['yo'],
        'ら': ['ra'], 'り': ['ri'], 'る': ['ru'], 'れ': ['re'], 'ろ': ['ro'],
        'わ': ['wa'], 'を': ['wo'],  # 'ゐ':['wi'],'ゑ':['we'],
        'ん': ['n'],
        'が': ['ga'], 'ぎ': ['gi'], 'ぐ': ['gu'], 'げ': ['ge'], 'ご': ['go'],
        'ざ': ['za'], 'じ': ['zi'], 'ず': ['zu'], 'ぜ': ['ze'], 'ぞ': ['zo'],
        'だ': ['da'], 'ぢ': ['di'], 'づ': ['du'], 'で': ['de'], 'ど': ['do'],
        'ば': ['ba'], 'び': ['bi'], 'ぶ': ['bu'], 'べ': ['be'], 'ぼ': ['bo'],
        'ぱ': ['pa'], 'ぴ': ['pi'], 'ぷ': ['pu'], 'ぺ': ['pe'], 'ぽ': ['po']
    }
    pianjm = {
        'ア': ['a'], 'イ': ['i', 'yi'], 'ウ': ['u'], 'エ': ['e'], 'オ': ['o'],
        'カ': ['ka'], 'キ': ['ki'], 'ク': ['ku'], 'ケ': ['ke'], 'コ': ['ko'],
        'サ': ['sa'], 'シ': ['si', 'shi'], 'ス': ['su'], 'セ': ['se'], 'ソ': ['so'],
        'タ': ['ta'], 'チ': ['ti', 'chi'], 'ツ': ['tu', 'tsu'], 'テ': ['te'], 'ト': ['to'],
        'ナ': ['na'], 'ニ': ['ni'], 'ヌ': ['nu'], 'ネ': ['ne'], 'ノ': ['no'],
        'ハ': ['ha'], 'ヒ': ['hi'], 'フ': ['hu', 'fu'], 'ヘ': ['he'], 'ホ': ['ho'],
        'マ': ['ma'], 'ミ': ['mi'], 'ム': ['mu'], 'メ': ['me'], 'モ': ['mo'],
        'ヤ': ['ya'], 'ユ': ['yu'], 'ヨ': ['yo'],
        'ラ': ['ra'], 'リ': ['ri'], 'ル': ['ru'], 'レ': ['re'], 'ロ': ['ro'],
        'ワ': ['wa'], 'ヲ': ['wo'],
        'ン': ['n'],
        'ガ': ['ga'], 'ギ': ['gi'], 'グ': ['gu'], 'ゲ': ['ge'], 'ゴ': ['go'],
        'ザ': ['za'], 'ジ': ['zi'], 'ズ': ['zu'], 'ゼ': ['ze'], 'ゾ': ['zo'],
        'ダ': ['da'], 'ヂ': ['di'], 'ヅ': ['du'], 'デ': ['de'], 'ド': ['do'],
        'バ': ['ba'], 'ビ': ['bi'], 'ブ': ['bu'], 'ベ': ['be'], 'ボ': ['bo'],
        'パ': ['pa'], 'ピ': ['pi'], 'プ': ['pu'], 'ペ': ['pe'], 'ポ': ['po']
    }
    timeout = 10
    await send(event, '五十音抢答已准备,在60s内输入"开始"以开始竞赛！')

    def waiter(event2):
        answer = str(event2.message_chain)
        if answer == 'end' or answer == 'cancel' or answer == '取消':
            return 0
        elif answer == '开始' or answer == 'start':
            return 1

    start = await my_filter(waiter, 'G', timeout=60)

    if start is None or start == 0:
        await send(event, "五十音抢答已取消!", True)
        return
    winner = {}
    fail_word = []
    for i in range(num):
        if mode == 0:
            dic = pingjm
        elif mode == 1:
            dic = pianjm
        else:
            dic = [pingjm, pianjm][randint(0, 1)]
        k = list(dic.keys())[randint(0, len(dic)-1)]
        mesg = f'第({i+1}/{num})题,时限:{timeout}秒\n请输入音标：{k}'
        await send(event, mesg)

        def waiter(event2):
            answer = str(event2.message_chain)
            if answer in dic[k]:
                return event2.sender.id
            elif event2.sender.id in Config.get()['game_admin'] and answer == '/关闭':
                return -1

        qq_id = await my_filter(waiter, 'G', timeout=timeout)

        if qq_id == -1:
            break
        answer = f'{k}:'+','.join(dic[k])
        if qq_id is not None:
            if qq_id in winner:
                winner[qq_id] += 1
            else:
                winner[qq_id] = 1
        else:
            if i != num-1:
                await send(event, f"时间到!\n正确答案：{answer}\n2s后继续下一题")
                fail_word.append(k)
                await asyncio.sleep(2)
                continue
            else:
                await send(event, f"时间到!\n正确答案：{answer}")
                fail_word.append(k)
                break
        if i != num-1:
            await send(event, [At(qq_id), f" 首先回答正确!\n积分+1,当前积分{winner[qq_id]}\n正确答案：{answer}\n2s后继续下一题"])
            await asyncio.sleep(2)
        else:
            await send(event, [At(qq_id), f" 首先回答正确!\n积分+1,当前积分{winner[qq_id]}\n正确答案：{answer}"])
    end_mesg_chain = ['游戏结束！本轮五十音抢答得分如下：']
    for k in sorted(winner, key=winner.__getitem__, reverse=True):
        end_mesg_chain.append(f'\n{winner[k]} ')
        end_mesg_chain.append(At(k))
    await send(event, end_mesg_chain)
    mesg_chain_fail = []
    for k in winner:
        pf = gb.get_player_file(k, server_name)
        if pf is None:
            mesg_chain_fail.append(At(k))
        else:
            adddata = {'exp': 3*winner[k], 'money': 1*winner[k]}
            gb.add_data(adddata, k, server_name)
    if mesg_chain_fail == []:
        await send(event, "以上每积分已转换成3经验,1金币发放!")
    else:
        mesg_chain_fail.append(' 由于未注册无法发放金币经验,其他玩家每积分已转换成3经验,1金币发放!')
        await send(event, mesg_chain_fail)
    if fail_word != []:
        mesg = '本轮以下假名无人答对：\n'+','.join(fail_word)
        await send(event, mesg)


async def recite_words(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "本群当前未开服！", True)
        return
    x = str(event.message_chain).replace('/背单词', '', 1).replace(' ', '')
    lst_books = ['CET4', 'CET6', 'GRE', 'IELTS', 'KAOYAN', 'TOEFL']
    path = 'statics/words/TOEFL.json'
    for b in lst_books:
        if x.startswith(b):
            path = f'statics/words/{b}.json'
            x = x.replace(b, '', 1)
            break
    if x == '':
        num = 5
    else:
        try:
            num = int(x)
        except:
            await send(event, "指令错误", True)
            return
        else:
            if num < 3 or num > 20:
                await send(event, "单词数量应为3~20的整数", True)
                return
    with open(path, 'r', encoding='UTF-8') as f:
        import json
        dict_words = json.load(f)
    lst_words = list(dict_words.values())
    timeout = 20
    remind_time = 10
    await send(event, f'背{b}单词竞赛已准备,在60s内输入"开始"以开始单词竞赛！')

    def waiter(event2):
        answer = str(event2.message_chain)
        if answer == 'end' or answer == 'cancel' or answer == '取消':
            return 0
        elif answer == '开始' or answer == 'start':
            return 1

    start = await my_filter(waiter, 'G', timeout=60)

    if start is None or start == 0:
        await send(event, "背单词已取消!", True)
        return
    winner = {}
    fail_word = []
    for i in range(num):
        ran = randint(0, len(lst_words)-1)
        dict_a_word = lst_words[ran]
        word = dict_a_word['word']
        trs = dict_a_word['trans']
        mesg = f'第({i+1}/{num})题,时限:{timeout}秒'
        str_trs = ''
        for tr in trs:
            str_trs += f'\n[{tr["pos"]}] {tr["tran"]}'
        mesg += str_trs+f'\n这个单词有{len(word)}个字母'
        await send(event, mesg)

        def waiter(event2):
            answer = str(event2.message_chain)
            if answer == word:
                return event2.sender.id
            elif event2.sender.id in Config.get()['game_admin'] and answer == '/关闭':
                return -1

        qq_id = await my_filter(waiter, 'G', timeout=remind_time)

        if qq_id == -1:
            break
        if qq_id is not None:
            if qq_id in winner:
                winner[qq_id] += 1
            else:
                winner[qq_id] = 1
        else:
            n = int(len(word)/2)
            remind_word = word[:n]
            mesg2 = f'{remind_time}s内没人猜出来哦，给个提示:这个单词的前{n}个字母是{remind_word}'
            await send(event, mesg2)

            def waiter(event2):
                answer = str(event2.message_chain)
                if answer == word:
                    return event2.sender.id

            qq_id = await my_filter(waiter, 'G', timeout=timeout-remind_time)

            if qq_id is not None:
                if qq_id in winner:
                    winner[qq_id] += 1
                else:
                    winner[qq_id] = 1
            else:
                if i != num-1:
                    await send(event, f"时间到!\n正确答案:{word}{str_trs}\n\n3s后继续下一题")
                    fail_word.append(word)
                    await asyncio.sleep(3)
                    continue
                else:
                    await send(event, f"时间到!\n正确答案:{word}{str_trs}")
                    fail_word.append(word)
                    break
        if i != num-1:
            await send(event, [At(qq_id), f" 首先回答正确!\n积分+1,当前积分{winner[qq_id]}\n正确答案:{word}{str_trs}\n\n3s后继续下一题"])
            await asyncio.sleep(3)
        else:
            await send(event, [At(qq_id), f" 首先回答正确!\n积分+1,当前积分{winner[qq_id]}\n正确答案:{word}{str_trs}"])
    end_mesg_chain = ['游戏结束！本轮背单词得分如下：']
    for k in sorted(winner, key=winner.__getitem__, reverse=True):
        end_mesg_chain.append(f'\n{winner[k]} ')
        end_mesg_chain.append(At(k))
    await send(event, end_mesg_chain)
    mesg_chain_fail = []
    for k in winner:
        pf = gb.get_player_file(k, server_name)
        if pf is None:
            mesg_chain_fail.append(At(k))
        else:
            adddata = {'exp': 5*winner[k], 'money': 3*winner[k]}
            gb.add_data(adddata, k, server_name)
    if mesg_chain_fail == []:
        await send(event, "以上每积分已转换成5经验,3金币发放!")
    else:
        mesg_chain_fail.append(' 由于未注册无法发放金币经验,其他玩家每积分已转换成5经验,3金币发放!')
        await send(event, mesg_chain_fail)
    if fail_word != []:
        mesg = '本轮以下单词无人答对：\n'+','.join(fail_word)
        await send(event, mesg)


async def play_game(event, server_name):
    game_banned_group = Config.get()['game_banned_group']
    if event.group.id in game_banned_group:
        return
    if str(event.message_chain) == '/游戏' or str(event.message_chain) == '/game':
        await e_send_game_menu(event)
    elif str(event.message_chain) == '/开服':
        await e_create_server(event, server_name)
    elif str(event.message_chain) == "/注册" or str(event.message_chain) == "/register":
        await e_register(event, server_name)
    elif str(event.message_chain) == "/签到" or str(event.message_chain) == "/checkin":
        await e_check_in(event, server_name)
    elif str(event.message_chain) == "/档案" or str(event.message_chain) == "/file":
        await e_look_file(event, server_name)
    elif str(event.message_chain) == "/升级" or str(event.message_chain) == "/upgrade":
        await e_upgrade(event, server_name)
    elif str(event.message_chain) == "/改名":
        await e_change_nickname(event, server_name)
    elif str(event.message_chain).startswith("/扫雷"):
        await play_minesweeper(event, server_name)
    elif str(event.message_chain).startswith("/wordle"):
        if '-s' in str(event.message_chain):
            await play_wordle_single(event, server_name)
        else:
            await play_wordle(event, server_name)
    elif str(event.message_chain) == "/数织" or str(event.message_chain) == "/nonogram":
        await play_nonogram(event, server_name)
    elif str(event.message_chain) == '/连珠消消乐':
        await play_renju_eliminate(event, server_name)
    elif str(event.message_chain) == '/趣味连线':
        await play_connect_balls(event, server_name)
    elif str(event.message_chain) == "/合成十":
        await play_get10(event, server_name)

    elif str(event.message_chain) == "/合成十AI":
        ai = AIGet10(5, 5)
        await send(event, "请稍等", True)
        gif_bt, score = ai.quick_AI_game_gif_bytes()
        await send(event, [f'AI本局得分：{score}'], img_bytes=gif_bt)

    elif str(event.message_chain) == "/24点" or str(event.message_chain) == "/24":
        await e_tf_points_single(event, server_name)
    elif str(event.message_chain) == "/nim":
        await nim_game(event, server_name)
    elif str(event.message_chain).startswith('/24') and str(event.message_chain).startswith('/24pk') == False:
        x = str(event.message_chain).replace('/24', '', 1).replace(' ', '')
        lst_timeset = ['e', 'm', 'h']
        flag = True
        for t in lst_timeset:
            if t in x:
                x = x.replace(t, '', 1)
                flag = False
                break
        if flag:
            t = 'm'
        if x == '':
            await e_tf_points_single(event, server_name, t)
        else:
            try:
                num = int(x)
            except ValueError:
                await send(event, "指令错误", True)
                return
            if num <= 0 or num > 10:
                await send(event, "题数只能为1~10间的数哦")
                return
            else:
                await e_tf_points_single(event, server_name, t, num)
    elif str(event.message_chain).startswith("/24pk"):
        x = str(event.message_chain.get(Plain, 1)[0]).replace(
            "/24pk", '').replace(' ', '')
        try:
            num = int(x)
        except ValueError:
            await e_tf_points_pk(event, server_name)
        else:
            if num <= 0 or num > 10:
                await send(event, "一次只能pk1~10道题", True)
                return
            await e_tf_points_pk(event, server_name, num)

    elif str(event.message_chain) == "/富豪榜":
        await e_get_rich_list(event, server_name)
    elif str(event.message_chain) == "/负豪榜":
        await e_get_poor_list(event, server_name)
    elif str(event.message_chain) == "/猜词榜":
        await e_get_wordle_list(event, server_name)
    elif str(event.message_chain) == "/猜词胜率榜":
        await e_get_wordle_list(event, server_name, 1)
    elif str(event.message_chain).startswith('/背单词'):
        await recite_words(event, server_name)
    elif str(event.message_chain).startswith('/五十音'):
        await recite_wushiyin(event, server_name)
    elif str(event.message_chain) == '/赠送':
        await give_money(event, server_name)


async def send_pk_invite(event, server_name, tp):
    id1 = event.sender.id
    try:
        pf1 = gb.get_player_file(id1, server_name)
    except FileNotFoundError:
        await send(event, "本群当前未开服！")
        return
    if pf1 is None:
        await send(event, "您还未注册！")
        return
    if event.message_chain.count(At) == 0:
        await send(event, "请在30s内@你想邀请pk的对手", True)

        def waiter(event2):
            if event.sender.id == event2.sender.id:
                if event2.message_chain.count(At) == 1:
                    at = event2.message_chain.get(At)
                    return at
                elif str(event.message_chain) == "取消" or str(event.message_chain) == "cancel":
                    return

        at = await my_filter(waiter, 'G', timeout=30)

    elif event.message_chain.count(At) >= 2:
        await send(event, "一次只能和一个人pk哦", True)
        return
    else:
        at = event.message_chain.get(At)
    if at is None:
        await send(event, "请求已取消！", True)
        return
    id2 = at[0].target
    if id1 == id2:
        await send(event, "不能和自己pk哦！")
        return
    elif id2 == Config.bot_qq():
        await chess_pk_ai(event, server_name, tp)
        return
    pf2 = gb.get_player_file(id2, server_name)
    if pf2 is None:
        await send(event, "该玩家还未注册！")
        return
    return pf1, pf2, id2


async def respond_to_pk_invite(id1, id2, timeout):
    def waiter(event2):
        if event2.sender.id == id2:
            if str(event2.message_chain) == '接受' or str(event2.message_chain) == 'accept' or str(event2.message_chain) == 'y':
                return 1
            elif str(event2.message_chain) == '拒绝' or str(event2.message_chain) == 'decline' or str(event2.message_chain) == 'n':
                return 0
        elif event2.sender.id == id1:
            if str(event2.message_chain) == '取消':
                return 0

    is_accept = await my_filter(waiter, 'G', timeout=timeout)

    if is_accept is None:
        is_accept = 0
    return is_accept


async def pk_invite(event, server_name, tp):
    pf = await send_pk_invite(event, server_name, tp)
    if pf is None:
        return
    id1 = event.sender.id
    id2 = pf[2]
    timeout = 120
    kw = ['国际象棋', '围棋', '五子棋', '黑白棋', '重力棋', '反井字棋', '犹太人棋']
    sign = kw[tp] if type(tp) is int else tp
    await send(event, [At(id2), f'\n{pf[0]["nickname"]}向您发起{sign}pk，请在{timeout}s内发送“接受”或“拒绝”'])
    is_accept = await respond_to_pk_invite(id1, id2, timeout)
    if not is_accept:
        await send(event, "pk申请已取消！", True)
        return
    return pf[0], pf[1], id2


async def yes_or_no_filter(qqid, timeout):
    def waiter(event2):
        answer = str(event2.message_chain)
        if event2.sender.id == qqid:
            if answer == 'yes' or answer == 'y' or answer == '同意' or answer == '接受':
                return True
            elif answer == 'no' or answer == 'n' or answer == '不同意' or answer == '拒绝':
                return False

    mesg = await my_filter(waiter, 'G', timeout=timeout)

    if mesg is None:
        mesg = False
    return mesg


class ChessType:
    CHESS = 0
    GO = 1
    GOMOKU = 2
    REVERSI = 3
    CONNECT_X = 4
    ANTITTT = 5
    JEWISH = 6
    class_name = [PlayChess, Go, Gomoku,
                  Reversi, ConnectX, AntiTTT, JewishChess]


async def send_draw_mesg(id1, id2, nickname1, nickname2, num, event, server_name):
    if num <= 3:
        await send(event, "3手内对局无效，不加经验金币！")
        return
    await send(event, [At(id1), At(id2), "\n游戏结束，双方和棋！"])
    adddata = {'exp': 25, 'money': 15}
    gb.add_data(adddata, id1, server_name)
    gb.add_data(adddata, id2, server_name)
    await send(event, f"玩家 {nickname1} 和 {nickname2}:\n经验+{adddata['exp']},金币+{adddata['money']}！")


async def send_win_mesg(winner_id, loser_id, winner_name, loser_name, num, event, server_name):
    if num <= 3:
        await send(event, "3手内对局无效，不加经验金币！")
        return
    await send(event, [At(winner_id), At(loser_id), f"\n游戏结束，{winner_name} 获得胜利！"])
    adddata1 = {'exp': 50, 'money': 30}
    adddata2 = {'exp': 10, 'money': -15}
    gb.add_data(adddata1, winner_id, server_name)
    gb.add_data(adddata2, loser_id, server_name)
    await send(event, f"""{winner_name} 经验+{adddata1['exp']},金币+{adddata1['money']}！
{loser_name} 经验+{adddata2['exp']},金币{adddata2['money']}！""")


async def play_chess(event, server_name, tp):
    res = await pk_invite(event, server_name, tp)
    if res is None:
        return
    qqid = [event.sender.id, res[2]]
    players = [res[0]['nickname'], res[1]['nickname']]
    if players[0] == players[1]:
        for i in (0, 1):
            gameid = gb.get_player_file(qqid[i], server_name)['gameid']
            players[i] += f'(gameid={gameid})'
    if randint(0, 1):
        qqid[0], qqid[1] = qqid[1], qqid[0]
        players[0], players[1] = players[1], players[0]
    chs = ChessType.class_name[tp](players=players)
    await send(event, [At(qqid[chs.turn]), f"\n{players[chs.turn]} 先行"])
    await send(event, [], img_bytes=chs.get_img_bytes())
    flag_of_undo = {qqid[0]: 3, qqid[1]: 3}
    flag_of_od = {qqid[0]: 3, qqid[1]: 3}
    while True:
        def waiter(event2):
            if event2.sender.id == qqid[chs.turn]:
                answer = str(event2.message_chain)
                if answer == 'resign' or answer == '认输' or answer == '投降':
                    return -1
                elif answer == 'od' or answer == '提和' or answer == '求和':
                    return -3
                else:
                    if tp == ChessType.CHESS and re.search('[A-Qa-q0][\w-]+', answer) and 1 < len(answer) < 6:
                        return answer
                    elif tp == ChessType.CONNECT_X and len(answer) == 1:
                        try:
                            int(answer)
                            return answer
                        except:
                            pass
                    elif tp == ChessType.JEWISH and \
                            (re.search('[\d+][,.。][\d+]', answer) or re.search('[\d+][,.。][\d+][,.。][\d+][,.。][\d+]', answer)):
                        return answer
                    elif re.search('[\d+][,.。][\d+]', answer) and 1 < len(answer) < 6:
                        return answer
            elif event2.sender.id == qqid[not chs.turn]:
                answer = str(event2.message_chain)
                if answer == 'undo' or answer == '悔棋':
                    return -2

        move = await my_filter(waiter, 'G', timeout=600)

        if move is None:
            await send(event, [f"{players[chs.turn]} 超时判负！"])
            await send_win_mesg(qqid[not chs.turn], qqid[chs.turn], players[not chs.turn], players[chs.turn],
                                chs.num, event, server_name)
            break
        elif move == -1:
            await send(event, [f"{players[chs.turn]} 认输！"])
            await send_win_mesg(qqid[not chs.turn], qqid[chs.turn], players[not chs.turn], players[chs.turn],
                                chs.num, event, server_name)
            break
        elif move == -2:
            if flag_of_undo[qqid[not chs.turn]] <= 0:
                await send(event, [At(qqid[not chs.turn]), "\n您本局的悔棋次数已用光！"])
                continue
            flag_of_undo[qqid[not chs.turn]] -= 1
            await send(event, [At(qqid[chs.turn]), f"\n{players[not chs.turn]} 请求悔棋，您是否同意？(y/n)"])
            mesg = await yes_or_no_filter(qqid[chs.turn], 60)
            if not mesg:
                await send(event, [At(qqid[0]), At(qqid[1]), f'\n{players[chs.turn]} 不同意悔棋！游戏继续'])
                await send(event, [], img_bytes=chs.get_img_bytes())
                continue
            try:
                chs.undo()
            except Exception as e:
                await send(event, [At(qqid[not chs.turn]), str(e)])
                continue
            await send(event, [], img_bytes=chs.get_img_bytes())
            await send(event, [At(qqid[chs.turn]), '悔棋成功！请下棋'])
            continue
        elif move == -3:
            if flag_of_od[qqid[chs.turn]] <= 0:
                await send(event, [At(qqid[chs.turn]), "您本局的提和次数已用光！"])
                continue
            flag_of_od[qqid[chs.turn]] -= 1
            await send(event, [At(qqid[not chs.turn]), f"\n{players[chs.turn]} 请求和棋，您是否同意？(y/n)"])
            mesg = await yes_or_no_filter(qqid[not chs.turn], 60)
            if mesg:
                await send_draw_mesg(qqid[0], qqid[1], players[0], players[1],
                                     chs.num, event, server_name)
                break
            else:
                await send(event, [At(qqid[0]), At(qqid[1]), f'\n{players[not chs.turn]} 不同意和棋！游戏继续'])
                await send(event, [], img_bytes=chs.get_img_bytes())
                continue
        try:
            mesg = chs.play(move, players[chs.turn])
        except Exception as e:
            await send(event, [At(qqid[chs.turn]), str(e)])
            continue
        if mesg is not None:
            await send(event, [], img_bytes=chs.get_img_bytes())
            if chs.outcome == 2:
                await send_draw_mesg(qqid[0], qqid[1], players[0], players[1],
                                     chs.num, event, server_name)
            else:
                if tp == ChessType.REVERSI:
                    if chs.outcome == -1:
                        await send(event, f"{players[not chs.turn]} 无处可走,{players[chs.turn]}继续下棋！")
                        continue
                    await send(event, f"黑子：{mesg[0]}个\n白子：{mesg[1]}个")
                await send_win_mesg(qqid[chs.outcome], qqid[not chs.outcome], players[chs.outcome],
                                    players[not chs.outcome], chs.num, event, server_name)
            break
        await send(event, [], img_bytes=chs.get_img_bytes())
        await send(event, [At(qqid[chs.turn]), f"\n轮到 {players[chs.turn]} 下棋"])

    await send(event, [At(qqid[0]), At(qqid[1]), "\n本局的棋谱动图如下"])
    await send(event, [], img_bytes=chs.get_gif())


async def chess_pk_ai(event, server_name, tp):
    if tp != ChessType.ANTITTT and tp != ChessType.GOMOKU:
        await send(event, "当前暂不支持该棋类挑战AI！")
        return
    pf = gb.get_player_file(event.sender.id, server_name)
    name = pf['nickname']
    qqid = event.sender.id
    AI_turn = randint(0, 1) if tp == ChessType.ANTITTT else 1
    players = [name, 'AI'] if AI_turn else ['AI', name]
    if tp == ChessType.ANTITTT:
        chs = AntiTTT_with_AI(players=players)
        await send(event, f"{players[0]} 执黑先行")
    elif tp == ChessType.GOMOKU:
        chs = Katagomo(players, Config.get()['katagomo_command'])
        await send(event, [At(qqid), "爷让你先走"])
    await send(event, [], img_bytes=chs.get_img_bytes())
    flag_of_undo = 3
    while True:
        if chs.turn == AI_turn:
            await send(event, "到我下棋了，让我想想")
            mesg = chs.AI_play()
        else:
            await send(event, [At(qqid), " 该你下棋了！"])

            def waiter(event2):
                if event2.sender.id == qqid:
                    answer = str(event2.message_chain)
                    if answer == 'resign' or answer == '认输' or answer == '投降':
                        return -1
                    elif answer == 'undo' or answer == '悔棋':
                        return -2
                    elif answer == 'od' or answer == '提和' or answer == '求和':
                        return -3
                    else:
                        if tp == ChessType.CHESS and re.search('[A-Qa-q0][\w-]+', answer) and 1 < len(answer) < 6:
                            return answer
                        elif tp == ChessType.CONNECT_X and len(answer) == 1:
                            try:
                                int(answer)
                                return answer
                            except:
                                pass
                        elif re.search('[\d+][,.。][\d+]', answer) and 1 < len(answer) < 6:
                            return answer

            move = await my_filter(waiter, 'G', timeout=300)

            if move is None:
                await send(event, [At(qqid), ' 你超时了，爷赢了！'])
                break
            elif move == -1:
                await send(event, [f"哈哈哈,{name},你这臭棋篓子终于认输了"])
                break
            elif move == -2:
                if flag_of_undo <= 0:
                    await send(event, [At(qqid), " 悔了多少次了还想悔棋？不让你悔！"])
                    continue
                try:
                    chs.player_undo()
                except Exception as e:
                    await send(event, [At(qqid), str(e)])
                    continue
                await send(event, [], img_bytes=chs.get_img_bytes())
                await send(event, [At(qqid), ' 臭棋篓子让你悔棋又何妨'])
                continue
            elif move == -3:
                await send(event, "爷不准你提和！")
                continue
            try:
                mesg = chs.play(move, players[chs.turn])
            except Exception as e:
                await send(event, [At(qqid), str(e)])
                continue
        if mesg is not None:
            await send(event, [], img_bytes=chs.get_img_bytes())
            if chs.outcome == 2:
                await send(event, [At(qqid), " 你好强,竟然和我打了个平手！\n我赏你50经验30金币！"])
                data = {'exp': 50, 'money': 30}
                gb.add_data(data, qqid, server_name)
            else:
                if tp == ChessType.REVERSI:
                    if chs.outcome == -1:
                        await send(event, f"{players[not chs.turn]} 无处可走,{players[chs.turn]}继续下棋！")
                        continue
                    await send(event, f"黑子：{mesg[0]}个\n白子：{mesg[1]}个")
                if chs.outcome == AI_turn:
                    await send(event, [At(qqid), f" 哈哈哈,{name},你这臭棋篓子败给我了吧"])
                else:
                    await send(event, [At(qqid), " 你好强,竟然赢了我！\n我赏你100经验60金币！"])
                    data = {'exp': 100, 'money': 60}
                    gb.add_data(data, qqid, server_name)
            break
        await send(event, [], img_bytes=chs.get_img_bytes())
    await send(event, [At(qqid), "\n本局的棋谱动图如下"])
    await send(event, [], img_bytes=chs.get_gif())


async def chess_main(event, server_name):
    if str(event.message_chain) == '/katago':
        await katago(event, server_name, ChessType.GO)
        return
    if str(event.message_chain) == '/katagomo':
        await katago(event, server_name, tp=ChessType.GOMOKU)
        return
    kw = [
        ['/chess', '/国际象棋'],
        ['/weiqi', '/go', '/围棋'],
        ['/五子棋', '/gomoku'],
        ['/黑白棋', '/翻转棋', '/奥赛罗', '/reversi', '/othello'],
        ['/下棋', '/connectx', '/下落棋', '/重力棋'],
        ['/反井字棋', '/antittt'],
        ['/犹太人棋']
    ]
    for i in range(len(kw)):
        for k in kw[i]:
            if str(event.message_chain).startswith(k):
                await play_chess(event, server_name, i)
                return


async def katago(event, server_name, tp):
    """katago分析"""
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    await send(event, 'katago启动中')
    classname = [None, KataGo, Katagomo]
    command = Config.get()['katago_command'] if tp == 1 else Config.get()[
        'katagomo_command']
    kata = classname[tp](command)
    await send(event, [], img_bytes=kata.get_img_bytes())
    await send(event, '分析中..')
    mesg = kata.analyse(300)
    await send(event, mesg)
    await send(event, [At(event.sender.id), ' 当前分析完成，请在120s内走子！'])
    while True:
        def waiter(event2):
            x = str(event2.message_chain)
            if event2.sender.id == event.sender.id:
                if (3 <= len(x) <= 5 and re.match('\d+[,.。，]\d+', x)) or \
                        (5 <= len(x) <= 7 and re.match('[(（)]\d+[,.。，]\d+[)）]', x)):
                    return x
                elif x == '关闭':
                    return -1
            if event2.sender.id in Config.get()['game_admin']:
                if x == '关闭':
                    return -1

        mesg = await my_filter(waiter, 'G', timeout=120)

        if mesg is None or mesg == -1:
            await send(event, [At(event.sender.id), "分析结束！"])
            break
        await send(event, '分析中..')
        try:
            mesg = kata.play_and_analyse(mesg)
        except ValueError as e:
            await send(event, str(e))
            continue
        if type(mesg) is int:
            await send(event, '棋局结束！')
            break
        await send(event, [], img_bytes=kata.get_img_bytes())
        await send(event, mesg)
        await send(event, [At(event.sender.id), '当前分析完成，请在120s内继续走子！'])
    await send(event, [At(event.sender.id), "\n本局的棋谱动图如下"])
    await send(event, [], img_bytes=kata.get_gif())


async def play_wordle_single(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    global flag_of_wod, flag_of_wod_single
    if event.sender.group.id in flag_of_wod and flag_of_wod[event.sender.group.id]:
        await send(event, "当前群正在进行多人wordle,不能同时进行单人wordle!", True)
        return
    try:
        flag_of_wod_single[event.sender.group.id] += 1
    except KeyError:
        flag_of_wod_single[event.sender.group.id] = 1
    if event.sender.id in Config.get()['wordle_zhendui']:
        wod = Wordle(
            4, mode=2) if '-sh' in str(event.message_chain) else Wordle(4)
    elif '-sh' in str(event.message_chain):
        wod = Wordle(mode=2)
    else:
        wod = Wordle()
    await send(event, [], PIL_image=wod.img)
    await send(event, [At(event.sender.id), "您的wordle游戏开始！"])
    while True:
        def waiter(event2):
            if event2.sender.id == event.sender.id:
                x = str(event2.message_chain)
                if x == '/放弃':
                    return -1
                if len(x) == 5 and re.match('[A-Za-z]{5}', x):
                    return x

        mesg = await my_filter(waiter, 'G', timeout=300)

        if mesg is None:
            data = {'money': -5, 'exp': 5, 'wordle_lose': 1}
            await send(event, [At(event.sender.id),
                               f"超时，wordle结束！经验+{data['exp']},金币{data['money']},wordle负场+1"])
            gb.add_data(data, event.sender.id, server_name)
            break
        if mesg == -1:
            data = {'money': -5, 'exp': 5, 'wordle_lose': 1}
            await send(event, [At(event.sender.id),
                               f"wordle已中止！经验+{data['exp']},金币{data['money']},wordle负场+1\n正确答案是：{wod.word0}"])
            gb.add_data(data, event.sender.id, server_name)
            break
        input_str = mesg
        try:
            mesg = wod.play(input_str)
        except ValueError as e:
            await send(event, str(e))
            continue
        await send(event, [At(event.sender.id)], PIL_image=wod.img)
        if mesg is None:
            continue
        elif mesg == 1:
            data = {'money': 10, 'exp': 15, 'wordle_win': 1}
            await send(event, [At(event.sender.id),
                               f"恭喜猜对！经验+{data['exp']},金币+{data['money']},wordle胜场+1\n正确答案是：{wod.word0}"])
            gb.add_data(data, event.sender.id, server_name)
            break
        elif mesg == 0:
            data = {'money': -5, 'exp': 5, 'wordle_lose': 1}
            await send(event, [At(event.sender.id),
                               f"很遗憾，猜词次数用光了！经验+{data['exp']},金币{data['money']},wordle负场+1\n正确答案是：{wod.word0}"])
            gb.add_data(data, event.sender.id, server_name)
            break
    flag_of_wod_single[event.sender.group.id] -= 1


async def play_wordle(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    global flag_of_wod, flag_of_wod_single
    if event.sender.group.id in flag_of_wod and flag_of_wod[event.sender.group.id]:
        await send(event, "当前已有一场多人wordle了！", True)
        return
    elif event.sender.group.id in flag_of_wod_single and flag_of_wod_single[event.sender.group.id] > 0:
        await send(event, "当前群正在进行单人wordle,不能同时进行多人wordle！", True)
        return
    flag_of_wod[event.sender.group.id] = True

    if '-e' in str(event.message_chain):
        wod = Wordle(7)
    elif '-h' in str(event.message_chain):
        wod = Wordle(5)
    else:
        wod = Wordle()
    await send(event, [], PIL_image=wod.img)
    await send(event, "wordle游戏开始！")

    while True:

        def waiter(event2):
            if event2.sender.group.id == event.sender.group.id:
                x = str(event2.message_chain)
                if event2.sender.id in Config.get()['game_admin'] and x == '/关闭':
                    return -1
                if len(x) == 5 and re.match('[A-Za-z]{%d}' % (wod.word_len), x):
                    return x, event2.sender.id

        mesg = await my_filter(waiter, 'G', timeout=300)

        if mesg is None:
            await send(event, "超时，wordle结束！")
            break
        if mesg == -1:
            await send(event, "管理员强制关闭多人wordle！")
            break
        input_str = mesg[0]

        try:
            mesg = wod.play(input_str)
        except ValueError as e:
            await send(event, str(e))
            continue
        await send(event, [], PIL_image=wod.img)
        if mesg is None:
            continue
        elif mesg == 1:
            await send(event, f"恭喜猜对！正确答案是：{wod.word0}")
            break
        elif mesg == 0:
            await send(event, f"很遗憾，猜词次数用光了！\n正确答案是：{wod.word0}")
            break

    flag_of_wod[event.sender.group.id] = False


async def play_minesweeper(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    global flag_of_ms
    try:
        if flag_of_ms[event.sender.group.id]:
            await send(event, "当前已有一场扫雷了！", True)
            return
    except KeyError:
        pass
    flag_of_ms[event.sender.group.id] = True
    if 'e' in str(event.message_chain):
        mine = ms.MineSweeper(9, 9, 10)
    elif 'm' in str(event.message_chain):
        mine = ms.MineSweeper(16, 16, 40)
    else:
        mine = ms.MineSweeper(10, 10, 15)
    await send(event, [], PIL_image=mine.draw_panel())
    winner = {}

    ms_admin = Config.get()['game_admin']
    while True:
        def waiter(event2):
            if event2.sender.group.id == event.sender.group.id:
                x = str(event2.message_chain)
                if event2.sender.id in ms_admin and x == '/关闭':
                    return -1
                if len(x) == 2 and re.match('[a-zA-Z][a-zA-z]', x):
                    return x, event2.sender.id

        mesg = await my_filter(waiter, 'G', timeout=120)

        if mesg is None:
            await send(event, "超时，扫雷结束！")
            flag_of_ms[event.sender.group.id] = False
            return
        if mesg == -1:
            await send(event, "管理员强制关闭扫雷！")
            break
        input_str = mesg[0]
        qq_id = mesg[1]
        try:
            location = ms.MineSweeper.parse_input(input_str)
            mine.mine(location[0], location[1])
        except Exception as e:
            await send(event, str(e))
            continue
        await send(event, [], PIL_image=mine.draw_panel())
        if mine.state == ms.GameState.FAIL:
            await send(event, [At(qq_id), "挖到雷了！扫雷失败"])

            if qq_id in winner:
                winner[qq_id] -= 10
            else:
                winner[qq_id] = -10
            break
        elif mine.state == ms.GameState.WIN:
            await send(event, "成功扫雷！")
            if qq_id in winner:
                winner[qq_id] += 2
            else:
                winner[qq_id] = 2
            break
        if qq_id in winner:
            winner[qq_id] += 1
        else:
            winner[qq_id] = 1

    flag_of_ms[event.sender.group.id] = False
    end_mesg_chain = ['游戏结束！本轮扫雷得分如下：']
    for k in sorted(winner, key=winner.__getitem__, reverse=True):
        end_mesg_chain.append(f'\n{winner[k]} ')
        end_mesg_chain.append(At(k))
    await send(event, end_mesg_chain)
    mesg_chain_fail = []
    for k in winner:
        pf = gb.get_player_file(k, server_name)
        if pf is None:
            mesg_chain_fail.append(At(k))
        else:
            adddata = {'exp': 4*winner[k], 'money': 2*winner[k]}
            gb.add_data(adddata, k, server_name)
    if mesg_chain_fail == []:
        await send(event, "以上每积分已转换成4经验,2金币发放!")
    else:
        mesg_chain_fail.append(' 由于未注册无法发放金币经验,其他玩家每积分已转换成4经验,2金币发放!')
        await send(event, mesg_chain_fail)


async def play_connect_balls(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    if not gb.is_register(event.sender.id, server_name):
        await send(event, "您还未注册！", True)
        return
    if randint(0, 1):
        game = ConnectBalls()
    else:
        game = ConnectBalls(6, 6, 7)
    await send(event, [At(event.sender.id), ' 趣味连线开始！'], PIL_image=game.get_img_PIL())
    while True:
        def waiter(event2):
            if event2.sender.id == event.sender.id:
                if event2.message_chain.count(Image) == 1:
                    return event2.message_chain.get(Image)[0]
                elif str(event2.message_chain) == '中止':
                    return -1

        mesg = await my_filter(waiter, 'G', timeout=120)

        if mesg is None:
            await send(event, [At(event.sender.id), "超时，趣味连线结束！"])
            break
        elif mesg == -1:
            await send(event, [At(event.sender.id), "趣味连线已中止！"])
            break
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(mesg.url) as resp:
                img_bytes = await resp.read()
        ret = game.play(img_bytes)
        if ret == False:
            await send(event, [At(event.sender.id), " 错误解！"])
            continue
        else:
            await send(event, [At(event.sender.id), ' 恭喜回答正确！经验+10,金币+5'])
            adddata = {'exp': 10, 'money': 5}
            gb.add_data(adddata, event.sender.id, server_name)
            break


async def play_renju_eliminate(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    col = row = 9
    game = RenjuEliminate(col, row)
    await send(event, [At(event.sender.id), ' 连珠消消乐开始！'], PIL_image=game.frames)
    while True:
        def waiter(event2):
            if event2.sender.id == event.sender.id:
                x = str(event2.message_chain)
                if re.search('[\d+][,.。][\d+][,.。][\d+][,.。][\d+]', x):
                    return x
                elif x == '中止':
                    return -1

        mesg = await my_filter(waiter, 'G', timeout=120)

        if mesg is None:
            await send(event, "超时，连珠消消乐结束！")
            break
        elif mesg == -1:
            await send(event, "连珠消消乐已中止！")
            break
        else:
            try:
                ret = game.play(mesg)
            except ValueError as e:
                await send(event, str(e))
                continue
        if ret == -1:
            await send(event, [At(event.sender.id), f" 棋盘已满，游戏结束！\n得分:{game.score}"])
            await send(event, [], PIL_image=game.frames)
            return
        else:
            await send(event, [At(event.sender.id), f' 当前得分:{game.score}'], PIL_image=game.frames)


async def play_get10(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    col = row = 5
    game = Get10(col, row)
    await send(event, [At(event.sender.id), ' 合成十开始！'], PIL_image=game.get_img_PIL())
    while True:
        def waiter(event2):
            if event2.sender.id == event.sender.id:
                x = str(event2.message_chain)
                if (3 <= len(x) <= 5 and re.match('\d+[,.。，]\d+', x)) or \
                        (5 <= len(x) <= 7 and re.match('[(（)]\d+[,.。，]\d+[)）]', x)):
                    return x
                elif x == '中止':
                    return -1

        mesg = await my_filter(waiter, 'G', timeout=120)

        if mesg is None:
            await send(event, "超时，合成十结束！")
            break
        elif mesg == -1:
            await send(event, "合成十已中止！")
            break
        else:
            try:
                ret = game.play(mesg)
            except ValueError as e:
                await send(event, str(e))
                continue
        if ret == -1:
            await send(event, [At(event.sender.id), f" 无可合并项，游戏结束！\n得分:{game.score}"])
            await send(event, [], PIL_image=game.frame)
            return
        else:
            await send(event, [At(event.sender.id), f' 当前得分:{game.score}'], PIL_image=game.frame)


async def play_nonogram(event, server_name):
    if not gb.is_server_open(server_name):
        await send(event, "当前群未开服！", True)
        return
    global flag_of_nn
    try:
        if flag_of_nn[server_name]:
            await send(event, "当前已有一场数织了！", True)
            return
    except KeyError:
        pass
    flag_of_nn[server_name] = True
    nono_admin = Config.get()['game_admin']
    nono = Nonogram()
    await send(event, [], PIL_image=nono.board_img())

    while True:
        def waiter(event2):
            if event2.sender.group.id == event.sender.group.id:
                x = str(event2.message_chain)
                if re.match('\d', x[0]) and re.match('\d', x[2]):
                    return x, event2.sender.id
            if event2.sender.id in nono_admin and x == '/关闭':
                return -1

        mesg = await my_filter(waiter, 'G', timeout=120)

        if mesg is None:
            await send(event, "超时，数织结束！")
            break
        elif mesg == -1:
            await send(event, "管理员强制关闭数织！")
            break
        input_str = mesg[0]
        try:
            mesg = nono.play(input_str)
        except Exception as e:
            await send(event, str(e))
            continue
        await send(event, [], PIL_image=nono.board_img())
        if mesg != -1:
            await send(event, f"游戏结束！共执行{mesg}次操作")
            break

    flag_of_nn[server_name] = False


async def game_admin(event, server_name):
    if event.sender.id not in Config.get()['game_admin']:
        return
    if str(event.message_chain).startswith('/give'):
        x = str(event.message_chain)
        x = x.replace('/give', '', 1)
        if x.startswith(' '):
            x = x.replace(' ', '', 1)
        keyw = ['m', 'e', 'l']
        lst_tp = ['money', 'exp', 'level']
        for i in range(len(keyw)):
            if keyw[i] in x:
                tp = lst_tp[i]
                qq_id = int(x[:x.index(keyw[i])])
                amount = int(x[x.index(keyw[i])+1:])
                data = {tp: amount}
                break
            if i == len(keyw)-1:
                await send(event, "指令错误")
                return
        mesg = gb.add_data(data, qq_id, server_name)
        await send(event, mesg)

    elif str(event.message_chain).startswith('/change'):
        x = str(event.message_chain)
        x = x.replace('/change', '', 1)
        if x.startswith(' '):
            x = x.replace(' ', '', 1)
        keyw = ['m', 'e', 'l', 'n']
        lst_tp = ['money', 'exp', 'level', 'nickname']
        for i in range(len(keyw)):
            if keyw[i] in x:
                tp = lst_tp[i]
                qq_id = int(x[:x.index(keyw[i])])
                amount = str(x[x.index(keyw[i])+1:])
                data = {tp: amount}
                break
            if i == len(keyw)-1:
                await send(event, "指令错误")
                return
        mesg = gb.change_data(data, qq_id, server_name)
        await send(event, mesg)

    elif str(event.message_chain).startswith('/ckf'):
        x = str(event.message_chain).replace('/ckf', '', 1)
        if x.startswith(' '):
            x = x.replace(' ', '', 1)
        try:
            qq_id = int(x)
        except ValueError:
            await send(event, "指令错误！")
            return
        if not gb.is_register(event.sender.id, server_name):
            await send(event, "该玩家还未注册！", True)
            return
        pf = gb.get_player_file(qq_id, server_name)
        mesg = f'qq号{qq_id}在本服的游戏信息：\n'\
            f'昵称：{pf["nickname"]}\n账号id：{pf["gameid"]}\n等级：{pf["level"]}级'\
            f'{pf["exp"]}经验\n财富：{pf["money"]}金币\n'\
            f'wordle胜场：{pf["wordle_win"]}\nwordle负场：{pf["wordle_lose"]}'
        await send(event, mesg)
