# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

from .chess_basic import ChessWithImg


class JewishChess(ChessWithImg):
    def __init__(self, col=6, row=6, diag=True, zuozi=0, players=None, anti=False,
                 is_col_label=True, is_row_label=True, is_dot=True, show_num=True):
        if col <= 0 or row <= 0:
            col, row = 6, 6
        self.anti = anti
        self.players = ['player1', 'player2'] if (
            players is None or players[0] == players[1]) else players
        ChessWithImg.__init__(self, col, row, zuozi, is_col_label=is_col_label,
                              is_row_label=is_row_label, is_dot=is_dot, show_num=show_num)

        self.diag = diag

    def play(self, input_str, player=None):
        if player is not None:
            try:
                t = self.players.index(player)
            except:
                raise ValueError('玩家不存在！')
            if t != self.turn:
                raise ValueError('还没轮到你下棋！')
        san = self.parse_input(input_str)
        self._push(san)
        self._save_frame()
        self.check_end()
        if self.outcome == -1:
            self.turn ^= 1
        else:
            return self.outcome

    def parse_input(self, input_str):
        """分析输入，返回长度为2或4的list表示下棋位置 """
        k = input_str.replace('(', '').replace(')', '').replace(
            '，', ',').replace('.', ',')
        k = k.split(',')
        if len(k) != 2 and len(k) != 4:
            raise ValueError("输入非法！")
        for i in range(len(k)):
            try:
                num = int(k[i])
            except ValueError:
                raise ValueError('输入非法！')
            if num <= 0 or (num > self.col and i % 2 == 0) or (num > self.row and i % 2 == 1):
                raise ValueError('输入越界！')
            k[i] = num-1
        return k

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

    def _push(self, san):
        if len(san) == 2:
            if self.board[san[0]][san[1]] != -1:
                raise ValueError("当前位置已有棋子！")
            self.board[san[0]][san[1]] = self.turn
            self.num += 1
            self.board_num[san[0]][san[1]] = self.num
        elif len(san) == 4:
            if san[0] == san[2]:
                for i in range(min(san[1], san[3]), max(san[1], san[3])+1):
                    if self.board[san[0]][i] != -1:
                        raise ValueError("当前位置已有棋子！")
                self.num += 1
                for i in range(min(san[1], san[3]), max(san[1], san[3])+1):
                    self.board[san[0]][i] = self.turn
                    self.board_num[san[0]][i] = self.num
            elif san[1] == san[3]:
                for i in range(min(san[0], san[2]), max(san[0], san[2])+1):
                    if self.board[i][san[1]] != -1:
                        raise ValueError("当前位置已有棋子！")
                self.num += 1
                for i in range(min(san[0], san[2]), max(san[0], san[2])+1):
                    self.board[i][san[1]] = self.turn
                    self.board_num[i][san[1]] = self.num

            elif abs(san[2]-san[0]) == abs(san[3]-san[1]):
                if san[2] > san[0]:
                    y = san[1]
                    for i in range(san[0], san[2]+1):
                        if self.board[i][y] != -1:
                            raise ValueError("当前位置已有棋子！")
                        if san[1] < san[3]:
                            y += 1
                        else:
                            y -= 1
                    y = san[1]
                    self.num += 1
                    for i in range(san[0], san[2]+1):
                        self.board[i][y] = self.turn
                        self.board_num[i][y] = self.num
                        if san[1] < san[3]:
                            y += 1
                        else:
                            y -= 1
                else:
                    y = san[3]
                    for i in range(san[2], san[0]+1):
                        if self.board[i][y] != -1:
                            raise ValueError("当前位置已有棋子！")
                        if san[3] < san[1]:
                            y += 1
                        else:
                            y -= 1
                    y = san[3]
                    self.num += 1
                    for i in range(san[2], san[0]+1):
                        self.board[i][y] = self.turn
                        self.board_num[i][y] = self.num
                        if san[3] < san[1]:
                            y += 1
                        else:
                            y -= 1
            else:
                raise ValueError('输入两点需在同一直线或45度斜线上！')

    def check_end(self):
        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] == -1:
                    return
        self.outcome = self.turn ^ self.anti


if __name__ == '__main__':
    path = 'tempgo.png'
    players = [input("请输入玩家1昵称："), input("请输入玩家2昵称：")]
    chs = JewishChess(players=players, path=path)
    chs.image.show()
    while True:
        try:
            input_str = input(f"轮到 {players[chs.turn]} 下棋:")
            if input_str == '悔棋':
                chs.undo()
                chs.image.show()
                continue
            elif input_str == '中止':
                chs.save_gif()
                print("游戏结束！")
                print("棋谱gif已保存！")
                break
            mesg = chs.play(input_str, players[chs.turn])
            chs.image.show()
            if mesg is not None:
                print(f'{players[chs.outcome]} 获得胜利！')
                chs.save_gif()
                print("游戏结束！")
                print("棋谱gif已保存！")
                break
                break
        except Exception as e:
            print(e)
