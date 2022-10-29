# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import copy
from get_10 import Get10


class AIGet10Train(Get10):
    def __init__(self, col, row):
        super().__init__(col, row)

    def training(self):
        # TODO: 现在没啥用
        for param in range(12, 48):
            param /= 4
            score = self.AI_play_more(2000, param)
            print(param, score)

    def AI_play_more(self, num, param):
        score = 0
        for i in range(num):
            ai = AIGet10Train(5, 5)
            score += ai.AI_play(param)
            del ai
        score /= num
        return score

    def AI_play(self, param):
        while True:
            x, y = self.algorithm(param)
            # if not self.is_legal(x,y):
          #      raise ValueError("错误！！")
            self.score += self.combine(x, y)
            self.drop()
            self.fill_empty()
            if self.is_gameover():
                break
        return self.score

    def evaluate_training(self, board_try, param):
        judge_score = 0
        for j in range(self.row):
            for i in range(self.col):
                if board_try[i][j] == 0:
                    continue
                if not self.is_legal(i, j):
                    judge_score -= 1
        judge_score -= param * self.max_board_num

        return judge_score

    def algorithm(self, param):
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
                    score = self.evaluate_training(self.board, param)
                    if score > mem[2]:
                        mem[0] = i
                        mem[1] = j
                        mem[2] = score
                    self.board = copy.deepcopy(board_copy)

        return mem[0], mem[1]


if __name__ == '__main__':
    ai = AIGet10Train(5, 5)
    ai.training()
