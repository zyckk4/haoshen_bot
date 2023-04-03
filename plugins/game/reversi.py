# -*- coding: utf-8 -*-
'''
@author: zyckk4  https://github.com/zyckk4
'''
import copy
from .chess_basic import ChessWithImg


class Reversi(ChessWithImg):
    def __init__(self, players: list, col=8, row=8,
                 zuozi=-1, anti=False, show_num=True):
        # the first player in players plays first(plays as black)
        if col <= 0 or row <= 0:
            col, row = 15, 15, 5
        if zuozi == -1:
            zuozi = [[(4, 5), (5, 4)], [(4, 4), (5, 5)]]
        self.players = ['player1', 'player2'] if (
            players is None or players[0] == players[1]) else players
        ChessWithImg.__init__(self, col, row, zuozi, is_col_label=True,
                              is_row_label=True, is_dot=False, show_num=show_num)
        self.last_1_board = copy.deepcopy(self.board)
        self.anti = anti
        self.regret = 0
        self.b_piece, self.w_piece = 2, 2

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
        self._push(x, y)
        self._save_frame()
        if self.check_end():
            self.b_piece, self.w_piece = self.check_win()
            return self.b_piece, self.w_piece
        if not self.is_able2play(not self.turn):
            return -3
           # raise ValueError(f"{self.players[not self.turn]} 无处可走,players[self.turn]继续下棋！")
        self.turn ^= 1

    def _push(self, x, y):
        if x >= self.col or y >= self.row or x < 0 or y < 0:
            raise ValueError('输入超出合法范围！')
        elif self.board[x][y] != -1:
            raise ValueError("当前位置已有棋子！")
        elif not self.can_capture(x, y):
            raise ValueError("必须下在能翻对面子的地方！")
        self.board[x][y] = self.turn
        self.num += 1
        self.board_num[x][y] = self.num
        self.capture(x, y)
        self.regret = 1

    def undo(self):
        if self.regret <= 0:
            if self.num == 0:
                raise ValueError("不允许还没下就悔棋！")
            raise ValueError("不允许连续悔棋！")
        for x in range(self.col):
            for y in range(self.row):
                if self.board_num[x][y] == self.num:
                    self.board_num[x][y] = -1
                    break
            break
        self.num -= 1
        self.board = copy.deepcopy(self.last_1_board)
        self.regret = 0
        self.turn ^= 1
        self._save_frame(True)

    def can_capture_base(self, x, y, v, t):
        # Here x, y startsfrom 0
        # v:direction vector
        if v == (0, 0):
            return False
        if t is None:
            t = self.turn
        x += v[0]
        y += v[1]
        try:
            if self.board[x][y] == t or self.board[x][y] == -1:
                return False
        except IndexError:
            return False
        while x >= 0 and y >= 0 and x < self.col and y < self.row:
            if self.board[x][y] == t:
                return True
            if self.board[x][y] == -1:
                return False
            x += v[0]
            y += v[1]
        return False

    def can_capture(self, x, y, t=None):
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if self.can_capture_base(x, y, (i, j), t):
                    return True
        return False

    def capture_base(self, x, y, v):
        # Here x, y start from 0
        # v: direction vector
        if v == (0, 0):
            return 0
        m = self.board[x][y]
        x += v[0]
        y += v[1]
        try:
            if self.board[x][y] == m or self.board[x][y] == -1:
                return -1
        except IndexError:
            return -2
        ct = 0
        flag = False
        lst = []
        while x >= 0 and y >= 0 and x < self.col and y < self.row:
            if self.board[x][y] == m:
                for k in lst:
                    self.board[k[0]][k[1]] = m
                flag = True
                break
            if self.board[x][y] == -1:
                break
            lst.append((x, y))
            x += v[0]
            y += v[1]
            ct += 1
        if not flag:
            return -3
        else:
            return ct

    def capture(self, x, y):
        # Here x, y start from 0
        ct = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                m = self.capture_base(x, y, (i, j))
                if m > 0:
                    ct += m
        return ct

    def is_able2play(self, t):
        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] == -1 and self.can_capture(x, y, t):
                    return True
        return False

    def check_end(self):
        return False if self.is_able2play(0) | self.is_able2play(1) else True

    def check_win(self):
        piece_num = [0, 0]
        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] != -1:
                    piece_num[self.board[x][y]] += 1
        if piece_num[0] == piece_num[1]:
            self.outcome = 2
        else:
            self.outcome = (piece_num[0] < piece_num[1]) ^ self.anti
        return piece_num[0], piece_num[1]


'''
lst_zuozi=[
    [[(2,6),(3,3),(3,4),(3,5),(3,7),(4,3),(4,4),(5,2),(5,5),(7,5)],
     [(1,4),(1,5),(1,6),(2,5),(3,6),(3,8),(4,5),(4,6),(4,7),(5,4),(5,6),(5,7),(6,3),(6,4),(6,5),(6,6),(6,7),(7,6)]],
    [[(3,6),(4,3),(5,2),(5,3),(6,6),(7,5),(8,6)],
     [(3,5),(4,5),(4,6),(4,7),(4,8),(5,4),(5,5),(5,6),(5,7),(5,8),(6,3),(6,4),(6,5),(7,4)]]
    ]
'''
