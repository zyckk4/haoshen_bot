# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from random import randint
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class ChessBasic():
    def __init__(self, col, row, zuozi):
        self.col = col
        self.row = row
        # 0 represents a black stone.Also 0 means it's black's turn
        self.turn = 0
        self.board = [[-1 for _ in range(self.row)] for __ in range(self.col)]
        self.board_num = [[-1 for _ in range(self.row)]
                          for __ in range(self.col)]
        # self.outcome = 0: first player wins; 1: second player wins; 2: draw
        self.outcome = -1
        self.zuozi = zuozi
        self.zuozi_num = 0
        self.__set_zuozi(zuozi)
        self.num = 0  # the total number of moves

    def __generate_random_play(self, t, num):
        k = 0
        while k < num:
            x = randint(0, self.col-1)
            y = randint(0, self.row-1)
            if self.board[x][y] == -1:
                self.board[x][y] = t
                k += 1
            continue

    def __set_zuozi(self, zuozi):
        if type(zuozi) is int:
            if zuozi <= 0:
                return
            self.zuozi_num = zuozi
            num1 = (zuozi+self.turn)//2
            num0 = zuozi-num1
            self.__generate_random_play(0, num0)
            self.__generate_random_play(1, num1)
            x = zuozi
            self.turn = (self.turn+x) % 2
        elif type(zuozi) is list:
            self.zuozi_num = len(zuozi[0])+len(zuozi[1])
            for k0 in zuozi[0]:
                self.board[k0[0]-1][k0[1]-1] = 0
                self.board_num[k0[0]-1][k0[1]-1] = 0
            for k1 in zuozi[1]:
                self.board[k1[0]-1][k1[1]-1] = 1
                self.board_num[k1[0]-1][k1[1]-1] = 0
            try:
                self.turn = zuozi[2]
            except:
                pass


class ChessWithImg(ChessBasic):
    r = 1
    side_empty_h = 70*r
    side_empty_w = 70*r
    gap_h = 50*r
    gap_w = 50*r
    line_wid = 3*r
    stone_radius = 23*r
    BGcolor = (217, 152, 77)
    line_color = 0
    stone_outline_color = 0
    stone_outline_width = 2

    def __init__(self, col, row, zuozi, is_col_label=True,
                 is_row_label=True, is_dot=True, show_num=True, show_players=None):
        ChessBasic.__init__(self, col, row, zuozi)
        self.w = self.gap_w*(col-1)+self.line_wid*col+2*self.side_empty_w
        self.h = self.gap_h*(row-1)+self.line_wid*row+2*self.side_empty_h
        self.is_col_label = is_col_label
        self.is_row_label = is_row_label
        self.is_dot = is_dot
        self.show_num = show_num
        self.show_players = show_players
        self.frames = []
        self._save_frame()

    def __draw_a_label(self, draw, num, tp):
        size = 36*self.r
        font = ImageFont.truetype("statics/fonts/calibri.ttf", size=size)
        if tp == 'col':
            x = self.side_empty_w-size//4+(self.line_wid+self.gap_w)*(num-1)
            y = self.side_empty_h-size-5
            if num >= 10:
                x -= size//4
            draw.text((x, y), str(num), font=font, fill=0)
        elif tp == 'row':
            x = self.side_empty_w-size//2-10
            y = self.side_empty_h+(self.line_wid+self.gap_w)*(num-1)-size//2+2
            if num >= 10:
                x -= size//2
            draw.text((x, y), str(num), font=font, fill=0)

    def __draw_labels(self, draw):
        if self.is_row_label:
            for i in range(self.row):
                self.__draw_a_label(draw, i+1, 'row')
        if self.is_col_label:
            for i in range(self.col):
                self.__draw_a_label(draw, i+1, 'col')

    def __get_lst_dots(self):
        lst_dots = []
        if self.row == self.col:
            s = self.row
            if s % 2 == 0:
                if s <= 12 and s >= 8:
                    lst_dots = [(3, 3), (3, s-3), (s-3, 3), (s-3, s-3)]
                elif s >= 14:
                    lst_dots = [(4, 4), (4, s-4), (s-4, 4), (s-4, s-4)]
            else:
                if self.row == self.col == 15:
                    lst_dots = [(8, 8), (4, 4), (4, 12), (12, 4), (12, 12)]
                elif self.row == self.col == 19:
                    lst_dots = [(4, 4), (4, 10), (4, 16),
                                (10, 4), (10, 10), (10, 16), (16, 4), (16, 10), (16, 16)]
        return lst_dots

    def __draw_dots(self, draw):
        if not self.is_dot:
            return
        for d in self.__get_lst_dots():
            c = (self.side_empty_w+(d[0]-1)*(self.gap_w+self.line_wid)-self.line_wid//2+1,
                 self.side_empty_h+(d[1]-1)*(self.gap_h+self.line_wid)-self.line_wid//2+1)
            draw.ellipse((c[0]-8, c[1]-8, c[0]+8, c[1]+8), fill=0)

    def __draw_stone(self, draw, d):
        c = (self.side_empty_w+d[0]*(self.gap_w+self.line_wid)-self.line_wid//2+1,
             self.side_empty_h+d[1]*(self.gap_h+self.line_wid)-self.line_wid//2+1)
        color = self.board[d[0]][d[1]]
        if color == 'B' or color == 0:
            fill = 0
        else:
            fill = (255, 255, 255)
        draw.ellipse((c[0]-self.stone_radius, c[1]-self.stone_radius, c[0]+self.stone_radius,
                      c[1]+self.stone_radius), fill=fill, outline=self.stone_outline_color, width=self.stone_outline_width)
        num = self.board_num[d[0]][d[1]]
        if self.show_num and num > 0:
            size = int(self.stone_radius*3/2)
            x = c[0]-size//4
            y = c[1]-size//2+self.line_wid
            if num >= 10 and num <= 99:
                x -= size//4
            elif num >= 100:
                size -= 5*self.r
                x -= size//2
            font = ImageFont.truetype("statics/fonts/calibri.ttf", size=size)
            if color == 'B' or color == 0:
                fill2 = (255, 255, 255)
            else:
                fill2 = 0
            draw.text((x, y), str(num), font=font, fill=fill2)

    @staticmethod
    def text_b(coord, draw, text, font, shadowcolor, fillcolor, bw=1, is_thin=True):
        '''draw text with boarder'''
        x = coord[0]
        y = coord[1]
        if is_thin:
            # thin border
            draw.text((x - bw, y), text, font=font, fill=shadowcolor)
            draw.text((x + bw, y), text, font=font, fill=shadowcolor)
            draw.text((x, y - bw), text, font=font, fill=shadowcolor)
            draw.text((x, y + bw), text, font=font, fill=shadowcolor)
        else:
            # thicker border
            draw.text((x - bw, y - bw), text, font=font, fill=shadowcolor)
            draw.text((x + bw, y - bw), text, font=font, fill=shadowcolor)
            draw.text((x - bw, y + bw), text, font=font, fill=shadowcolor)
            draw.text((x + bw, y + bw), text, font=font, fill=shadowcolor)
        # now draw the text over it
        draw.text((x, y), text, font=font, fill=fillcolor)

    def __draw_players_name(self, draw):
        if self.show_players is None:
            return
        size = 20*self.r
        font = ImageFont.truetype("statics/fonts/msyh.ttc", size=size)
        x = self.w/2-2*size
        y = self.h-self.side_empty_h/2+5
        self.text_b((x, y-size), draw,
                    self.players[0], font, (255, 255, 255), 0)
        self.text_b((x, y+5), draw, self.players[1], font, 0, (255, 255, 255))

    def __draw_init_board(self):
        img = Image.new("RGB", (self.w, self.h), self.BGcolor)
        draw = ImageDraw.Draw(img)
        # draw up-down lines
        for i in range(self.col):
            draw.line([(self.side_empty_w+(self.gap_w+self.line_wid)*i, self.side_empty_h),
                       (self.side_empty_w+(self.gap_w+self.line_wid)*i, self.h-self.side_empty_h-self.line_wid)], fill=self.line_color, width=self.line_wid)
        # draw horizontal lines
        for i in range(self.row):
            draw.line([(self.side_empty_w, self.side_empty_h+(self.gap_h+self.line_wid)*i),
                       (self.w-self.side_empty_w-self.line_wid, self.side_empty_h+(self.gap_h+self.line_wid)*i)], fill=self.line_color, width=self.line_wid)
        self.__draw_dots(draw)
        self.__draw_labels(draw)
        self.__draw_players_name(draw)
        return img

    def get_img_PIL(self):
        image = self.__draw_init_board()
        draw = ImageDraw.Draw(image)
        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] != -1:
                    self.__draw_stone(draw, (x, y))
        return image

    def get_img_bytes(self):
        bt = BytesIO()
        self.get_img_PIL().save(bt, format='PNG')
        return bt.getvalue()

    def _save_frame(self, pop=False):
        if not pop:
            self.frames.append(self.get_img_PIL())
        else:
            self.frames.pop()

    def get_gif(self, ratio=None):
        bt = BytesIO()
        frames = self.frames.copy()
        if ratio is not None:
            if not isinstance(ratio, int):
                raise ValueError('"ratio" must be int or None!')
            for img in frames:
                if ratio > 0:
                    img.resize((self.w*ratio, self.h*ratio))
                else:
                    img.resize((self.w//-ratio, self.h//-ratio))
        frames[0].save(
            bt,
            format="GIF",
            append_images=self.frames[1:],
            save_all=True,
            duration=800,
            loop=0,
        )
        return bt.getvalue()
