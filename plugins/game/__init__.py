# -*- coding: utf-8 -*-
"""
@author: zyckk4  https://github.com/zyckk4
"""
from mirai import GroupMessage
from utils.utils import Listen
from .game import play_game, chess_main, game_admin

plugin = Listen(
    'game',
    '游戏功能'
)


@plugin.group()
async def game_main(event: GroupMessage):
    server_name = str(event.sender.group.id)
    await play_game(event, server_name)
    await chess_main(event, server_name)
    await game_admin(event, server_name)
