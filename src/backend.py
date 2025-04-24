#------------------------------------------------
# name: backend.py
# author: taster
# date: 2025-04-20 10:40:31 星期日
# id: 41361e00bc9851721e712f1881018e7c
# description: 棋盘类及其他后台逻辑
#------------------------------------------------
from abc import abstractmethod
import numpy as np
from collections import deque
import subprocess
import re
from src.linklist import DoubleLink


class Board:
    """
    用于描述2 player的2维棋盘类游戏的基类
    """
    def __init__(self, board_size):
        self.size           = board_size
        self.state          = DoubleLink() # 状态保存
        self.state.append({
            'board'  : np.zeros((board_size, board_size), dtype=int),
            'player' : "black",
            'move'   : (None, None) # 当前的棋步
        })

    @property
    def cur_board(self):
        return self.state.current_state()['board'].copy()

    @property
    def cur_player(self):
        return self.state.current_state()['player'].copy()

    @property
    def cur_move(self):
        return self.state.current_state()['move'].copy()

    def undo(self):
        self.state.move_previous()

    def redo(self):
        self.state.move_next()

    def reset(self):
        self.state.clear()

    @abstractmethod
    def rule(self, move):
        """接收一个棋步，把棋局转换到下一个状态（定义游戏规则）"""
        raise NotImplementedError("规则函数需要定义")

    def place_stone(self, move):
        new_state = self.rule(move)
        if new_state is None: # 尝试的棋步不符合规则，静默处理
            return None
        self.state.append(new_state) # 添加一个棋步


class GoBoard:
    """
    后台的棋盘，可以用于沟通用户与前端或者ai程序与前端
    """
    def __init__(self, board_size=19):
        self.size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = "black"
        # 处理“劫”规则
        self.last_ko_position = None  # 劫的位置
        self.last_ko_player = None    # 上次触发劫的玩家

        # 存储历史记录
        self.history = [(
            self.board.copy(),
            self.current_player,
            self.last_ko_position,
            self.last_ko_player,
        )]
        self.pointer = 0

    def cal_group_qi(self, x, y, temp_board):
        """
        计算指定位置所在的连通块的气（基于一个临时的棋盘）
        返回气的数量和所在的连通块
        """
        if temp_board[x, y] == 0: # 指定的位置没有棋子
            return 0, []
        color         = temp_board[x, y] # 指定位置的棋子类型
        visited       = np.zeros_like(temp_board, dtype=bool) # 记录是否被访问过
        queue         = deque([(x, y)])
        visited[x, y] = True
        group         = [] # 连通块
        qi_set        = set() # 计算为气的空位置

        # 用BFS找到所有相连的同色棋子
        while queue:
            i, j = queue.popleft()
            group.append((i, j))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # 向四周搜索
                ni, nj = i + dx, j + dy
                if 0 <= ni < self.size and 0 < nj < self.size:
                    if temp_board[ni, nj] == 0:
                        qi_set.add((ni, nj))
                    elif temp_board[ni, nj] == color and not visited[ni, nj]:
                        visited[ni, nj] = True
                        queue.append((ni, nj))
        return len(qi_set), group

    def find_captured_stones(self, temp_board):
        """
        返回所有敌方气为0的棋子
        为了适应围棋规则，需要延后提子，先模拟计算落子后的气
        """
        captured = [] # 返回的位置列表
        visited = np.zeros_like(temp_board, dtype=bool)

        for i in range(self.size):
            for j in range(self.size):
                if temp_board[i, j] != 0 and not visited[i, j]:
                    qi, group = self.cal_group_qi(i, j, temp_board)
                    if qi == 0:
                        captured.extend(group)
                    for x, y in group:
                        visited[x, y] = True

        return captured

    def place_stone(self, x, y):
        """
        落子
        需要满足高级的落子规则以及劫的规则
        """
        # 初步的检查
        if not (0 <= x < self.size and 0 <= y < self.size): # 越界
            return False
        if self.board[x, y] != 0: # 已经有子了
            return False

        # 劫争检查：禁止立即回提，至少需要间隔一手
        if self.last_ko_position and (x, y) == self.last_ko_position:
            if self.current_player != self.last_ko_player:
                return False

        # 创建一个临时棋盘用于模拟落子之后的状态
        current_color = 1 if self.current_player == "white" else -1
        temp_board = self.board.copy()
        temp_board[x, y] = current_color

        # 计算对方被提的棋子
        enemy_color = -current_color
        enemy_captured = [
            (i, j) for i, j in self.find_captured_stones(temp_board)
            if temp_board[i, j] == enemy_color
        ]

        # 模拟提掉对方的棋子
        for i, j in enemy_captured:
            temp_board[i, j] = 0

        # 模拟提子后检查自己的气
        my_qi, _ = self.cal_group_qi(x, y, temp_board)
        if my_qi == 0 and len(enemy_captured) == 0:
            return False # 禁止自杀行为（模拟结果：没有提掉对方的子，新落的子的气还为0）

        # 模拟成功，更新棋盘
        self.board = temp_board

        # 记录劫的状态
        if len(enemy_captured) == 1: # 只提掉对方一个子，此时构成了劫
            self.last_ko_position = enemy_captured[0]
            self.last_ko_player = self.current_player
        else:
            self.last_ko_position = None
            self.last_ko_player = None

        # 切换当前玩家
        self.current_player = "white" if self.current_player == "black" else "black"

        # 存储到历史，如果已经回退了，挤掉多余的历史记录
        self.history = self.history[:self.pointer + 1] + [(
            self.board.copy(),
            self.current_player,
            self.last_ko_position,
            self.last_ko_player,
        )]
        self.pointer += 1
        return True

    def _reset(self):
        """ 重置 """
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.current_player = "black"
        self.last_ko_position = None
        self.last_ko_player = None
        self.history = [(
            self.board.copy(),
            self.current_player,
            self.last_ko_position,
            self.last_ko_player,
        )] # 清空历史记录
        self.pointer = 0

    def _undo(self):
        """
        回退一步
        """
        if self.pointer == 0:
            return
        self.pointer -= 1
        self.board            = self.history[self.pointer][0]
        self.current_player   = self.history[self.pointer][1]
        self.last_ko_position = self.history[self.pointer][2]
        self.last_ko_player   = self.history[self.pointer][3]

    def _redo(self):
        """
        向前一步
        """
        if self.pointer == len(self.history) - 1:
            return
        self.pointer += 1
        self.board            = self.history[self.pointer][0]
        self.current_player   = self.history[self.pointer][1]
        self.last_ko_position = self.history[self.pointer][2]
        self.last_ko_player   = self.history[self.pointer][3]

    def reset(self):
        self._reset()

    def undo(self):
        self._undo()

    def redo(self):
        self._redo()


class GnugoAI(GoBoard):
    """
    利用GnuGo作为智能对战后台
    """
    def __init__(self, board_size=19, level=10):
        super().__init__(board_size)
        self.level = level
        self.gnugo = subprocess.Popen(
            ["gnugo", "--mode", "gtp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        # 游戏的预定配置
        self.send_command(f"boardsize {self.size}") # 定义棋盘大小
        self.send_command(f"level {self.level}") # 定义难度

    def send_command(self, command):
        assert self.gnugo.stdin is not None
        assert self.gnugo.stdout is not None
        self.gnugo.stdin.write(command + "\n")
        self.gnugo.stdin.flush()
        response = []
        while True:
            line = self.gnugo.stdout.readline()
            if line.strip() == "":
                break
            response.append(line.strip())
        return "\n".join(response)

    def ai_move(self):
        """生成GnuGo的棋步"""
        response = self.send_command(f"genmove {self.current_player}")
        if response.startswith("= "):
            move = re.search(r"= ([A-Za-z][0-9]+)", response).group(1)
            x = ord(move[0].upper()) - ord('A')
            y = int(move[1:]) - 1
            self.place_stone(x, y)

    def reset(self):
        self._reset()
        self.send_command("clear_board")

    def undo(self):
        self._undo()
        self._undo()
        self.send_command("undo")

    def redo(self):
        self._redo()
