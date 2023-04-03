# -*- coding: utf-8 -*-
"""
@author: zyckk4 https://github.com/zyckk4
"""

from random import randint

from PIL import Image, ImageColor, ImageDraw, ImageFont


class Nonogram:
    def __init__(self, col=7, row=7, mine_num=-1, mode=0):
        self.col = col
        self.row = row
        self.mode = mode
        if mine_num == -1:
            mine_num = randint(col*row//2, 2*col*row//3)
        self.mine = mine_num
        self.board = self.get_board()
        self.board_sign = [[0 for _ in range(self.row)]
                           for __ in range(self.col)]
        self.label = self.get_label()

        self.font = ImageFont.truetype("statics/fonts/Deng.ttf", 40)
        self.num = 0  # the total number of moves

    def get_board(self):
        while True:
            ct = 0
            board = [[0 for _ in range(self.row)] for __ in range(self.col)]
            while ct < self.mine:
                col = randint(0, self.col-1)
                row = randint(0, self.row-1)
                if board[col][row] == 0:
                    board[col][row] = 1
                    ct += 1
            if self.is_board_ok(board):
                return board

    def is_board_ok(self, board):
        for i in range(self.col):
            if sum(board[i]) == 0:
                return False
        for i in range(self.row):
            if sum([board[k][i] for k in range(self.col)]) == 0:
                return False
        return True

    def get_label(self):
        label = [[[] for _ in range(self.col)], [[] for __ in range(self.row)]]
        for i in range(self.col):
            flag = False
            ct = 0
            for j in range(self.row):
                if self.board[i][j] == 1:
                    flag = True
                    ct += 1
                elif self.board[i][j] == 0 and flag:
                    label[0][i].append(ct)
                    flag = False
                    ct = 0
            if flag:
                label[0][i].append(ct)
        for j in range(self.row):
            flag = False
            ct = 0
            for i in range(self.col):
                if self.board[i][j] == 1:
                    flag = True
                    ct += 1
                elif self.board[i][j] == 0 and flag:
                    flag = False
                    label[1][j].append(ct)
                    ct = 0
            if flag:
                label[1][j].append(ct)
        print(label)
        return label

    def __tag(self, coord, tp):
        if self.board_sign[coord[0]][coord[1]] == tp:
            return -1
        self.board_sign[coord[0]][coord[1]] = tp
        return 0

    def play(self, input_str):
        coord, tp = self.parse_input(input_str)
        if self.__tag(coord, tp) == -1:
            return -1
        self.num += 1
        if self.is_end():
            return self.num
        return -1

    def __get_sign_num(self):
        ct_mine = 0
        ct_safe = 0
        for i in range(self.col):
            for j in range(self.row):
                if self.board_sign[i][j] == 1:
                    ct_mine += 1
                elif self.board_sign[i][j] == 2:
                    ct_safe += 1
        return ct_mine, ct_safe

    def is_end(self):
        ct_mine, ct_safe = self.__get_sign_num()
        if ct_safe > self.row*self.col-self.mine:
            raise ValueError("当前排除格数已大于应有数量，请修改！")
        elif ct_mine > self.mine:
            raise ValueError("当前标雷数已大于应有数量，请修改！")
        elif ct_mine < self.mine:
            return False
        # check label:
        label = [[[] for _ in range(self.col)], [[] for __ in range(self.row)]]
        for i in range(self.col):
            flag = False
            ct = 0
            for j in range(self.row):
                if self.board_sign[i][j] == 1:
                    flag = True
                    ct += 1
                elif self.board_sign[i][j] != 1 and flag:
                    label[0][i].append(ct)
                    flag = False
                    ct = 0
            if flag:
                label[0][i].append(ct)
        for j in range(self.row):
            flag = False
            ct = 0
            for i in range(self.col):
                if self.board[i][j] == 1:
                    flag = True
                    ct += 1
                elif self.board[i][j] != 1 and flag:
                    flag = False
                    label[1][j].append(ct)
                    ct = 0
            if flag:
                label[1][j].append(ct)
        return label == self.label

    def parse_input(self, input_str):
        input_str = input_str.replace('.', ',').replace(
            '。', ',').replace('(', '').replace(')', '')
        if input_str[-1] == '/':
            input_str = input_str.replace('/', '')
            tp = 2
        elif input_str[-1] == '白':
            input_str = input_str.replace('白', '')
            tp = 0
        elif input_str[-1] == 'b':
            input_str = input_str.replace('b', '')
            tp = 0
        else:
            tp = 1
        x = input_str.split(',', 1)
        try:
            coord = [int(x[0]), int(x[1])]
        except:
            raise ValueError("输入非法！")
        if not (0 <= coord[0] <= self.col-1 and 0 <= coord[1] <= self.row-1):
            raise ValueError("输入超出合法范围！")
        return coord, tp

    def board_img(self):
        img = Image.new(
            "RGB", (112 * self.col, 112 * self.row), (255, 255, 255))
        self.__draw_split_line(img)
        self.__draw_cell_cover(img)
        self.__draw_cell(img)
        self.__draw_label(img)
        return img

    def __draw_split_line(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.row):
            draw.line((0, i * 80, img.size[0], i * 80), fill=0)
        for i in range(0, self.col):
            draw.line((i * 80, 0, i * 80, img.size[1]), fill=0)

    def __draw_cell_cover(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for j in range(0, self.row):
                sign = self.board_sign[i][j]
                if not sign:
                    draw.rectangle((i * 80 + 1, j * 80 + 1, (i + 1) * 80 - 1, (j + 1) * 80 - 1),
                                   fill=ImageColor.getrgb("gray"))

    def __draw_cell(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for j in range(0, self.row):
                sign = self.board_sign[i][j]
                if not sign:
                    index = f"{i},{j}"
                    font_size = self.font.getsize(index)
                    center = (
                        80 * (i + 1) - (font_size[0] / 2) - 40, 80 * (j + 1) - 40 - (font_size[1] / 2))
                    draw.text(center, index, fill=0, font=self.font)
                else:
                    text = '▇' if sign == 1 else '/'
                    font_size = self.font.getsize(text)
                    center = (
                        80 * (i + 1) - (font_size[0] / 2) - 40, 80 * (j + 1) - 40 - (font_size[1] / 2))
                    draw.text(center, text, fill=0, font=self.font)

    def __draw_label(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for t in range(len(self.label[0][i])):
                text = str(self.label[0][i][t])
                font_size = self.font.getsize(text)
                center = (80 * (i + 1) - (font_size[0] / 2) - 40,
                          80 * self.row+60*(t+1) - 40 - (font_size[1] / 2))
                draw.text(center, text, fill=0, font=self.font)
        for i in range(0, self.row):
            for t in range(len(self.label[1][i])):
                text = str(self.label[1][i][t])
                font_size = self.font.getsize(text)
                center = (80 * self.col+60*(t+1) -
                          (font_size[0] / 2) - 40, 80 * (i + 1) - 40 - (font_size[1] / 2))
                draw.text(center, text, fill=0, font=self.font)


if __name__ == '__main__':
    game = Nonogram()
    game.board_img().show()
    while True:
        try:
            mesg = game.play(input())
            game.board_img().show()
        except Exception as e:
            print(e)
        if mesg != -1:
            print(f"游戏结束！总操作数为{mesg}")
            break
