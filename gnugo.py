#------------------------------------------------
# name: gnugo.py
# author: taster
# date: 2025-04-17 10:49:53 星期四
# id: 6aafd1c5dfb12d39607a5fb9a78151d3
# description: 利用gnugo作为backend来构建的游戏
#------------------------------------------------
import tkinter as tk
from tkinter import messagebox
import subprocess
import re

class GoBoard:
    def __init__(self, size=19):
        self.size = size
        self.gnugo = subprocess.Popen(
            ["gnugo", "--mode", "gtp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        self.current_player = "black"  # 黑棋先行
        self.stones = {}  # 记录棋盘上的棋子 {(x,y): color}

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

class GoGUI(tk.Tk):
    def __init__(self, board_size=19):
        super().__init__()
        self.board_size = board_size
        self.cell_size = 30
        self.board = GoBoard(board_size)
        self.init_ui()

    def init_ui(self):
        # 棋盘画布
        self.canvas = tk.Canvas(
            self, 
            width=self.cell_size * (self.board_size + 1),
            height=self.cell_size * (self.board_size + 1),
            bg="#DEB887"
        )
        self.canvas.pack()
        self.draw_grid()

        # 绑定点击事件
        self.canvas.bind("<Button-1>", self.on_click)

        # 控制按钮
        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=10)
        tk.Button(self.btn_frame, text="AI Move", command=self.ai_move).pack(side=tk.LEFT)
        tk.Button(self.btn_frame, text="Reset", command=self.reset).pack(side=tk.LEFT)

    def draw_grid(self):
        # 绘制棋盘网格线
        for i in range(self.board_size):
            x = self.cell_size * (i + 1)
            self.canvas.create_line(
                self.cell_size, x,
                self.cell_size * self.board_size, x
            )
            self.canvas.create_line(
                x, self.cell_size,
                x, self.cell_size * self.board_size
            )
        
        # 绘制特殊标记点（星位）
        star_points = []
        if self.board_size == 19:
            star_points = [3, 9, 15]
        elif self.board_size == 13:
            star_points = [3, 6, 9, 12]
        elif self.board_size == 9:
            star_points = [2, 4, 6, 8]
        
        for x in star_points:
            for y in star_points:
                cx = self.cell_size * (x + 1)
                cy = self.cell_size * (y + 1)
                self.canvas.create_oval(
                    cx - 3, cy - 3,
                    cx + 3, cy + 3,
                    fill="black"
                )

    def on_click(self, event):
        # 将点击坐标转换为棋盘坐标
        x = round((event.x - self.cell_size) / self.cell_size)
        y = round((event.y - self.cell_size) / self.cell_size)
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            self.place_stone(x, y, self.board.current_player)
            self.ai_move()

    def place_stone(self, x, y, color):
        # 发送落子命令给GnuGo
        cmd = f"play {color} {chr(ord('A') + x)}{y+1}"
        response = self.board.send_command(cmd)
        if "illegal" not in response.lower():
            # 检查是否有提子
            self.check_captured_stones()
            self.draw_stone(x, y, color)
            self.board.current_player = "white" if color == "black" else "black"
        else:
            messagebox.showerror("Invalid Move", "此处不能落子！")

    def draw_stone(self, x, y, color):
        # 在棋盘上绘制棋子
        cx = self.cell_size * (x + 1)
        cy = self.cell_size * (y + 1)
        self.canvas.create_oval(
            cx - 12, cy - 12,
            cx + 12, cy + 12,
            fill=color, outline="black"
        )
        # 记录棋子位置
        self.board.stones[(x, y)] = color

    def check_captured_stones(self):
        # 获取被提掉的棋子
        response = self.board.send_command("list_captures")
        if "=" in response:
            captures = response.split("=")[1].strip()
            if captures:
                for move in captures.split():
                    # 解析坐标
                    x = ord(move[0].upper()) - ord('A')
                    y = int(move[1:]) - 1
                    # 移除被提掉的棋子
                    if (x, y) in self.board.stones:
                        self.remove_stone(x, y)

    def remove_stone(self, x, y):
        # 从棋盘上移除棋子
        cx = self.cell_size * (x + 1)
        cy = self.cell_size * (y + 1)
        # 创建一个与背景同色的圆形来覆盖棋子
        self.canvas.create_oval(
            cx - 12, cy - 12,
            cx + 12, cy + 12,
            fill="#DEB887", outline="#DEB887"
        )
        # 重新绘制交叉点
        self.draw_grid_lines_at(x, y)
        # 从记录中移除
        if (x, y) in self.board.stones:
            del self.board.stones[(x, y)]

    def draw_grid_lines_at(self, x, y):
        # 在指定位置重新绘制网格线（用于提子后恢复棋盘）
        cx = self.cell_size * (x + 1)
        cy = self.cell_size * (y + 1)
        
        # 绘制水平线
        if x > 0:
            self.canvas.create_line(
                self.cell_size * x, cy,
                cx, cy
            )
        if x < self.board_size - 1:
            self.canvas.create_line(
                cx, cy,
                self.cell_size * (x + 2), cy
            )
        
        # 绘制垂直线
        if y > 0:
            self.canvas.create_line(
                cx, self.cell_size * y,
                cx, cy
            )
        if y < self.board_size - 1:
            self.canvas.create_line(
                cx, cy,
                cx, self.cell_size * (y + 2)
            )

    def ai_move(self):
        # 让GnuGo生成AI落子
        cmd = "genmove " + ("black" if self.board.current_player == "black" else "white")
        response = self.board.send_command(cmd)
        if "= " in response:
            move = re.search(r"= ([A-Za-z][0-9]+)", response).group(1)
            x = ord(move[0].upper()) - ord('A')
            y = int(move[1:]) - 1
            self.draw_stone(x, y, self.board.current_player)
            self.board.current_player = "white" if self.board.current_player == "black" else "black"

    def reset(self):
        # 重置棋盘
        self.board.send_command("clear_board")
        self.canvas.delete("all")
        self.draw_grid()
        self.board.current_player = "black"

if __name__ == "__main__":
    app = GoGUI(board_size=19)
    app.title("Python Go with GnuGo")
    app.mainloop()

