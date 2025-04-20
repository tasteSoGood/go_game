#------------------------------------------------
# name: backend.py
# author: taster
# date: 2025-04-20 10:40:31 星期日
# id: 41361e00bc9851721e712f1881018e7c
# description: 棋盘类及其他后台逻辑
#------------------------------------------------
import numpy as np


class GoBoard:
    """
    后台的棋盘，可以用于沟通用户与前端或者ai程序与前端
    """
    def __init__(self, board_size=19):
        self.size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        # self.board = np.random.randint(-1, 2, (board_size, board_size))
        self.current_player = "black"

    def place_stone(self, x, y):
        """落子"""
        if not (0 <= x < self.size and 0 <= y < self.size): # 越界
            return False
        if self.board[x, y] != 0: # 已经有子了
            return False
        if self.current_player == "white":
            self.board[x, y] = 1 # 用1表示落上白子
            self.current_player = "black"
            return True
        elif self.current_player == "black":
            self.board[x, y] = -1 # 用0表示落上黑子
            self.current_player = "white"
            return True
        return False # 其他情况

    def reset(self):
        """ 重置 """
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = "black"

