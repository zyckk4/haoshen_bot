# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from mirai import Mirai, WebSocketAdapter
from mirai_extensions.trigger import InterruptControl
import yaml
import os
import importlib


class Core:
    def __init__(self):
        self.config = self.load_config()
        self.bot = Mirai(
            qq=self.config['bot_qq'],
            adapter=WebSocketAdapter(
                verify_key=self.config['verify_key'], host=self.config['host'], port=self.config['port']
            )
        )
        self.inc = InterruptControl(self.bot)

    def load_config(self):
        with open('config/config.yml', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def import_modules(self):
        for module in os.listdir("plugins"):
            if module.startswith('__'):
                continue
            if not os.path.isdir(module):
                module = 'plugins.'+module.split('.')[0]
            importlib.import_module(module, module)
            print(f'{module} 模块已加载')
