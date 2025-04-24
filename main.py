#------------------------------------------------
# name: main.py
# author: taster
# date: 2025-04-07 15:49:50 星期一
# id: 8a955a873923ce1ded0074ac98fad4e1
# description: 一个简单的围棋程序
#------------------------------------------------
from src.gui import GoGUI
from src.tui import GoTUI

if __name__ == "__main__":
    # # 文本用户界面
    # game = GoTUI(board_size=19, ai=True)
    # game.run()
    # 窗口用户界面
    game = GoGUI(board_size=19)
    game.mainloop()

