# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class RenjuEliminate:
    '''连珠消消乐'''
    cell_h = 70
    cell_w = 70
    line_wid = 3
    BGcolor = (255, 255, 255)
    line_color = 0
    text_color = 0

    def __init__(self, col, row, connect=5):
        self.col = col
        self.row = row
        self.connect = connect
        self.score = 0
        self.frames = []
        self.board = [[0 for _ in range(self.row)] for __ in range(self.col)]  # 0为空,1-6为颜色
        self.gen_balls(7)

    def play(self, input_str):
        k = input_str.replace('(', '').replace(')', '').replace('，', ',').replace('.', ',')
        k = k.split(',', 3)
        try:
            x1 = int(k[0])-1
            y1 = int(k[1])-1
            x2 = int(k[2])-1
            y2 = int(k[3])-1
        except:
            raise ValueError('输入不合法！')
        if x1 < 0 or x1 > self.col-1 or y1 < 0 or y1 > self.row-1 or \
                x2 < 0 or x2 > self.col-1 or y2 < 0 or y2 > self.row-1:
            raise ValueError('输入超范围！')
        if self.board[x1][y1] == 0:
            raise ValueError('起点不能为空位！')
        if not self.is_moveable(x1, y1, x2, y2):
            raise ValueError('路径被阻挡，不可移动！')
        self.frames = []
        self.board[x2][y2] = self.board[x1][y1]
        self.board[x1][y1] = 0
        cnt,board_temp=self.check_eliminate(x2, y2)
        if cnt != 0:
            self.board = [[(not board_temp[j][i] and self.board[j][i])
                           for i in range(self.row)] for j in range(self.col)]
            self.score += cnt*2
        self.frames.append(self.get_img_PIL())
        if cnt == 0:
            self.gen_balls(3)
        if self.is_full():
            return -1
        else:
            return 0

    def __gen_a_ball(self):
        while True:
            x = random.randint(0, self.col-1)
            y = random.randint(0, self.row-1)
            if self.board[x][y] == 0:
                break
        color = random.randint(1, 6)
        self.board[x][y] = color
        return x, y

    def gen_balls(self, num):
        for k in range(num):
            x, y = self.__gen_a_ball()
            cnt, board_temp = self.check_eliminate(x, y)
            if cnt != 0:
                self.frames.append(self.get_img_PIL())
                self.board = [[(not board_temp[j][i] and self.board[j][i])
                               for i in range(self.row)] for j in range(self.col)]
                self.score += cnt*2
                if k != num-1:
                    self.frames.append(self.get_img_PIL())
            else:
                if self.is_full():
                    return -1
        self.frames.append(self.get_img_PIL())
        return 0
    
    def eliminate(self):
        '''消除并得分'''
        pass
        
    def count_base(self, x, y, v):
        s = -1
        num = self.board[x][y]
        board_temp = [[0 for _ in range(self.row)] for __ in range(self.col)]
        while x >= 0 and x < self.col and y >= 0 and y < self.row:
            if self.board[x][y] != num:
                break
            s += 1
            board_temp[x][y] = 1
            x += v[0]
            y += v[1]

        return s, board_temp

    def count_a_line(self, x, y, v):
        ct1, board_temp1 = self.count_base(x, y, v)
        ct2, board_temp2 = self.count_base(x, y, [-i for i in v])
        cnt = ct1+ct2+1
        board_temp = [[(board_temp1[i][j] or board_temp2[i][j])
                       for i in range(self.row)] for j in range(self.col)]
        return cnt, board_temp

    def check_eliminate(self, x, y):
        total_cnt = 0
        board_temp = [[0 for _ in range(self.row)] for __ in range(self.col)]
        for v in ((1, -1), (1, 0), (1, 1), (0, 1)):
            cnt, board_temp1 = self.count_a_line(x, y, v)
            if cnt >= self.connect:
                board_temp = [[(board_temp[i][j] or board_temp1[i][j])
                               for i in range(self.row)] for j in range(self.col)]
                total_cnt += cnt
        return total_cnt, board_temp

    def is_full(self):
        for i in range(self.col):
            for j in range(self.row):
                if self.board[i][j] == 0:
                    return False
        return True

    def is_moveable(self, x1, y1, x2, y2):
        '''递归找出所有和(x1,y1)处相同且联通的点,从而判断是否可以移动'''
        if x1 == x2 and y1 == y2:
            return False
        elif self.board[x1][y1] == 0 or self.board[x2][y2] != 0:
            return False
        board_temp = [[0 for _ in range(self.row)] for __ in range(self.col)]
        return self.is_moveable_base(x1, y1, x2, y2, board_temp)

    def is_moveable_base(self, x1, y1, x2, y2, board_temp):
        if abs(x1 - x2) + abs(y1 - y2) == 1:
            return True
        board_temp[x1][y1]=1
        if y1 > 0 and self.board[x1][y1-1] == 0 and board_temp[x1][y1-1] != 1 and \
            self.is_moveable_base(x1, y1-1, x2, y2, board_temp):
            return True
        if y1 < self.col-1 and self.board[x1][y1+1] == 0 and board_temp[x1][y1+1] != 1 and \
            self.is_moveable_base(x1, y1+1, x2, y2, board_temp):
            return True
        if x1 > 0 and self.board[x1-1][y1] == 0 and board_temp[x1-1][y1] != 1 and \
            self.is_moveable_base(x1-1, y1, x2, y2, board_temp):
            return True
        if x1 < self.row-1 and self.board[x1+1][y1] == 0 and board_temp[x1+1][y1] != 1 and \
            self.is_moveable_base(x1+1, y1, x2, y2, board_temp):
            return True
        return False

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
        COLOR = [(0, 55, 218), (19, 161, 14), (58, 150, 221), (197, 15, 31),
                 (136, 23, 152), (193, 156, 0)]
        draw = ImageDraw.Draw(img)
        for i in range(0, self.col):
            for j in range(0, self.row):
                fill = (255, 255, 255) if self.board[i][j] == 0 else COLOR[self.board[i][j]-1]
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
    game = RenjuEliminate(9, 9)
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
