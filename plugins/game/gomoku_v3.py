# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from .chess_basic import ChessWithImg
from .katago import KataAnalyse
from .antiTTT_AI import AntiTTT_AI


class Gomoku(ChessWithImg):
    def __init__(self, col=15, row=15, connect=5, zuozi=0, players=None, anti=False,
                 is_col_label=True, is_row_label=True, is_dot=True, show_num=True):
        if col <= 0 or row <= 0 or connect <= 0:
            col, row = 15, 15, 5
        self.anti = anti
        self.players = ['player1', 'player2'] if (
            players is None or players[0] == players[1]) else players
        ChessWithImg.__init__(self, col, row, zuozi, is_col_label=is_col_label,
                              is_row_label=is_row_label, is_dot=is_dot, show_num=show_num)

        self.connect = connect

    def play(self, input_str, player=None):
        if player is not None:
            try:
                t = self.players.index(player)
            except:
                raise ValueError('玩家不存在！')
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
        self._push(x, y)
        self._save_frame()
        self.check_end(x, y)
        if self.outcome == -1:
            self.turn ^= 1
        elif self.outcome == 2:
            return 2
        else:
            return self.outcome

    def undo(self):
        if self.num <= 0:
            raise ValueError("不允许还没下就悔棋！")
        for x in range(self.col):
            for y in range(self.row):
                if self.board_num[x][y] == self.num:
                    self.board_num[x][y] = -1
                    self.board[x][y] = -1
                    self.num -= 1
                    self.turn = (self.turn+1) % 2
                    self._save_frame(True)
                    return

    def _push(self, x, y):
        if x >= self.col or y >= self.row or x < 0 or y < 0:
            raise ValueError('输入超出合法范围！')
        elif self.board[x][y] != -1:
            raise ValueError("当前位置已有棋子！")
        self.board[x][y] = self.turn
        self.num += 1
        self.board_num[x][y] = self.num

    def count(self, x, y, v):
        # v:direction vector
        s = -1
        while x >= 0 and x < self.col and y >= 0 and y < self.row:
            if self.board[x][y] != self.turn:
                break
            s += 1
            x += v[0]
            y += v[1]
        return s

    def check_end(self, x, y):
        c = self.connect
        if self.count(x, y, (1, 0))+self.count(x, y, (-1, 0))+1 >= c \
                or self.count(x, y, (0, 1))+self.count(x, y, (0, -1))+1 >= c \
                or self.count(x, y, (1, 1))+self.count(x, y, (-1, -1))+1 >= c \
                or self.count(x, y, (-1, 1))+self.count(x, y, (1, -1))+1 >= c:
            self.outcome = self.turn ^ self.anti
            return

        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] == -1:
                    return
        self.outcome = 2


class AntiTTT(Gomoku):
    def __init__(self, players):
        Gomoku.__init__(self, 4, 4, 3, zuozi=[[(2, 4)], [(3, 3)]], players=players, anti=True,
                        is_col_label=True, is_row_label=True, is_dot=False, show_num=True)


class AntiTTT_with_AI(AntiTTT, AntiTTT_AI):
    def __init__(self, players):
        AntiTTT.__init__(self, players)
        AntiTTT_AI.__init__(self)

    def AI_play(self):
        x, y = self.AImove()
        self._push(x, y)
        self._save_frame()
        # print(self.board)
        self.check_end(x, y)
        if self.outcome == -1:
            self.turn ^= 1
        elif self.outcome == 2:
            return 2
        else:
            return self.outcome

    def player_undo(self):
        self.undo()
        self.undo()


class Katagomo(Gomoku, KataAnalyse):
    def __init__(self, players, command):
        Gomoku.__init__(self, players=players)
        command = KataAnalyse.__init__(self, command)

    def play_and_analyse(self, input_str, num=500):
        mesg1 = self.play(input_str)
        if mesg1 is not None:
            return mesg1
        self.kata_play(input_str)
        mesg2 = self.analyse(num)
        return mesg2

    # 分析时用
    def play(self, input_str, player):
        mesg = Gomoku.play(self, input_str, player)
        if mesg is not None:
            return mesg
        self.kata_play(input_str)

    def AI_play(self, visit_num=500):
        x, y = self.AImove(visit_num)
        self._push(x, y)
        self._save_frame()
        self.check_end(x, y)
        if self.outcome == -1:
            self.turn ^= 1
        elif self.outcome == 2:
            return 2
        else:
            return self.outcome

    def player_undo(self):
        self.undo()
        self.undo()
        self.kata_undo()
        self.kata_undo()

