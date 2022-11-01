# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from .get_10 import Get10
import copy


class AIGet10(Get10):
    def __init__(self, col, row):
        super().__init__(col, row)

    def evaluate(self, board_try):
        judge_score = 0
        for j in range(self.row):
            for i in range(self.col):
                if board_try[i][j] == 0:
                    continue
                if not self.is_legal(i, j):
                    judge_score -= 1
        if self.row + self.col > 11:
            judge_score -= 2 * self.max_board_num*self.max_board_num
        else:
            judge_score -= 5 * self.max_board_num

        return judge_score

    def evaluate_filled(self, board_try):
        """模拟填完数组中空位后算分"""
        judge_score = 0
        for j in range(self.row):
            for i in range(self.col):
                if not self.is_legal(i, j):
                    judge_score -= 7*self.row*self.col

        judge_score -= self.row * self.col * 30 * self.max_board_num

        return judge_score

    def algorithm(self):
        LOSE = -2147483647
        ct = False
        mem = [0, 0, LOSE]
        for i in range(self.col):
            for j in range(self.row):
                if self.is_legal(i, j):
                    mem[0] = i
                    mem[1] = j
                    ct = True
                    break
                if ct:
                    break

        board_copy = copy.deepcopy(self.board)
        for i in range(self.col):
            for j in range(self.row):
                if self.is_legal(i, j):
                    self.combine(i, j)
                    self.drop()
                    score = self.evaluate(self.board)
                    if score > mem[2]:
                        mem[0] = i
                        mem[1] = j
                        mem[2] = score
                    self.board = copy.deepcopy(board_copy)

        return mem[0], mem[1]

    def algorithm_filled_depth2(self):
        LOSE = -2147483647
        ct = False
        max_move = [0, 0, 0]
        imi_time1, imi_time2 = 3, 2
        mem = [[-1 for i in range(imi_time1)], [-1 for i in range(imi_time1)],
               [LOSE for i in range(imi_time1)]]
        count = [[0 for _ in range(self.row)] for __ in range(self.col)]

        for i in range(self.col):
            for j in range(self.row):
                if self.is_legal(i, j):
                    max_move[0] = i
                    max_move[1] = j
                    ct = True
                    break
                if ct:
                    break

        board_copy1 = copy.deepcopy(self.board)
        for i in range(self.col):
            for j in range(self.row):
                if self.is_legal(i, j):
                    self.combine(i, j)
                    self.drop()
                    board_copy2 = copy.deepcopy(self.board)
                    for ct in range(imi_time1):
                        self.fill_empty()
                        board_copy3 = copy.deepcopy(self.board)
                        average_score = [[LOSE for _ in range(
                            self.row)] for __ in range(self.col)]
                        for k in range(self.col):
                            for m in range(self.row):
                                if self.is_legal(k, m):
                                    self.combine(k, m)
                                    self.drop()
                                    if self.row+self.col > 12:
                                        board_copy4 = copy.deepcopy(self.board)
                                        temp_score = 0
                                        for __ in range(imi_time2):
                                            self.fill_empty()
                                            judge_score = self.evaluate_filled(
                                                self.board)
                                            temp_score += judge_score
                                            self.board = copy.deepcopy(
                                                board_copy4)
                                        if temp_score > average_score[i][j]:
                                            average_score[i][j] = temp_score
                                    else:
                                        judge_score = self.evaluate(self.board)
                                        if judge_score > average_score[i][j]:
                                            average_score[i][j] = judge_score

                                    self.board = copy.deepcopy(board_copy3)

                        if average_score[i][j] > mem[2][ct]:
                            mem[0][ct] = i
                            mem[1][ct] = j
                            mem[2][ct] = average_score[i][j]

                        self.board = copy.deepcopy(board_copy2)
                    self.board = copy.deepcopy(board_copy1)

        for ct in range(imi_time1):
            if mem[0][ct] == -1:
                continue
            count[mem[0][ct]][mem[1][ct]] += 1
        for i in range(self.col):
            for j in range(self.row):
                if count[i][j] > max_move[2]:
                    max_move[0] = i
                    max_move[1] = j
                    max_move[2] = count[i][j]
        return max_move[0], max_move[1]

    def quick_AI_game(self):
        while True:
            x, y = self.algorithm()
            #x, y = self.algorithm_filled_depth2()
            # print(x,y)
            if not self.is_legal(x, y):
                raise ValueError("错误！！")
            self.score += self.combine(x, y)
            self.drop()
            self.fill_empty()
            if self.is_gameover():
                # print(f'{self.score}分')
                break
        return self.score

    def quick_AI_game_gif_bytes(self):
        frame = []
        frame.append(self.get_img_PIL())
        while True:
            x, y = self.algorithm()
            #x, y = self.algorithm_filled_depth2()
            # print(x,y)
            self.score += self.combine(x, y)
            frame.append(self.get_img_PIL())
            self.drop()
            frame.append(self.get_img_PIL())
            self.fill_empty()
            frame.append(self.get_img_PIL())
            if self.is_gameover():
                # print(f'{self.score}分')
                break
        from io import BytesIO
        bt = BytesIO()
        frame[0].save(
            bt,
            format="GIF",
            append_images=frame[1:],
            save_all=True,
            duration=500,
            loop=0,
        )
        return bt.getvalue(), self.score


if __name__ == '__main__':
    # 修改第一行的导入以使用
    total_score = 0
    max_score = 0
    num = 100
    import time
    import random
    start_time = time.time()
    for i in range(num):
       # r=random.randint(5,8)
       # c=random.randint(5,10)
        r, c = 5, 5
        ai = AIGet10(c, r)
        score = ai.quick_AI_game()
        print(f'第{i+1}局{r}行{c}列{score}分')
        # score/=r*c
        if score > max_score:
            max_score = score
        total_score += score
        del ai
    print(f'本轮{num}局',
          # f'加权总分为{total_score}',
          f'平均分为{total_score/num}',
          f'最高分为{max_score}',
          f'总用时{time.time()-start_time}',
          sep='\n')
