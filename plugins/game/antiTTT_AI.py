# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4

从 AntiTTT_AI_prune.cpp 移植，根据需要进行了修改
原作者： https://github.com/ForeverHaibara
"""

import copy


class AntiTTT_AI:
    """用主类继承这个类以实现AI功能

    // record all the scores of the chessboards
    // There are in total 4*4 = 16 steps
    // * When i = m[board] < 0: it means it loses the game at the last but i step
    // * When i = m[board] > 0: it means it wins  the game at the last but i step
    // * IN PARTICULAR, IF THE GAME[i] DRAWS, m[i] = 64
    // * When m[board] == 0: it means it is not yet explored
    """

    def __init__(self):
        self.m = {}

    def board_int(self) -> int:  # 暂时没用
        """压位，将棋盘数组对应为一个正整数
        
        其二进制的前col*row位存黑棋，后col*row位存白棋
        """
        board_int = 0
        for x in range(self.col):
            for y in range(self.row):
                if self.board[x][y] == 0:
                    board_int += 2**(2*self.row*self.col - self.row*x - y - 1)
                elif self.board[x][y] == 1:
                    board_int += 2**(self.row*self.col - self.row*x - y - 1)
        return board_int

    def a_cnt(self, x, y, v):
        # v: direction vector
        s = -1
        while x >= 0 and x < self.col and y >= 0 and y < self.row:
            if self.board[x][y] != self.turn:
                break
            s += 1
            x += v[0]
            y += v[1]
        return s

    def a_check_lose(self, x, y):
        c = self.connect
        if self.a_cnt(x, y, (1, 0))+self.a_cnt(x, y, (-1, 0))+1 >= c \
                or self.a_cnt(x, y, (0, 1))+self.a_cnt(x, y, (0, -1))+1 >= c \
                or self.a_cnt(x, y, (1, 1))+self.a_cnt(x, y, (-1, -1))+1 >= c \
                or self.a_cnt(x, y, (-1, 1))+self.a_cnt(x, y, (1, -1))+1 >= c:
            return True
        return False

    def attempt(self, x, y):
        self.board[x][y] = self.turn
        self.num += 1
        res = self.a_check_lose(x, y)
        self.turn ^= 1
        return res

    def AItry(self, x, y):
        # return a score after playing (x,y)
        # save a original version of the board
        bd = copy.deepcopy(self.board)
        result = self.attempt(x, y)
        bd_str = str(self.board)
        s = 64  # temporary value for m[board], 64 for tie
        if result:
            '''// lose
            // examples:
            // lose when count = 16: score = 16 - 17 = -1 (slight penalty at last step)
            // lose when count = 6:  score = 6 - 17 = -11 (heavy penalty if lose early)'''
            s = self.m[bd_str] = self.num + self.zuozi_num - 17

        if bd_str not in self.m:
            # no record, dfs
            # simulate all possible moves of the opponent
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == -1:
                        t = self.AItry(i, j)
                        s = min(s, -t)
                        '''
                        /* // Thoughts:
                        if (t < 0){
                            // the opponent will lose, nice
                            // examples:
                            // t = -1: the opponent loses at the last step
                            //        => win at the last but 2 step
                            // t = -11: the oppoenet loses early, I happy
                            //        => win at the last but 11 step
                            
                            // opponent delays my winning
                            s = min(s, -t);                       
                        }
                        else if (t > 0){ 
                            // the opponent can win, too bad
                            // as long as I could fail, the score must be negative
                            // examples:
                            // t = 2: opponent win at the last but 2 step
                            //       => I lose at the last but 2 step

                            // opponent speeds up the killing
                            s = min(s, -t);
                        }
                        */
                        // Conclusion: opponent minimizes my s (score)
                        '''
            if s == 64:
                s = 0
            self.m[bd_str] = 64 if s == 0 else s
        else:
            # not tie
            s = 0 if self.m[bd_str] == 64 else self.m[bd_str]

        # restore the move
        self.board = copy.deepcopy(bd)
        self.num -= 1
        self.turn ^= 1
        return s

    def AImove(self):
        s = -100
        choicei, choicej = 0, 0
        if self.num+self.zuozi_num == 0:
            # No chess on the board! (must fail)
            s = -2
        elif self.num+self.zuozi_num == 1:
            # Only one chess on the board!
            # We have found that the opposite corner leads to the success.
            s = 2
            i, j = 0, 0
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] != -1:
                        break
                if j < self.row:
                    break  # b(i,j) == -1
            choicei = 3 if i <= 1 else 0
            choicej = 3 if j <= 1 else 0
        elif self.num == 0 and self.zuozi == [[(2, 4)], [(3, 3)]]:
            choicei, choicej = 0, 0
        else:
            for i in range(self.col):
                for j in range(self.row):
                    if self.board[i][j] == -1:
                        t = self.AItry(i, j)
                        if t >= s:
                            s = t
                            choicei, choicej = i, j

                        # Conclusion: seek to maximize my s (score)
        # print(f"AI Choice={choicei+1},{choicej+1},Score={s},Size={len(self.m)}")
        return choicei, choicej
