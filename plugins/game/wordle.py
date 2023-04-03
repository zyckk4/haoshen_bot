# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import re
from random import randint

from PIL import Image, ImageColor, ImageDraw, ImageFont


class Wordle:
    cell_w = 50
    cell_h = 50
    cell_bd = 3
    gap_w = 8
    gap_h = 8
    left_empty = 20
    right_empty = 20
    up_empty = 20
    down_empty = 20
    BGcolor = (255, 255, 255)

    def __init__(self, total_guess_chance=6, word_len=5, mode=1):
        file = 'statics/wordle.txt' if mode == 1 else 'statics/wordle2.txt'
        with open(file, 'r') as f:
            k = f.read()
        self.lst_words = k.split('\n')
        self.word_len = word_len
        self.word0 = self.lst_words[randint(1, len(self.lst_words)-1)].lower()
        self.guess_num = 0
        self.total_guess_chance = total_guess_chance

        self.w = word_len*self.cell_w + \
            (word_len-1)*self.gap_w+self.left_empty+self.right_empty
        self.h = total_guess_chance*self.cell_h + \
            (total_guess_chance-1)*self.gap_h+self.up_empty+self.down_empty
        self.font = ImageFont.truetype("statics/fonts/timesbd.ttf", 36)
        self.draw_init_board()
        # print(f'wordle new game start:{self.word0}')

    def play(self, input_str):
        if self.guess_num >= self.total_guess_chance:
            raise ValueError("猜词次数已用完！")
        if not (len(input_str) == self.word_len and re.match('[A-Za-z]{%d}' % (self.word_len), input_str)):
            raise ValueError("输入不符合规则！")
        word = input_str.lower()
        if word not in self.lst_words:
            raise ValueError("您输入的不是单词，或该单词未被收录！")
        lst_state = self.get_state(word)
        self.__draw_add(lst_state, word.upper())
        if lst_state == [2 for i in range(self.word_len)]:
            return 1
        self.guess_num += 1
        if self.guess_num == self.total_guess_chance:
            return 0

    def get_state(self, word):
        """返回0代表该字母不在要猜的单词中；1代表该字母在单词中但是不在此位置；2代表字母，位置均正确"""
        lst_state = []
        for i in range(self.word_len):
            if word[i] not in self.word0:
                lst_state.append(0)
            else:
                if word[i] != self.word0[i]:
                    lst_state.append(1)
                else:
                    lst_state.append(2)
        return lst_state

    def draw_init_board(self):
        self.img = Image.new("RGB", (self.w, self.h), self.BGcolor)
        for i in range(self.word_len):
            for j in range(self.total_guess_chance):
                self.__draw_cell_bd((i, j))

    def __draw_add(self, lst_state, word):
        for i in range(self.word_len):
            self.__draw_cell_cover((i, self.guess_num), lst_state[i])
            self.__draw_cell_text((i, self.guess_num), word[i])

    def __draw_cell_bd(self, coord):
        draw = ImageDraw.Draw(self.img)
        draw.rectangle((self.left_empty+coord[0]*(self.cell_w+self.gap_w),
                       self.up_empty+coord[1]*(self.cell_h+self.gap_h),
                       self.left_empty+coord[0] *
                        (self.cell_w+self.gap_w)+self.cell_w,
                       self.up_empty+coord[1]*(self.cell_h+self.gap_h)+self.cell_h),
                       fill=ImageColor.getrgb("gray"))
        draw.rectangle((self.left_empty+coord[0]*(self.cell_w+self.gap_w)+self.cell_bd,
                       self.up_empty+coord[1] *
                        (self.cell_h+self.gap_h)+self.cell_bd,
                       self.left_empty +
                        coord[0]*(self.cell_w+self.gap_w) +
                        self.cell_w-self.cell_bd,
                       self.up_empty+coord[1]*(self.cell_h+self.gap_h)+self.cell_h-self.cell_bd),
                       fill=(255, 255, 255))

    def __draw_cell_cover(self, coord, state_num):
        draw = ImageDraw.Draw(self.img)
        fill = [ImageColor.getrgb("gray"), (196, 184, 98), (132, 164, 113)]
        draw.rectangle((self.left_empty+coord[0]*(self.cell_w+self.gap_w)+self.cell_bd,
                       self.up_empty+coord[1] *
                        (self.cell_h+self.gap_h)+self.cell_bd,
                       self.left_empty +
                        coord[0]*(self.cell_w+self.gap_w) +
                        self.cell_w-self.cell_bd,
                       self.up_empty+coord[1]*(self.cell_h+self.gap_h)+self.cell_h-self.cell_bd),
                       fill=fill[state_num])

    def __draw_cell_text(self, coord, text):
        draw = ImageDraw.Draw(self.img)
        font_size = self.font.getsize(text)
        draw.text((self.left_empty+coord[0]*(self.cell_w+self.gap_w)+(self.cell_w-font_size[0])//2,
                   self.up_empty+coord[1]*(self.cell_h+self.gap_h)+(self.cell_h-font_size[1])//2-1),
                  text, fill=(255, 255, 255), font=self.font)


if __name__ == '__main__':
    wod = Wordle()
    while True:
        print(f'您当前还有{wod.total_guess_chance-wod.guess_num}次猜词机会')
        wod.img.show()
        try:
            mesg = wod.play(input('请猜词:'))
        except ValueError as e:
            print(str(e))
        if mesg is not None:
            break
    wod.img.show()
    if mesg:
        print('恭喜猜对！正确答案是:{wod.word0}')
    else:
        print('很遗憾，猜词次数用光了！正确答案是:{wod.word0}')
