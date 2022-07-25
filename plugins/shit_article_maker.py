# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
申论生成器代码来自 https://github.com/Uahh/Slscq
"""
from utils.utils import Listen,send
import random
import json

@Listen.all_mesg()
async def shit_article_maker(event):
    if str(event.message_chain).startswith('/屁文'):
        theme=str(event.message_chain).replace('/屁文','',1).strip()
        if len(theme)>20:
            await send(event,"标题太长了！",True)
            return
        a=BullshitArticle('statics/bullshit_article_data.json')
        article=a.make_bullshit_article(theme)
        article=theme+'\n'+article
        await send(event,article)
        
    elif str(event.message_chain).startswith('/申论'):
        theme=str(event.message_chain).replace('/申论','',1).strip()
        if len(theme)>20:
            await send(event,"主题太长了！",True)
            return
        a=Slscq('statics/shenlun_data.json')
        article=a.gen_text(theme)
        await send(event,article)
      
class BullshitArticle:
    REPEAT = 2

    def __init__(self, path):
        self.load_source(path)
        self.next_rubbish = self.shuffle_rubbish(self.rubbish)
        self.next_famous_saying = self.shuffle_rubbish(self.famous_sayings)

    def load_source(self, path):
        with open(path, mode='r', encoding="utf-8") as f:
            data = json.loads(f.read())

        self.famous_sayings = data["famous"]  # a 代表前面垫话，b代表后面垫话
        self.rubbish_before = data["before"]  # 在名人名言前面弄点废话
        self.rubbish_after = data['after']  # 在名人名言后面弄点废话
        self.rubbish = data['bosh']  # 代表文章主要废话来源

    def shuffle_rubbish(self, rubbish: list):
        rubbish_pool = rubbish * self.REPEAT
        while True:
            random.shuffle(rubbish_pool)
            for i in rubbish_pool:
                yield i

    def add_famous_sayings(self):
        return next(self.next_famous_saying)\
    .replace("a", random.choice(self.rubbish_before)).replace("b", random.choice(self.rubbish_after))

    def make_bullshit_article(self,theme,length=500):
        tmp = ''
        while (len(tmp) < length):
            branch = random.randint(0, 100)
            if branch < 5:
                tmp += ". \r\n    "  # 另起一段
            elif branch < 20:
                tmp += self.add_famous_sayings()
            else:
                tmp += next(self.next_rubbish)
        article = tmp.replace("x", theme)
        return article

class Slscq:
    def __init__(self, json_path):
        self.data = json.load(open(json_path, 'r', encoding='utf-8'))

    def get_random_element(self, element_type: str) -> str:
        total = len(self.data[element_type]) - 1
        return self.data[element_type][random.randint(0, total)]

    def get_title(self) -> str: return self.get_random_element('title')
    def get_noun(self) -> str: return self.get_random_element('noun')
    def get_verb(self) -> str: return self.get_random_element('verb')
    def get_adverb(self, adverb_type: int) -> str: return self.get_random_element('adverb_1' if (adverb_type == 1) else 'adverb_2')
    def get_phrase(self) -> str: return self.get_random_element('phrase')
    def get_sentence(self) -> str: return self.get_random_element('sentence')
    def get_parallel_sentence(self) -> str: return self.get_random_element('parallel_sentence')
    def get_beginning(self) -> str: return self.get_random_element('beginning')
    def get_body(self) -> str: return self.get_random_element('body')
    def get_ending(self) -> str: return self.get_random_element('ending')

    def replace_xx(self, input_str: str,them: str) -> str:
        return input_str.replace('xx', them)

    def replace_vn(self, input_str: str) -> str:
        while input_str.find('vn') != -1:
            vn = '，'.join([self.get_verb() + self.get_noun() for i in range(random.randint(1, 4))])
            input_str = input_str.replace('vn', vn,1)
        return input_str

    def replace_v(self, input_str: str) -> str:
        while input_str.find('v') != -1:
            input_str = input_str.replace('v', self.get_verb(),1)
        return input_str

    def replace_n(self, input_str: str) -> str:
        while input_str.find('n') != -1:
            input_str = input_str.replace('n', self.get_noun(),1)
        return input_str

    def replace_ss(self, input_str: str) -> str:
        while input_str.find('ss') != -1:
            input_str = input_str.replace('ss', self.get_sentence(),1)
        return input_str

    def replace_sp(self, input_str: str) -> str:
        while input_str.find('sp') != -1:
            input_str = input_str.replace('sp', self.get_parallel_sentence(),1)
        return input_str

    def replace_p(self, input_str: str) -> str:
        while input_str.find('p') != -1:
            input_str = input_str.replace('p', self.get_phrase(),1)
        return input_str

    def replace_all(self, input_str: str, them: str) -> str:
        input_str = self.replace_vn(input_str)
        input_str = self.replace_v(input_str)
        input_str = self.replace_n(input_str)
        input_str = self.replace_ss(input_str)
        input_str = self.replace_sp(input_str)
        input_str = self.replace_p(input_str)
        input_str = self.replace_xx(input_str, them)
        return input_str

    def gen(self, them: str = '年轻人买房', essay_num: int = 500) -> dict:
        end_num = begin_num = essay_num * 0.15
        body_num = essay_num * 0.7

        title = self.replace_all(self.get_title(), them)
        begin = ''
        body = ''
        end = ''

        while len(begin) < begin_num: begin += self.replace_all(self.get_beginning(), them)
        while len(body) < body_num: body += self.replace_all(self.get_body(), them)
        while len(end) < end_num: end += self.replace_all(self.get_ending(), them)

        return {'title': title,'begin': begin,'body': body,'end': end}
    
    def gen_text(self, them: str = '年轻人买房', essay_num: int = 500) -> str:
        result = self.gen(them,essay_num)
        return f"{result['title']}\n    {result['begin']}\n    {result['body']}\n    {result['end']}"


if __name__ == "__main__":
    if 1:
        a=BullshitArticle('C:/Users/123/Documents/ZYC/mirai program/haoshenhaoshen/statics/bullshit_article_data.json')
        article=a.make_bullshit_article('快乐')
        print(article)
    else:
        import argparse
        paser = argparse.ArgumentParser(
            prog='slscq.py',
            description='auto generate a shit article'
        )
        paser.add_argument('them',help='article topic',type=str)
        paser.add_argument('-n','--essay_num',help='least character of article',type=int,default=500,metavar='num')
        paser.add_argument('-d','--data_source',help='json file of data source',type=str,default='../data.json',metavar='json file')
        params = paser.parse_args()
        arc_gen = Slscq(params.data_source)
        arc_text = arc_gen.gen_text(params.them,params.essay_num)
        print(arc_text)