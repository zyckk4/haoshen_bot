# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from subprocess import Popen, PIPE


def trans_alp(alp):
    return str(ord(alp)-ord('A')+1) if alp < 'I' else str(ord(alp)-ord('A'))


def trans_num(numstr):
    return chr(64+int(numstr)) if int(numstr) < 9 else chr(65+int(numstr))


class KataAnalyse:
    # TODO: linux有问题
    def __init__(self, command):
        self.proc = Popen(args=command, encoding='utf-8',
                          stdin=PIPE, stdout=PIPE, stderr=PIPE)
        # self.proc.stdin.write('rectangular_boardsize 7 6\n')
        # self.proc.stdin.flush()
        # for i in range(2):
        #   self.proc.stdout.readline()
        print('katago已启动')

    def AImove(self, visit_num):
        self.proc.stdin.write(f'kata-analyze {visit_num}\n')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        out = self.proc.stdout.readline()
        # print(out)
        self.proc.stdin.write('stop\n')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        self.proc.stdout.readline()
        self.proc.stdout.readline()
        info = out.split('info move ')
        self.proc.stdin.write(f'play W {info[1][:3]}\n')
        print(f'W {info[1][:3]}')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        self.proc.stdout.readline()
        x, y = int(trans_alp(info[1][0])), int(info[1][1:3])
        return x-1, y-1

    def analyse(self, visit_num):
        self.proc.stdin.write(f'kata-analyze {visit_num}\n')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        out = self.proc.stdout.readline()

        self.proc.stdin.write('stop\n')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        self.proc.stdout.readline()
        self.proc.stdout.readline()
        mesg = self.parse_output(out, visit_num)
        return mesg

    def parse_input(self, input_str):
        input_str = input_str.replace('(', '').replace(
            ')', '').replace('，', ',').replace('.', ',')
        numstr = input_str.split(',')
        turn = ['W ', 'B ']  # 这里反过来，因为self.turn已经改了
        try:
            return turn[self.turn]+trans_num(numstr[0])+numstr[1]
        except AttributeError:
            return turn[int(numstr[2])]+trans_num(numstr[0])+numstr[1]

    def parse_output(self, out, visit_num):
        info = out.split('info move ')
        del info[0]
        for i in range(len(info)):
            info[i] = info[i].split(' ')
            info[i][0] = "({})".format(info[i][0].replace(
                info[i][0][0], trans_alp(info[i][0][0])+',', 1))
        # print(info)
        num = len(info) if len(info) < 10 else 10
        mesg = f'共计算{visit_num}visits'
        for i in range(num):
            mesg += f"\n{i+1}选：{info[i][0]},{info[i][2]}po,winrate={info[i][6]},scoreMean={info[i][4]}"
        return mesg

    def kata_play(self, input_str):
        san = self.parse_input(input_str)
        print(san)
        self.proc.stdin.write(f'play {san}\n')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        self.proc.stdout.readline()

    def kata_undo(self):
        self.proc.stdin.write('undo\n')
        self.proc.stdin.flush()
        self.proc.stdout.readline()
        self.proc.stdout.readline()

    def __del__(self):
        self.proc.kill()
        print('katago已关闭')


if __name__ == '__main__':
    # reversi_analyse(10000)
    kata = KataAnalyse()
    print(kata.analyse(100))
    kata.kata_play('16,16,1')
    print(kata.analyse(100))
    kata.kata_play('4,3,0')
    print(kata.analyse(100))
