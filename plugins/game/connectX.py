# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from .chess_basic import ChessWithImg


class ConnectX(ChessWithImg):
    def __init__(self, players=None, col=7, row=6, connect=4, zuozi=0):
        if col <= 0 or row <= 0 or connect <= 0:
            col, row, connect = 7, 6, 4
        self.c = connect
        self.players = ['Player 1', 'Player 2'] if players is None else players
        ChessWithImg.__init__(self, col, row, zuozi, is_col_label=True,
                              is_row_label=False, is_dot=True, show_num=True)
        self.stack = [0 for _ in range(self.col)]

    def play(self, x, player=None):
        if self.outcome != -1:
            raise ValueError('游戏已结束！')
        if player is not None and self.players[self.turn] != player:
            raise ValueError("Invalid player's name!")
        try:
            x = int(x) - 1
        except:
            raise ValueError('输入非法！')
        if x < 0 or x >= self.col:
            raise ValueError(f'只能输入1~{self.col}的数字！')
        if self.stack[x] == self.row:
            raise ValueError('这一列已满！')

        self.stack[x] += 1
        self.board[x][-self.stack[x]] = self.turn
        self.num += 1
        self.board_num[x][-self.stack[x]] = self.num
        self._save_frame()
        self.check_end(x, self.row-self.stack[x])
        if self.outcome == -1:
            self.turn ^= 1
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
                    self.stack[x] -= 1
                    self.turn ^= 1
                    self._save_frame(True)
                    return

    def count(self, x, y, v):
        # v: direction vector
        s = -1
        while x >= 0 and x < self.col and y >= 0 and y < self.row:
            if self.board[x][y] != self.turn:
                break
            s += 1
            x += v[0]
            y += v[1]
        return s

    def check_end(self, x, y):
        c = self.c
        if self.count(x, y, (1, 0))+self.count(x, y, (-1, 0))+1 >= c \
                or self.count(x, y, (0, 1))+self.count(x, y, (0, -1))+1 >= c \
                or self.count(x, y, (1, 1))+self.count(x, y, (-1, -1))+1 >= c \
                or self.count(x, y, (-1, 1))+self.count(x, y, (1, -1))+1 >= c:
            self.outcome = self.turn
            return

        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] == -1:
                    return
        self.outcome = 2


if __name__ == '__main__':
    b = ConnectX(players=['zyckk', 'zyckk2'])
    mesg = b.play('4', 'zyckk')
    mesg = b.play('4', 'zyckk2')
    mesg = b.play('4', 'zyckk')
    print(mesg)
    b.image.show()
    b.save_gif()
