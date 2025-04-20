#------------------------------------------------
# name: main.py
# author: taster
# date: 2025-04-07 15:49:50 星期一
# id: 8a955a873923ce1ded0074ac98fad4e1
# description: 一个简单的围棋程序
#------------------------------------------------
from gui import GoGUI

if __name__ == "__main__":
    app = GoGUI(board_size=19)
    app.mainloop()

