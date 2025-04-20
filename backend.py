#------------------------------------------------
# name: backend.py
# author: taster
# date: 2025-04-20 10:40:31 星期日
# id: 41361e00bc9851721e712f1881018e7c
# description: 棋盘类及其他后台逻辑
#------------------------------------------------
import numpy as np
from collections import deque


class GoBoard:
    """
    后台的棋盘，可以用于沟通用户与前端或者ai程序与前端
    """
    def __init__(self, board_size=19):
        self.size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        # self.board = np.random.randint(-1, 2, (board_size, board_size))
        self.current_player = "black"

    def check_captured_stones(self):
        """检查被提掉的棋子"""
        self.qi_board = np.zeros_like(self.board, dtype=int) # 每个子的气
        self.visited = np.zeros_like(self.board, dtype=bool) # 该棋子是否被访问过
        # 需要等全部检查完之后才能改动棋盘
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i, j] != 0 and not self.visited[i, j]:
                    self.check_qi(i, j) # 把当前棋子的气记录下来

        # 根据棋子的气来提子
        for i in range(self.size):
            for j in range(self.size):
                if self.qi_board[i, j] == 0:
                    self.board[i, j] = 0

        # print(self.qi_board)

    def check_qi(self, i, j):
        """
        利用广度优先(BFS)检查 (x, y) 位置的棋子的气
        由于围棋规则中相连的棋子具有相同的气，需要找到连通块
        """
        # 找到连通块
        color = self.board[i, j]
        group = []
        queue = deque([(i, j)])
        self.visited[i, j] = True
        
        # 用BFS找到所有相连的同色棋子
        while queue:
            x, y = queue.popleft()
            group.append((x, y))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # 向四周搜索
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 < ny < self.size:
                    if self.board[nx, ny] == color and not self.visited[nx, ny]:
                        self.visited[nx, ny] = True
                        queue.append((nx, ny))

        # 计算该连通块的气
        qi_set = set()
        for x, y in group:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # 向四周搜索
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 < ny < self.size:
                    if self.board[nx, ny] == 0:
                        qi_set.add((nx, ny))

        # 为连通块中的所有棋子分配相同的气
        qi_count = len(qi_set)
        for x, y in group:
            self.qi_board[x, y] = qi_count

    def place_stone(self, x, y):
        """落子"""

        # TODO:
        # 1. 当前落子之后，如果存在可以被提掉的对方子，则当前的落子成立
        # 2. 当前落子之后，如果不存在可以被提掉的对方子，则当前位置不能落子

        if not (0 <= x < self.size and 0 <= y < self.size): # 越界
            return False
        if self.board[x, y] != 0: # 已经有子了
            return False
        if self.current_player == "white":
            self.board[x, y] = 1 # 用1表示落上白子
            self.current_player = "black"
            self.check_captured_stones() # 提子
            return True
        elif self.current_player == "black":
            self.board[x, y] = -1 # 用0表示落上黑子
            self.current_player = "white"
            self.check_captured_stones() # 提子
            return True
        return False # 其他情况

    def reset(self):
        """ 重置 """
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = "black"

