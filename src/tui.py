#------------------------------------------------
# name: tui.py
# author: taster
# date: 2025-04-23 20:41:49 星期三
# id: 3c31287864f9febb12142c503641cc0a
# description: 命令行用户界面
#------------------------------------------------
import os
from src.backend import GoBoard, GnugoAI


class GoTUI:
    def __init__(self, board_size=19, ai=False):
        self.ai = ai
        if ai:
            self.board = GnugoAI(board_size)
        else:
            self.board = GoBoard(board_size)
        self.board_size = board_size
        # 坐标字母映射（跳过I）
        self.letters = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'[:board_size]
        self.star_points = self._get_star_positions()

    def _get_star_positions(self):
        """根据棋盘尺寸返回星点坐标集合"""
        if self.board_size == 19:
            stars = [3, 9, 15]  # 对应1-based的4,10,16
        elif self.board_size == 13:
            stars = [3, 6, 9]
        elif self.board_size == 9:
            stars = [2, 4, 6]
        else:
            return set()
        # 生成所有星点组合
        return {(x, y) for x in stars for y in stars}
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_board(self):
        """打印棋盘，包含星点标记"""
        print('   ' + ' '.join(self.letters))
        
        for y in range(self.board_size):
            line = []
            for x in range(self.board_size):
                stone = self.board.cur_board[x, y]
                if stone == 1:
                    line.append('○')  # 白子
                elif stone == -1:
                    line.append('●')  # 黑子
                else:
                    if (x, y) in self.star_points:
                        line.append('+')  # 星点
                    elif x == 0 or x == self.board_size-1 or y == 0 or y == self.board_size-1:
                        line.append('+')  # 边界
                    else:
                        line.append('·')  # 空点
            print(f"{y+1:2d} {' '.join(line)} {y+1:2d}")
        
        print('   ' + ' '.join(self.letters))

    def parse_input(self, input_str):
        """解析用户输入：支持坐标（如A1）或命令（undo/redo/reset/exit）"""
        input_str = input_str.strip().upper()
        if input_str in ('UNDO', 'U'):
            self.board.undo()
            return True
        elif input_str in ('REDO', 'R'):
            self.board.redo()
            return True
        elif input_str in ('RESET', 'C'):
            self.board.reset()
            return True
        elif input_str in ('EXIT', 'QUIT', 'Q'):
            exit()
        elif len(input_str) >= 2:
            # 尝试解析坐标（如A1，B2等）
            if input_str[0] in self.letters and input_str[1:].isdigit():
                x = self.letters.index(input_str[0])
                y = int(input_str[1:]) - 1
                if 0 <= y < self.board_size:
                    return self.board.place_stone(x, y)
        print("无效输入！格式应为 A1 或命令")
        return False

    def run(self):
        """主循环"""
        while True:
            self.clear_screen()
            print(f"当前玩家: {self.board.cur_player}")
            self.print_board()
            print("命令说明:")
            print("  A1: 落子 | undo/u: 悔棋 | redo/r: 重做")
            print("  reset/c: 重置 | exit/q: 退出")
            
            if self.board.cur_player == "white" and self.ai:
                self.board.ai_move()
            else:
                cmd = input(">>> ").strip()
                success = self.parse_input(cmd)
                if not success:
                    input("按回车继续...")
