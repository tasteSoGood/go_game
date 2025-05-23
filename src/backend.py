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
        return self.state.current_state()['player']

    @property
    def cur_move(self):
        return self.state.current_state()['move']

    @property
    def pre_board(self):
        return self.state.previous_state()['board'].copy()

    @property
    def pre_player(self):
        return self.state.previous_state()['player']

    @property
    def pre_move(self):
        return self.state.previous_state()['move']

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

    def place_stone(self, x, y):
        new_state = self.rule((x, y))
        if new_state is None: # 尝试的棋步不符合规则，静默处理
            return False
        self.state.append(new_state) # 添加一个棋步
        return True


class WuziqiBoard(Board):
    """
    五子棋类
    """
    def __init__(self, board_size=19):
        super().__init__(board_size)

    def rule(self, move):
        if not (0 <= move[0] < self.size and 0 <= move[1] < self.size): # 越界
            return None
        if self.cur_board[*move] != 0: # 已经有子了
            return None
        # 如果赢了，就不能再下了
        if self.is_win():
            return None
        new_board = self.cur_board.copy()
        new_board[*move] = 1 if self.cur_player == "white" else -1

        return {
            "board": new_board,
            "player": "white" if self.cur_player == "black" else "black",
            "move": move,
        }

    def is_win(self):
        for i in range(self.size):
            if self._find_consecutive(self.cur_board[i], 5): # 行检查
                return True
            if self._find_consecutive(self.cur_board[:, i], 5): # 列检查
                return True
        # 遍历主、副对角线
        for offset in range(-self.size + 1, self.size):
            if self._find_consecutive(self.cur_board.diagonal(offset), 5):
                return True
            if self._find_consecutive(np.fliplr(self.cur_board).diagonal(offset), 5):
                return True
        return False

    def _find_consecutive(self, arr, n):
        """判断列表arr中是否存在n个连续相同的元素"""
        if n <= 0 or len(arr) < n:
            return False
        template = np.array([1] * n)
        white_arr = (arr == 1).astype(int)
        black_arr = (arr == -1).astype(int)
        for i in range(len(arr) - n):
            if np.sum(template * white_arr[i:i+n]) == n:
                return True
            if np.sum(template * black_arr[i:i+n]) == n:
                return True
        return False


class GoBoard(Board):
    """
    围棋类
    """
    def __init__(self, board_size=19):
        super().__init__(board_size)

    def rule(self, move):
        current_board  = self.cur_board  # 获取当前的棋盘状态
        current_player = self.cur_player # 获取当前的玩家
        current_move   = self.cur_move   # 获取当前的棋步
        x, y = move

        # 初步的检查
        if not (0 <= x < self.size and 0 <= y < self.size): # 越界
            return None
        if current_board[x, y] != 0: # 已经有子了
            return None

        # 处理“劫”规则
        color = 1 if current_player == 'white' else -1
        last_captured = np.sum(
            np.logical_xor(current_board == color, self.pre_board == color)
        ) # 计算上次提子数
        if last_captured == 1 and self.pre_move == move:
            return None

        # 创建一个临时棋盘用于模拟落子之后的状态
        current_color = 1 if current_player == "white" else -1
        temp_board = current_board.copy()
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
            return None # 禁止自杀行为（模拟结果：没有提掉对方的子，新落的子的气还为0）

        # 模拟成功，返回状态
        return {
            "board": temp_board,
            "player": "white" if current_player == "black" else "black",
            "move": move,
        }

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
        response = self.send_command(f"genmove {self.cur_player}")
        if response.startswith("= "):
            move = re.search(r"= ([A-Za-z][0-9]+)", response).group(1)
            x = ord(move[0].upper()) - ord('A')
            y = int(move[1:]) - 1
            self.place_stone(x, y)

    def reset(self):
        super().reset()
        self.send_command("clear_board")

    def undo(self):
        super().undo()
        super().undo()
        self.send_command("undo")

    def redo(self):
        super().redo()
