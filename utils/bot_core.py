# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import importlib
import logging
import os
from datetime import datetime

import yaml
from mirai import Mirai, WebSocketAdapter
from mirai_extensions.trigger import InterruptControl

from utils.bot_exceptions import BotImportError


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
        sh = logging.StreamHandler()
        fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        fh.setFormatter(fmt)
        sh.setFormatter(fmt)
        logger.handlers.clear()
        logger.propagate = False
        logger.addHandler(fh)
        logger.addHandler(sh)
        self.logger = logger

    def import_modules(self):
        for module in os.listdir("plugins/management"):
            if module.startswith(('_', '__')):
                continue
            module_name = module.split('.')[0]
            module_dir = "plugins.management."+module_name
            importlib.import_module(module_dir, module_dir)
            self.logger.info(f'管理模块 {module_name} 已加载')
        for module in os.listdir("plugins"):
            if module.startswith(('_', '__')) or module in ('management'):
                continue
            if os.path.isdir('plugins/' + module):
                module_name = module
                module_dir = 'plugins.' + module_name
                self.logger.info(f'准备加载大模块 {module_name}:')
                importlib.import_module(module_dir, module_dir)
                self.logger.info(f'大模块 {module_name} 已加载')
            else:
                module_name = module.split('.')[0]
                module_dir = 'plugins.' + module_name
                try:
                    importlib.import_module(module_dir, module_dir)
                    self.logger.info(f'常规模块 {module_name} 已加载')
                except BotImportError:
                    self.logger.info(f'常规模块 {module_name} 加载失败！可能缺少依赖')
