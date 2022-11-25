# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
import os
import logging
import importlib
from datetime import datetime
import yaml
from mirai import Mirai, WebSocketAdapter
from mirai_extensions.trigger import InterruptControl


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
        self.set_logger()

    def load_config(self):
        with open('config/config.yml', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def set_logger(self):
        logger = logging.getLogger("haoshen")
        logger.setLevel(logging.INFO)
        if not os.path.exists('log'):
            os.mkdir('log')
        fh = logging.FileHandler(
            f'./log/{datetime.now().strftime("%Y.%m.%d_%H.%M.%S")}.log',
            encoding='utf-8',
        )
        #sh = logging.StreamHandler()
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(fmt)
        #sh.setFormatter(fmt)
        logger.handlers.clear()
        logger.addHandler(fh)
        #logger.addHandler(sh)
        self.logger = logger

    def import_modules(self):
        for module in os.listdir("plugins/management"):
            if module.startswith('__'):
                continue
            module_name = module.split('.')[0]
            module_dir = "plugins.management."+module.split('.')[0]
            importlib.import_module(module_dir, module_dir)
            self.logger.info(f'管理模块 {module_name} 已加载')
        for module in os.listdir("plugins"):
            if module.startswith('__') or module in ('management'):
                continue
            module_name = module if os.path.isdir(
                module) else module.split('.')[0]
            module_dir = 'plugins.'+module_name
            importlib.import_module(module_dir, module_dir)
            self.logger.info(f'常规模块 {module_name} 已加载')
