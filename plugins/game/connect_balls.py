# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import itertools
import random
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFont


class ConnectBalls:
    cell_h = 70
    cell_w = 70
    line_wid = 3
    BGcolor = (255, 255, 255)
    line_color = (0, 0, 0)
    text_color = 0

    def __init__(self, col=5, row=5, pair_num=5):
        self.col = col
        self.row = row
        self.pair_num = pair_num if 2*pair_num < col*row else 1
        self.board = [[0 for _ in range(self.row)] for __ in range(self.col)]
        self.point_pairs = self.generate_problem()

    def play(self, img_bytes):
        return self.is_connect_state_solution(self.recognize_connection_state_by_bytes(img_bytes))

    def generate_problem(self):
        if (self.col*self.row) % 2:
            x = random.randint(0, self.col-1)
            xy = x, random.choice(range(x % 2, self.row, 2))
        else:
            xy = random.randint(0, self.col-1), random.randint(0, self.row-1)

        board_temp = [[0 for _ in range(self.row)] for __ in range(self.col)]
        board_temp[xy[0]][xy[1]] = 1
        path = []
        self._dfs(xy, board_temp, path)

        while True:
            nodes = list(random.choice(
                list(itertools.combinations(range(1, len(path)-2), self.pair_num-1))))
            ct = 0
            for i in range(self.pair_num-2):
                if nodes[i+1]-nodes[i] == 1:
                    ct = 1
                    break
            if ct == 1:
                continue
            else:
                break
        nodes.append(len(path)-1)
        point_pairs = [((path[0][0], path[0][1]),
                        (path[nodes[0]][0], path[nodes[0]][1]))]
        self.board[path[0][0]][path[0][1]] = 1
        for i in range(len(nodes)-1):
            self.board[path[nodes[i]][0]][path[nodes[i]][1]] = i+1
            self.board[path[nodes[i]+1][0]][path[nodes[i]+1][1]] = i+2
            point_pairs.append(((path[nodes[i]+1][0], path[nodes[i]+1][1]),
                                (path[nodes[i+1]][0], path[nodes[i+1]][1])))
        self.board[path[-1][0]][path[-1][1]] = len(nodes)
        print(self.board)
        print(point_pairs)
        return point_pairs

    def get_a_legal_points_pair(self):
        if (self.col*self.row) % 2 == 1:
            a = random.randint(0, self.col-1)
            b = random.choice(range(a % 2, self.row, 2))
            start = a, b
            a2 = random.randint(0, self.col-1)
            lst = list(range(a % 2, self.row, 2))
            if b in lst:
                lst.remove(b)
            end = a2, random.choice(lst)
        else:
            start = random.randint(
                0, self.col-1), random.randint(0, self.row-1)
            is_odd = sum(start) % 2
            while True:
                end = random.randint(
                    0, self.col-1), random.randint(0, self.row-1)
                if sum(end) != is_odd:
                    break
        return start, end

    def _dfs(self, xy, board_temp, path):
        direction = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while True:
            if self.is_full(board_temp):
                path.append(xy)
                return True
            if direction == []:
                return False
            d = random.choice(direction)
            next_xy = xy[0]+d[0], xy[1]+d[1]
            if (not (0 <= next_xy[0] <= self.col-1 and 0 <= next_xy[1] <= self.row-1)) or \
                    board_temp[next_xy[0]][next_xy[1]] == 1:
                direction.remove(d)
                continue
            board_temp[next_xy[0]][next_xy[1]] = 1
            if not self._dfs(next_xy, board_temp, path):
                direction.remove(d)
                board_temp[next_xy[0]][next_xy[1]] = 0
                continue
            else:
                path.append(xy)
                return True

    @staticmethod
    def is_full(board):
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    return False
        return True

    @staticmethod
    def max_board_num(board):
        """board中的最大数的值"""
        return max([max(column) for column in board])

    @staticmethod
    def min_board_num(board):
        """board中的最大数的值"""
        return min([min(column) for column in board])

    def generate_ini_chain(self):
        """初始时先生成一条‘墙壁’链"""
        ...

    def get_img_PIL(self, player=None):
        image = self._draw_board()
        if player is not None:
            self._draw_player_name(image, player)
        return image

    def get_img_bytes(self, player=None):
        bt = BytesIO()
        self.get_img_PIL(player).save(bt, format='PNG')
        return bt.getvalue()

    def _draw_board(self, draw_text=False):
        img = Image.new('RGB', (self.cell_w*self.col+self.line_wid*(self.col+1), self.cell_w*self.row+self.line_wid*(self.row+1)),
                        color=self.BGcolor)
        self.__draw_split_line(img)
        self.__draw_cell_cover(img)
        if draw_text:
            self.__draw_cell_text(img)
        return img

    def __draw_split_line(self, img):
        draw = ImageDraw.Draw(img)
        for i in range(self.row+1):
            draw.line((0, i * (self.cell_h+self.line_wid)+self.line_wid//2, img.size[0], i * (self.cell_h+self.line_wid)+self.line_wid//2),
                      fill=0, width=self.line_wid)
        for i in range(self.col+1):
            draw.line((i * (self.cell_w+self.line_wid)+self.line_wid//2, 0, i * (self.cell_w + self.line_wid)+self.line_wid//2, img.size[1]),
                      fill=0, width=self.line_wid)

    def __draw_cell_cover(self, img):
        COLOR = [(0, 55, 218), (19, 161, 14), (193, 156, 0), (197, 15, 31),
                 (58, 150, 221), (136, 23, 152), (187, 137, 243)]
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for j in range(0, self.row):
                fill = (
                    255, 255, 255) if self.board[i][j] == 0 else COLOR[self.board[i][j]-1]
                draw.rectangle((i*(self.cell_w+self.line_wid)+self.line_wid, j*(self.cell_h+self.line_wid)+self.line_wid,
                                i*(self.cell_w+self.line_wid)+self.cell_w+self.line_wid-1, j*(self.cell_h+self.line_wid)+self.cell_h+self.line_wid-1),
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

    def is_connect_state_solution(self, connect_state):
        """判断'connect_state'是否构成合法解"""
        if connect_state is None:
            return False
        board_connect = [[0 for _ in range(self.row)]
                         for __ in range(self.col)]
        for p in self.point_pairs:
            point = p[0]
            while True:
                ct = 0
                if point == p[1]:
                    break
                for c in connect_state:
                    if point == c[0]:
                        point = c[1]
                    elif point == c[1]:
                        point = c[0]
                    else:
                        continue
                    connect_state.remove(c)
                    board_connect[c[0][0]][c[0][1]] += 1
                    board_connect[c[1][0]][c[1][1]] += 1
                    ct = 1
                    break
                if ct == 0:
                    return False

        for i in range(self.col):
            for j in range(self.row):
                if board_connect[i][j] > 2 or board_connect[i][j] == 0:
                    return False
                elif board_connect[i][j] == 1:
                    if self.board[i][j] == 0:
                        return False

        return True

    def recognize_connection_state_by_bytes(self, img_bytes, rgb=None):
        return self.recognize_connection_state(Image.open(BytesIO(img_bytes)), rgb)

    @staticmethod
    def manhattan_dist(coord1, coord2):
        return sum([abs(coord1[i]-coord2[i]) for i in range(len(coord1))])

    def recognize_connection_state(self, PIL_img, rgb=None):
        rgb = self.line_color if rgb is None else rgb
        connect_state = []
        if PIL_img.size != (self.cell_w*self.col+self.line_wid*(self.col+1), self.cell_w*self.row+self.line_wid*(self.row+1)):
            return
        img_array = np.array(PIL_img).tolist()

        for j in range(1, self.row):
            for i in range(len(img_array[0])):
                if self.manhattan_dist(img_array[j*(self.cell_h+self.line_wid)+self.line_wid//2][i], rgb) > 150:
                    column = i//(self.cell_w+self.line_wid)
                    connect_state.append(((column, j-1), (column, j)))

        for i in range(1, self.col):
            for j in range(len(img_array)):
                for k in range(self.line_wid):
                    if self.manhattan_dist(img_array[j][i*(self.cell_w+self.line_wid)+self.line_wid//2], rgb) > 150:
                        _row = j//(self.cell_h+self.line_wid)
                        connect_state.append(((i-1, _row), (i, _row)))

        return list(set(connect_state))
