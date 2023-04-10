# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import random
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


class Get10:
    cell_h = 70
    cell_w = 70
    line_wid = 3
    BGcolor = (255, 255, 255)
    line_color = 0
    text_color = 0

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.score = 0
        self.board = [[random.randint(1, 3) for _ in range(
            self.row)] for __ in range(self.col)]

        # 储存最近一次操作的三张图片
        self.frame = []

    def play(self, input_str):
        k = input_str.replace('(', '').replace(')', '').replace(
            '，', ',').replace('.', ',')
        k = k.split(',', 1)
        try:
            x = int(k[0])-1
            y = int(k[1])-1
        except ValueError:
            raise ValueError('输入不合法！')
        if x < 0 or x > self.col-1 or y < 0 or y > self.row-1:
            raise ValueError('输入超范围！')
        if not self.is_legal(x, y):
            raise ValueError('此处不可消除')
        self.frame = []
        self.score += self.combine(x, y)
        self.frame.append(self.get_img_PIL())
        self.drop()
        self.frame.append(self.get_img_PIL())
        self.fill_empty()
        self.frame.append(self.get_img_PIL())
        if self.is_gameover():
            return -1
        else:
            return 0

    @property
    def max_board_num(self):
        """board中的最大数的值"""
        return max([max(column) for column in self.board])

    def fill_empty(self):
        """给下落后的空位赋新值"""
        max_board_num = self.max_board_num
        if max_board_num <= 3:
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == 0:
                        self.board[i][j] = random.randint(1, 3)
        elif max_board_num == 4:
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == 0:
                        if random.randint(1, 10) != 1:
                            self.board[i][j] = random.randint(1, 3)
                        else:
                            self.board[i][j] = 4
        elif max_board_num == 5:
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == 0:
                        x = random.randint(1, 20)
                        if 1 <= x <= 15:
                            self.board[i][j] = random.randint(1, 3)
                        elif 16 <= x <= 18:
                            self.board[i][j] = 4
                        else:
                            self.board[i][j] = 5
        elif max_board_num == 6:
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == 0:
                        x = random.randint(1, 20)
                        if 1 <= x <= 16:
                            self.board[i][j] = random.randint(1, 4)
                        elif 17 <= x <= 19:
                            self.board[i][j] = 5
                        else:
                            self.board[i][j] = 6
        else:
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == 0:
                        x = random.randint(1, 20)
                        if 1 <= x <= 16:
                            self.board[i][j] = random.randint(
                                1, max_board_num-3)
                        elif 16 <= x <= 18:
                            self.board[i][j] = max_board_num-2
                        elif x == 19:
                            self.board[i][j] = max_board_num-1
                        else:
                            self.board[i][j] = max_board_num

    def drop(self):
        """消除后的下落操作"""
        while True:
            k = False
            for i in range(self.col):
                for j in range(self.row-1):
                    if self.board[i][j+1] == 0 and self.board[i][j] != 0:
                        self.board[i][j], self.board[i][j +
                                                        1] = self.board[i][j+1], self.board[i][j]
                        k = True
            if not k:
                break

    def find_same(self, x, y):
        board_temp = [[0 for _ in range(self.row)] for __ in range(self.col)]
        return self._find_same_basic(x, y, board_temp)

    def _find_same_basic(self, x, y, board_temp):
        board = self.board
        board_temp[x][y] = 2
        if (y > 0 and board[x][y] == board[x][y - 1] and board_temp[x][y - 1] != 2):
            self._find_same_basic(x, y - 1, board_temp)
        if (y < self.row - 1 and board[x][y] == board[x][y + 1] and board_temp[x][y + 1] != 2):
            self._find_same_basic(x, y + 1, board_temp)
        if (x > 0 and board[x][y] == board[x - 1][y] and board_temp[x - 1][y] != 2):
            self._find_same_basic(x - 1, y, board_temp)
        if (x < self.col - 1 and board[x][y] == board[x + 1][y] and board_temp[x + 1][y] != 2):
            self._find_same_basic(x + 1, y, board_temp)

        return board_temp

    def combine(self, x, y):
        board_temp = self.find_same(x, y)
        cnt = 0
        num = self.board[x][y]
        for i in range(self.col):
            for j in range(self.row):
                if board_temp[i][j] == 2:
                    self.board[i][j] = 0
                    cnt += 1
        self.board[x][y] = num+1
        score = 3*cnt*num
        return score

    def is_legal(self, i, j):
        """判断i列j行是否可选中以消除"""
        return ((i > 0 and self.board[i][j] == self.board[i-1][j]) or
                (i < self.col - 1 and self.board[i][j] == self.board[i+1][j]) or
                (j > 0 and self.board[i][j] == self.board[i][j-1]) or
                (j < self.row - 1 and self.board[i][j] == self.board[i][j+1]))

    def is_gameover(self):
        """判断是否无可消去项"""
        for i in range(self.col):
            for j in range(self.row):
                if self.is_legal(i, j):
                    return False
        return True

    def get_img_PIL(self, player=None):
        image = self._draw_board()
        if player is not None:
            self._draw_player_name(image, player)
        return image

    def get_img_bytes(self, player=None):
        bt = BytesIO()
        self.get_img_PIL(player).save(bt, format='PNG')
        return bt.getvalue()

    def _draw_board(self):
        img = Image.new('RGB', (self.cell_w*self.col+self.line_wid*(self.col+1), self.cell_w*self.row+self.line_wid*(self.row+1)),
                        color=self.BGcolor)
        self.__draw_split_line(img)
        self.__draw_cell_cover(img)
        self.__draw_cell_text(img)
        return img

    def _draw_player_name(self, image, player):
        ...

    def __draw_split_line(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(self.row+1):
            draw.line((0, i * (self.cell_h+self.line_wid)+self.line_wid//2, img.size[0], i * (self.cell_h+self.line_wid)+self.line_wid//2),
                      fill=0, width=self.line_wid)
        for i in range(self.col+1):
            draw.line((i * (self.cell_w+self.line_wid)+self.line_wid//2, 0, i * (self.cell_w + self.line_wid)+self.line_wid//2, img.size[1]),
                      fill=0, width=self.line_wid)

    def __draw_cell_cover(self, img):
        COLOR = [(0, 55, 218), (19, 161, 14), (58, 150, 221), (197, 15, 31),
                 (136, 23, 152), (193, 156, 0), (97, 214, 214), (231, 72, 86)]
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for j in range(0, self.row):
                fill = (255, 255, 255) if self.board[i][j] == 0 else COLOR[(
                    self.board[i][j]-1) % len(COLOR)]
                draw.rectangle((i*(self.cell_w+self.line_wid)+self.line_wid, j*(self.cell_h+self.line_wid)+self.line_wid,
                                i*(self.cell_w+self.line_wid)+self.cell_w+self.line_wid, j*(self.cell_h+self.line_wid)+self.cell_h+self.line_wid),
                               fill=fill, width=0)

    def __draw_cell_text(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for j in range(0, self.row):
                num = self.board[i][j]
                if num == 0:
                    continue
                font = ImageFont.truetype('statics/fonts/calibri.ttf', 40)
                font_size = font.getsize(str(num))
                center = ((self.cell_w+self.line_wid) * (i + 1) - (
                    font_size[0] // 2) - 35, (self.cell_h+self.line_wid) * (j + 1) - 35 - (font_size[1] // 2))
                draw.text(center, str(num), fill=self.text_color, font=font)


if __name__ == '__main__':
    game = Get10(7, 7)
    game.get_img_PIL().show()
    while True:
        input_str = input('请输入:')
        try:
            ret = game.play(input_str)
        except Exception as e:
            print(str(e))
            continue
        if ret == -1:
            print(f'游戏结束，共{game.score}分')
        else:
            print(f'当前{game.score}分')
            game.get_img_PIL().show()
