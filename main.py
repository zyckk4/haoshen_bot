# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from utils.bot_core import Core
from utils.instance import core_instance

if __name__ == '__main__':
    core=Core()
    core_instance.set(core)
    core.import_modules()
    core.bot.run()