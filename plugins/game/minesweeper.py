# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import random
from enum import Enum
from time import time
from typing import Tuple

from PIL import Image, ImageColor, ImageDraw, ImageFont

COLUMN_NAME = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class GameState(Enum):
    PREPARE = 1
    GAMING = 2
    WIN = 3
    FAIL = 4


class Cell:
    def __init__(self, is_mine: bool, row: int = 0, column: int = 0,
                 is_mined: bool = False, is_marked: bool = False):
        self.is_mine = is_mine
        self.is_mined = is_mined
        self.is_marked = is_marked
        self.row = row
        self.column = column
        self.is_checked = False

    def __str__(self):
        return f"[Cell] is_mine:{self.is_mine} is_marked:{self.is_marked} is_mined:{self.is_mined}"


class MineSweeper:
    def __init__(self, row: int, column: int, mines: int):
        if row > 26 or column > 26:
            raise ValueError("暂不支持这么大的游戏盘")
        if mines >= row * column or mines == 0:
            raise ValueError("非法操作")
        if mines < column - 1 or mines < row - 1:
            raise ValueError("就不能来点难的吗")
        self.row = row
        self.column = column
        self.mines = mines
        self.start_time = time()
        self.actions = 0
        self.font = ImageFont.truetype(
            "statics/fonts/calibri.ttf", 40)
        self.panel = [[Cell(False, row=r, column=c)
                       for c in range(column)] for r in range(row)]
        self.state = GameState.PREPARE

    def __str__(self):
        return f"[MineSweeper] {self.mines} in {self.row}*{self.column}"

    def draw_panel(self) -> Image.Image:
        # start = time()
        img = Image.new(
            "RGB", (80 * self.column, 80 * self.row), (255, 255, 255))
        self.__draw_split_line(img)
        self.__draw_cell_cover(img)
        self.__draw_cell(img)
        # print(f"draw spend {time()-start}ms at {str(self)}")
        return img

    def __draw_split_line(self, img: Image.Image):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.row):
            draw.line((0, i * 80, img.size[0], i * 80),
                      fill=ImageColor.getrgb("black"))
        for i in range(0, self.column):
            draw.line(
                (i * 80, 0, i * 80, img.size[1]), fill=ImageColor.getrgb("black"))

    def __draw_cell_cover(self, img: Image.Image):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.row):
            for j in range(0, self.column):
                cell = self.panel[i][j]
                if self.state == GameState.FAIL and cell.is_mine:
                    draw.rectangle((j * 80 + 1, i * 80 + 1, (j + 1) * 80 - 1, (i + 1) * 80 - 1),
                                   fill=ImageColor.getrgb("red"))
                    continue
                if cell.is_marked:
                    draw.rectangle((j * 80 + 1, i * 80 + 1, (j + 1) * 80 - 1, (i + 1) * 80 - 1),
                                   fill=ImageColor.getrgb("blue"))
                    continue
                if not cell.is_mined:
                    draw.rectangle((j * 80 + 1, i * 80 + 1, (j + 1) * 80 - 1, (i + 1) * 80 - 1),
                                   fill=ImageColor.getrgb("gray"))

    def __draw_cell(self, img: Image.Image):
        draw = ImageDraw.Draw(img)
        for i in range(0, self.row):
            for j in range(0, self.column):
                cell = self.panel[i][j]
                if not cell.is_mined:
                    font_size = self.font.getsize("AA")
                    index = f"{COLUMN_NAME[i]}{COLUMN_NAME[j]}"
                    center = (
                        80 * (j + 1) - (font_size[0] / 2) - 40, 80 * (i + 1) - 40 - (font_size[1] / 2))
                    draw.text(center, index, fill=ImageColor.getrgb(
                        "black"), font=self.font)
                else:
                    count = self.count_around(i, j)
                    if count == 0:
                        continue
                    font_size = self.font.getsize(str(count))
                    center = (
                        80 * (j + 1) - (font_size[0] / 2) - 40, 80 * (i + 1) - 40 - (font_size[1] / 2))
                    draw.text(center, str(count), fill=self.__get_count_text_color(
                        count), font=self.font)

    @staticmethod
    def __get_count_text_color(count):
        if count == 1:
            return ImageColor.getrgb("green")
        if count == 2:
            return ImageColor.getrgb("orange")
        if count == 3:
            return ImageColor.getrgb("red")
        if count == 4:
            return ImageColor.getrgb("darkred")
        return ImageColor.getrgb("black")

    def mine(self, row: int, column: int):
        if not self.__is_valid_location(row, column):
            raise ValueError("非法操作")
        # start = time()
        cell = self.panel[row][column]
        if cell.is_mined:
            raise ValueError("你已经挖过这里了")
        cell.is_mined = True
        if self.state == GameState.PREPARE:
            self.__gen_mine()
        if self.state != GameState.GAMING:
            raise ValueError("游戏已结束")
        self.actions += 1
        if cell.is_mine:
            self.state = GameState.FAIL
            return
        self.__reset_check()
        self.__spread_not_mine(row, column)
        self.__win_check()
        # print(f"mine spend {time()-start}ms at {str(self)}")

    def tag(self, row: int, column: int):
        cell = self.panel[row][column]
        # start = time()
        if cell.is_mined:
            raise ValueError("你不能标记一个你挖开的地方")
        if self.state != GameState.GAMING and self.state != GameState.PREPARE:
            raise ValueError("游戏已结束")
        self.actions += 1
        if cell.is_marked:
            cell.is_marked = False
        else:
            cell.is_marked = True
        # print(f"tag spend {time()-start}ms at {str(self)}")

    def __gen_mine(self):
        count = 0
        while count < self.mines:
            row = random.randint(0, self.row - 1)
            column = random.randint(0, self.column - 1)
            if self.panel[row][column].is_mine or self.panel[row][column].is_mined:
                continue
            self.panel[row][column].is_mine = True
            count += 1
        self.state = GameState.GAMING

    def __spread_not_mine(self, row: int, column):
        if not self.__is_valid_location(row, column):
            return
        cell = self.panel[row][column]
        if cell.is_checked:
            return
        if cell.is_mine:
            return
        cell.is_mined = True
        cell.is_checked = True
        count = self.count_around(row, column)
        if count > 0:
            return
        self.__spread_not_mine(row + 1, column)
        self.__spread_not_mine(row - 1, column)
        self.__spread_not_mine(row, column + 1)
        self.__spread_not_mine(row, column - 1)
        if count == 0:
            self.__spread_not_mine(row + 1, column + 1)
            self.__spread_not_mine(row - 1, column - 1)
            self.__spread_not_mine(row + 1, column - 1)
            self.__spread_not_mine(row - 1, column + 1)

    def __reset_check(self):
        for i in range(0, self.row):
            for j in range(0, self.column):
                self.panel[i][j].is_checked = False

    def __win_check(self):
        mined = 0
        for i in range(0, self.row):
            for j in range(0, self.column):
                if self.panel[i][j].is_mined:
                    mined += 1
        if mined == (self.column * self.row) - self.mines:
            self.state = GameState.WIN

    def count_around(self, row: int, column: int) -> int:
        count = 0
        for r in range(row - 1, row + 2):
            for c in range(column - 1, column + 2):
                if not self.__is_valid_location(r, c):
                    continue
                if self.panel[r][c].is_mine:
                    count += 1
        if self.panel[row][column].is_mine:
            count -= 1
        return count

    @staticmethod
    def parse_input(input_text: str) -> Tuple[int, int]:
        if len(input_text) != 2:
            raise ValueError("非法位置")
        return COLUMN_NAME.index(input_text[0].upper()), COLUMN_NAME.index(input_text[1].upper())

    def __is_valid_location(self, row: int, column: int) -> bool:
        if row > self.row - 1 or column > self.column - 1 or row < 0 or column < 0:
            return False
        return True


if __name__ == '__main__':
    mine = MineSweeper(10, 20, 198)
    mine.draw_panel().show()
    while True:
        try:
            location = MineSweeper.parse_input(input())
            mine.mine(location[0], location[1])
            mine.draw_panel().show()
            print(mine.state)
        except Exception as e:
            print(e)
