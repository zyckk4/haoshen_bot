# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""

import importlib
import os

from utils.instance import core_instance

logger = core_instance.get().logger

for module in os.listdir("plugins/math"):
    if module.startswith(('_', '__')) or os.path.isdir("plugins/math" + module):
        continue
    module_name = module.split('.')[0]
    module_dir = "plugins.math."+module_name
    importlib.import_module(module_dir, module_dir)
    logger.info(f'-- 模块 {module_name} 已加载')
