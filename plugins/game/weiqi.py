# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import copy
from .chess_basic import ChessWithImg
from .katago import KataAnalyse


class Go(ChessWithImg):
    def __init__(self, col=19, row=19, zuozi=0, players=None,
                 is_col_label=True, is_row_label=True, is_dot=True, show_num=True):
        # 拷贝三份棋盘“快照”，悔棋和判断“打劫”时需要作参考
        self.players = ['player1', 'player2'] if (
            players is None or players[0] == players[1]) else players
        ChessWithImg.__init__(self, col, row, zuozi, is_col_label=is_col_label,
                              is_row_label=is_row_label, is_dot=is_dot, show_num=show_num)
        self.last_3_positions = copy.deepcopy(self.board)
        self.last_2_positions = copy.deepcopy(self.board)
        self.last_1_positions = copy.deepcopy(self.board)
        self.regret = 0

    def play(self, input_str, player=None):
        if player is not None:
            try:
                t = self.players.index(player)
            except:
                raise KeyError('玩家不存在！')
            if t != self.turn:
                raise ValueError('还没轮到你下棋！')
        k = input_str.replace('(', '').replace(')', '').replace(
            '，', ',').replace('.', ',')
        k = k.split(',', 1)
        try:
            x = int(k[0])-1
            y = int(k[1])-1
        except ValueError:
            raise ValueError('输入不合法！')
        if x >= self.col or y >= self.row or x < 0 or y < 0:
            raise ValueError('输入超出合法范围！')
        self.__push(x, y)
        self._save_frame()
        self.turn ^= 1

    # 放弃一手
    def pass_(self):
        # 拷贝棋盘状态，记录前三次棋局
        self.last_3_positions = copy.deepcopy(self.last_2_positions)
        self.last_2_positions = copy.deepcopy(self.last_1_positions)
        self.last_1_positions = copy.deepcopy(self.board)
        # 轮到下一玩家
        self.turn ^= 1

    # 悔棋函数
    def undo(self):
        if self.regret == 0:
            if self.num == 0:
                raise ValueError("不允许还没下就悔棋！")
            raise ValueError("不允许连续悔棋！")
        lst_b = []
        lst_w = []
        for x in range(self.col):
            for y in range(self.row):
                self.board[x][y] = -1
                if self.board_num[x][y] == self.num:
                    self.board_num[x][y] = -1
        self.num -= 1
        for x in range(self.col):
            for y in range(self.row):
                if self.last_2_positions[x][y] == 0:
                    lst_b += [[x, y]]
                elif self.last_2_positions[x][y] == 1:
                    lst_w += [[x, y]]
        self.__recover(lst_b, 0)
        self.__recover(lst_w, 1)
        self.last_1_positions = copy.deepcopy(self.last_2_positions)
        self.last_2_positions = copy.deepcopy(self.last_3_positions)
        self.regret = 0
        self.turn ^= 1
        self._save_frame(True)

    def __push(self, x, y):
        if self.board[x][y] != -1:
            raise ValueError("当前位置已有棋子！")
        # 位置未被占据，则尝试占据，获得占据后能杀死的棋子列表
        self.board[x][y] = self.turn
        deadlist = self.get_deadlist(x, y)
        self.__kill(deadlist)
        # 判断是否重复棋局
        if not self.last_2_positions == self.board:
            # 判断是否属于有气和杀死对方其中之一
            if len(deadlist) > 0 or self.if_dead([[x, y]], self.turn, [x, y]) == False:
                # 当不重复棋局，且属于有气和杀死对方其中之一时，落下棋子有效
                self.regret = 1
                self.num += 1
                self.board_num[x][y] = self.num
                self.last_3_positions = copy.deepcopy(self.last_2_positions)
                self.last_2_positions = copy.deepcopy(self.last_1_positions)
                self.last_1_positions = copy.deepcopy(self.board)
            else:
                # 不属于杀死对方或有气，判断为无气
                self.board[x][y] = -1
                raise ValueError("不允许棋自杀")
        else:
            # 重复棋局，警告打劫
            self.board[x][y] = -1
            self.__recover(deadlist, not self.turn)
            raise ValueError("打劫！请找劫财后再提劫")

    def if_dead(self, deadList, yourChessman, coord):
        '''
        判断棋子（种类为yourChessman，位置为coord）是否无气（死亡），有气则返回False，无气则返回无气棋子的列表
        本函数是游戏规则的关键，初始deadlist只包含了自己的位置，每次执行时，函数尝试寻找coord周围有没有空的位置，有则结束，返回False代表有气；
        若找不到，则找自己四周的同类（不在deadlist中的）是否有气，即调用本函数，无气，则把该同类加入到deadlist，然后找下一个邻居，只要有一个有气，返回False代表有气；
        若四周没有一个有气的同类，返回deadlist,至此结束递归
        '''
        for i in (-1, 1):
            if [coord[0]+i, coord[1]] not in deadList and 0 <= coord[0]+i < self.col:
                if self.board[coord[0]+i][coord[1]] == -1:
                    return False
            if [coord[0], coord[1]+i] not in deadList and 0 <= coord[1]+i < self.row:
                if self.board[coord[0]][coord[1]+i] == -1:
                    return False
        for i in (-1, 1):
            if [coord[0]+i, coord[1]] not in deadList and 0 <= coord[0]+i < self.col and \
                    self.board[coord[0]+i][coord[1]] == yourChessman:
                midvar = self.if_dead(
                    deadList+[[coord[0]+i, coord[1]]], yourChessman, [coord[0]+i, coord[1]])
                if not midvar:
                    return False
                else:
                    deadList += copy.deepcopy(midvar)
            if [coord[0], coord[1]+i] not in deadList and 0 <= coord[1]+i < self.row and \
                    self.board[coord[0]][coord[1]+i] == yourChessman:
                midvar = self.if_dead(
                    deadList+[[coord[0], coord[1]+i]], yourChessman, [coord[0], coord[1]+i])
                if not midvar:
                    return False
                else:
                    deadList += copy.deepcopy(midvar)
        return deadList

    def get_deadlist(self, x, y):
        '''落子后，依次判断四周是否有棋子被杀死，并返回死棋位置列表'''
        deadlist = []
        for i in (-1, 1):
            if 0 <= y+i < self.row and self.board[x][y+i] == (not self.turn) and ([x, y+i] not in deadlist):
                killList = self.if_dead([[x, y+i]], not self.turn, [x, y+i])
                if killList:
                    deadlist += copy.deepcopy(killList)
            if 0 <= x+i < self.col and self.board[x+i][y] == (not self.turn) and ([x+i, y] not in deadlist):
                killList = self.if_dead([[x+i, y]], not self.turn, [x+i, y])
                if killList:
                    deadlist += copy.deepcopy(killList)
        return deadlist

    def __recover(self, lst_recover, b_or_w):
        '''恢复位置列表lst_recover为b_or_w指定的棋子'''
        for k in lst_recover:
            self.board[k[0]][k[1]] = b_or_w

    def __kill(self, lst_kill):
        ''' 杀死位置列表lst_kill中的棋子'''
        for k in lst_kill:
            self.board[k[0]][k[1]] = -1


class KataGo(Go, KataAnalyse):
    def __init__(self, command):
        Go.__init__(self)
        KataAnalyse.__init__(self, command)

    def play_and_analyse(self, input_str, num=300):
        self.play(input_str)
        self.kata_play(input_str)
        mesg = self.analyse(num)
        return mesg


if __name__ == '__main__':
    players = [input("请输入玩家1昵称："), input("请输入玩家2昵称：")]
    path = 'tempgo.png'
    go = Go(players=players, path=path)
    go.image.show()
    while True:
        try:
            input_str = input(f"轮到 {players[go.turn]} 下棋:")
            if input_str == '悔棋':
                go.undo()
                go.image.show()
                continue
            elif input_str == '中止':
                go.save_gif()
                print("游戏结束！")
                print("棋谱gif已保存！")
                break
            mesg = go.play(input_str, players[go.turn])
            go.image.show()
            if mesg is not None:
                print(mesg[0])
                break
        except Exception as e:
            print(e)
