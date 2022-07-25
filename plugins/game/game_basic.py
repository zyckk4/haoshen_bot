# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import pandas as pd
import datetime
import random
import os
import re


def get_game_menu():
    # 输入/黑白棋s以预设开局开始
    game_menu = '''输入"/注册"或"register"以注册游戏账号开始游戏！
1./签到(或/checkin),/档案(或/file),/升级(或/upgrade),/改名执行对应操作
2.输入"/24"快速开始单人24点,输入“/24 e(或m,h,代表每题时间长短) x(1~10间的数代表总题数)”可以指定不同模式和题数
输入"/24pk"与他人pk24点(目前有无解情况,可以输入"."或"pass"或"过"或"放弃")
3.输入/重力棋,/五子棋,/反井字棋,/犹太人棋,/黑白棋,/围棋,/国际象棋+@你想对阵的玩家开始下棋！输入/反井字棋+@bot,与AI对弈！
4.输入"/背单词+你想背的词书+词数"开始背单词!目前可选词书有:CET4,CET6,GRE,TOEFL,KAOYAN,IELTS
5.输入"/五十音"快速开始五十音抢答竞赛,输入“/五十音+平(或片,或不填)+数量"自定义模式和题数
6.输入/扫雷,/数织，大家一起玩！输入/扫雷e或/扫雷m指定为标准的初级或中级难度扫雷'''
    return game_menu


def get_path(server_name):
    return f'data/game/{server_name}.xlsx'


def get_df(path, sheet_name="Sheet1", index_col=None, usecols=None):
    if not os.path.exists(path):
        raise FileNotFoundError("未找到服务器")
    return pd.read_excel(path, sheet_name=sheet_name, index_col=index_col, usecols=usecols)


def is_server_open(server_name):
    return os.path.exists(get_path(server_name))


def is_register(ID, server_name, way='qqid'):
    path = get_path(server_name)
    df = get_df(path)
    for i in range(df.shape[0]):
        if ID == df[way][i]:
            return True
    return False


def get_player_row(ID, server_name, way='qqid'):
    path = get_path(server_name)
    df = get_df(path)
    for i in range(df.shape[0]):
        if ID == df[way][i]:
            return i
    return


def get_gameid(qq_id, server_name):
    try:
        return get_player_file(qq_id, server_name)['gameid']
    except KeyError:
        return None


def get_player_file(ID, server_name, way='qqid') -> dict:
    path = get_path(server_name)
    df = get_df(path, index_col='qqid')
    try:
        player_file = df.loc[ID]
    except KeyError:
        return
    else:
        return player_file


def create_server(server_name: str):
    path = get_path(server_name)
    if os.path.exists(path):
        return "服务器已存在！"
    data = {'nickname': [],
            'qqid': [],
            'gameid': [],
            'level': [],
            'exp': [],
            'LastSignInDate': [],
            'money': [],
            'wordle_win': [],
            'wordle_lose': []
            }
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    return "开服成功！"


def create_account(qq_id, server_name, data):
    path = get_path(server_name)
    df = get_df(path)
    if is_register(qq_id, server_name):
        return -1
    game_id = df.shape[0]+1
    data['gameid'] = game_id
    df.loc[game_id] = data
    df.to_excel(path, sheet_name="Sheet1", index=False)
    return game_id


def check_in(qq_id, server_name):
    path = get_path(server_name)
    df = pd.read_excel(path, sheet_name="Sheet1")
    i = get_gameid(qq_id, server_name)
    if i is None:
        return "该玩家还未注册！"
    last_sign_in_date = df['LastSignInDate'][i-1]
    now = datetime.datetime.now()
    now_date = str(now.year)+'.'+str(now.month)+'.'+str(now.day)
    if now_date != last_sign_in_date:
        # print(now_date)
        # print(last_sign_in_date)
        df['LastSignInDate'][i-1] = now_date
        df['exp'][i-1] += 20
        df['money'][i-1] += 10
        df.to_excel(path, sheet_name="Sheet1", index=False)
        return "签到成功！经验+20,金币+10"
    else:
        return "您今天已经签过到了！"


def get_rich_list(server_name):
    path = get_path(server_name)
    df = get_df(path, index_col='qqid')
    df = df.sort_values(by='money', ascending=False)
    rich_list_money = df['money'].tolist()
    rich_list_nickname = df['nickname'].tolist()
    num = len(rich_list_money)
    if num > 8:
        num = 8
    rich_list = list(range(num))
    for i in range(num):
        rich_list[i] = str(rich_list_nickname[i])+',' + \
            str(rich_list_money[i])+'金币'
    return rich_list


def get_poor_list(server_name):
    path = get_path(server_name)
    df = get_df(path, index_col='qqid')
    df = df.sort_values(by='money')
    rich_list_money = df['money'].tolist()
    rich_list_nickname = df['nickname'].tolist()
    rich_list = []
    for i in range(len(rich_list_money)):
        if rich_list_money[i] < 0:
            rich_list.append(
                str(rich_list_nickname[i])+','+str(rich_list_money[i])+'金币')
        else:
            break
    return rich_list


def get_wordle_list(server_name, tp):
    path = get_path(server_name)
    if tp == 0:
        df = get_df(path, index_col='qqid')
        df = df.sort_values(by='wordle_win', ascending=False)
        wordle_list_win = df['wordle_win'].tolist()
        wordle_list_nickname = df['nickname'].tolist()
        num = len(wordle_list_win)
        if num > 5:
            num = 5
        wordle_list = list(range(num))
        for i in range(num):
            wordle_list[i] = str(wordle_list_nickname[i]) + \
                ','+str(wordle_list_win[i])+'胜局'
        return wordle_list
    elif tp == 1:
        pass


def twentyfour_points_check(qq_id, answer, server_name, problem, mode, points=24, extra_operater=False):
    answer = answer.replace('×', '*').replace('÷',
                                              '/').replace('（', '(').replace('）', ')')
    answer = answer.replace('J', '11').replace('Q', '12').replace('K', '13').replace(
        'j', '11').replace('q', '12').replace('k', '13').replace('A', '1').replace('a', '1')
    if not extra_operater:
        banned_operator = ['%', '=', '<', '>', ',', '&',
                           '|', "**", '^', ':', '!', '~', '.', '//']
        for i in range(len(banned_operator)):
            if banned_operator[i] in answer:
                return "使用了不允许的运算符！"
        # or 'int' in answer or 'len' in answer  or 'ord' in answer
        if bool(re.search('[a-zA-z]', answer)):
            return "使用了除J,Q,K,A以外的字母！"
    lst_answer = [int(s) for s in re.findall(r'\d+', answer)]
    lst_problem = [int(s) for s in re.findall(r'\d+', problem)]
    if set(lst_answer) != set(lst_problem):
        return "未用全题目中的数或增加了新的数！"
    else:
        try:
            result = eval(answer)
        except SyntaxError:
            return "语法错误！"
        except NameError:
            return "别瞎整"
        if abs(result-points) < 0.00001:
            if mode == 'easy' or mode == 'e':
                adddata = {'exp': 8, 'money': 4}
            elif mode == 'mid' or mode == 'm':
                adddata = {'exp': 10, 'money': 5}
            elif mode == 'hard' or mode == 'h':
                adddata = {'exp': 20, 'money': 10}
            else:
                adddata = {'exp': 0, 'money': 0}
            add_data(adddata, qq_id, server_name)
            return f"回答正确！经验+{adddata['exp']},金币+{adddata['money']}"
        else:
            return "计算错误！"


def twentyfour_hard_problem(num=None):
    # 12道Problem
    Problem = ["1、3、4、6", "1、4、5、6", "1、5、5、5", "2、2、11、11", "2、2、13、13", "3、3、7、7",
               "3、3、8、8", "4、4、7、7", "4、4、10、10", "5、5、7、11", "6、9、9、10", "1、7、13、13"]
    if num is None:
        return Problem[random.randint(0, len(Problem))]
    else:
        return Problem[num]


def give_twentyfour_problem(mode='hard'):
    if mode == 'hard':
        return twentyfour_hard_problem()
    elif mode == 'simple':
        return str(random.randint(1, 13))+'、'+str(random.randint(1, 13))+'、'+str(random.randint(1, 13))+'、'+str(random.randint(1, 13))


def upgrade(qq_id, server_name):
    exp2up = [10, 50, 100, 200, 500, 1000]
    maxlevel = len(exp2up)
    pf = get_player_file(qq_id, server_name)
    if pf is None:
        return "该玩家还未注册！"
    if pf['level'] == maxlevel:
        return "您已升至满级"
    elif exp2up[pf['level']] > pf['exp']:
        return f'升至{pf["level"]+1}级需要{exp2up[pf["level"]]}经验,您当前只有{pf["exp"]}经验'
    else:
        adddata = {'level': 1, 'exp': -exp2up[pf["level"]]}
        add_data(adddata, qq_id, server_name)
        return f'升级成功,当前您为{pf["level"]+1}级{pf["exp"]-exp2up[pf["level"]]}经验'


def add_data(data: dict, qq_id, server_name):
    path = get_path(server_name)
    df = pd.read_excel(path, sheet_name="Sheet1")
    i = get_player_row(qq_id, server_name)
    if i is None:
        return "该玩家还未注册！"
    mesg = ''
    for k in list(data.keys()):
        if data[k] != 0:
            df[k][i] += data[k]
            mesg += f'{k}{data[k]}'
    df.to_excel(path, sheet_name="Sheet1", index=False)
    return f'已发放{mesg}给玩家{df["nickname"][i]}(gameid={i+1})'


def change_data(data: dict, qq_id, server_name):
    path = get_path(server_name)
    df = pd.read_excel(path, sheet_name="Sheet1")
    i = get_player_row(qq_id, server_name)
    if i is None:
        return "该玩家还未注册！"
    mesg = ''
    # if 'qqid' in list(data.keys()):
    #   raise ValueError("不允许修改玩家的qqid")
    for k in list(data.keys()):
        mesg += f'\n{k}:{df[k][i]}->{data[k]}'
        df[k][i] = data[k]
    df.to_excel(path, sheet_name="Sheet1", index=False)
    return f'已更改玩家{df["nickname"][i]}(gameid={i+1})的以下数据：{mesg}'
