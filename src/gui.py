#------------------------------------------------
# name: gui.py
# author: taster
# date: 2025-04-19 19:20:39 星期六
# id: 66fa17e9a5fccc186c754a998de66a07
# description: 围棋游戏的前端
#------------------------------------------------
import tkinter as tk
from tkinter import messagebox
from src.backend import GoBoard, GnugoAI


class GoGUI(tk.Tk):
    def __init__(self, board_size=19, ai=False):
        super().__init__()
        self.title("围棋游戏")
        self.board_size = board_size
        self.cell_size = 30 # 网格的宽度
        self.ai = ai
        if ai:
            self.board = GnugoAI(board_size) # 后台棋盘类
        else:
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
        self.draw_stone()

        # 绑定点击事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.bind("<q>", lambda e: self.destroy())
        
        # 控制按钮
        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=10)
        # tk.Button(self.btn_frame, text="AI Move", command=self.ai_move).pack(side=tk.LEFT)
        tk.Button(self.btn_frame, text="Reset", command=self.reset).pack(side=tk.LEFT)
        tk.Button(self.btn_frame, text="Undo", command=self.undo).pack(side=tk.LEFT)
        tk.Button(self.btn_frame, text="Redo", command=self.redo).pack(side=tk.LEFT)

    def reset(self):
        """重置棋盘"""
        self.board.reset()
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_stone()

    def undo(self):
        """退回一步"""
        self.board.undo()
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_stone()

    def redo(self):
        """向前一步"""
        self.board.redo()
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_stone()

    def on_click(self, event):
        """
        将点击坐标转换为棋盘坐标
        """
        x = round((event.x - self.cell_size) / self.cell_size)
        y = round((event.y - self.cell_size) / self.cell_size)
        flag = self.board.place_stone(x, y)
        if flag:
            self.canvas.delete("all")
            self.draw_grid()
            self.draw_stone()
            if self.ai and self.board.cur_player == "white":
                self.board.ai_move()
                self.canvas.delete("all")
                self.draw_grid()
                self.draw_stone()
        if not flag:
            messagebox.showerror("Invalid Move", "此处不能落子！")

    def draw_stone(self):
        """
        在棋盘上绘制棋子
        """
        for i in range(self.board.size):
            for j in range(self.board.size):
                cx = self.cell_size * (i + 1)
                cy = self.cell_size * (j + 1)
                if self.board.cur_board[i, j] == 1:
                    color = "white"
                elif self.board.cur_board[i, j] == -1:
                    color = "black"
                else:
                    continue
                self.canvas.create_oval(
                    cx - 12, cy - 12,
                    cx + 12, cy + 12,
                    fill=color, outline="black"
                )

    def draw_grid(self):
        """
        绘制棋盘网格线
        """
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

