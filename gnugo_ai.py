#------------------------------------------------
# name: gnugo_ai.py
# author: taster
# date: 2025-04-24 11:20:28 星期四
# id: 8f610c4040a32bef3f8ff6bc1d95d093
# description: 支持完整历史同步的GNU Go AI集成
#------------------------------------------------
import subprocess
import numpy as np
from backend import GoBoard
import re

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
