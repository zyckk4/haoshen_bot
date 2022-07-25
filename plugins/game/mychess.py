# -*- coding: utf-8 -*-
"""
@author: zyckk4 https://github.com/zyckk4
"""

import chess
import chess.svg
from PIL import Image
from cairosvg import svg2png
from io import BytesIO

class PlayChess:
    def __init__(self,players:list):
        # the second player in players plays first(white)
        # the two players shouldn't use the same name
        self.players=players
        self.board=chess.Board()
        self.num=0
        self.frames=[]
        self.__save_frame()
        
    def play(self,input_str,player=None):
        if player is not None:
            try:
                t=self.players.index(player)
            except:
                raise KeyError("Invalid playername!")
            if t!=self.turn:
                raise ValueError("Not your turn to play!")
        try:
            self.__push(input_str)
        except ValueError:
            raise ValueError("Invalid or illegal san!")
        self.__save_frame()
        if self.board.outcome() is not None:
            outcome=self.board.outcome()
            if outcome.winner is None:
                return 'Draw!',2
            else:
                return f"{player} wins the game!",t
        
    def __push(self,input_str):
        self.board.push_san(input_str)
        self.num+=1
        
    def undo(self):
        if self.num==0:
            raise ValueError("不允许还没下就悔棋！")
        self.board.pop()
        self.__save_frame(True)
    
    @property
    def outcome(self):
        if self.board.outcome() is None:
            return -1
        if self.board.outcome().winner is None:
            return 2
        return self.board.outcome().winner
    
    @property
    def turn(self):
        return self.board.turn
    
    def get_img_bytes(self,orientation=None,img_size=1000):
        if orientation is None:
            orientation=self.turn
        return svg2png(bytestring=chess.svg.board(self.board,orientation=orientation,size=img_size))
    
    def get_img_PIL(self,orientation=None,img_size=1000):
        if orientation is None:
            orientation=self.turn
        img_content=svg2png(bytestring=chess.svg.board(self.board,orientation=orientation,size=img_size))
        return Image.open(BytesIO(img_content))
    
    def __save_frame(self,pop=False):
        if pop:
            self.frames.pop()
        else:
            self.frames.append(self.get_img_PIL())
        
    def get_gif(self,gif_size=None):
        bt=BytesIO()
        frames=self.frames.copy()
        if gif_size is not None:
            if not isinstance(gif_size, int):
                raise ValueError('"gif_size" must be int or None!')
            for img in frames:
                img.resize((gif_size,gif_size))
        frames[0].save(
            bt,
            format="GIF",
            append_images=self.frames[1:],
            save_all=True,
            duration=800,
            loop=0,
        )
        return bt.getvalue()
    
            