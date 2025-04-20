#------------------------------------------------
# name: main.py
# author: taster
# date: 2025-04-07 15:49:50 星期一
# id: 8a955a873923ce1ded0074ac98fad4e1
# description: 一个简单的围棋程序
#------------------------------------------------
import numpy as np

class GoGame:
    """
    围棋程序
    功能包括：
    - 初始化棋盘
    - 落子
    - 判断气( liberties )
    - 提子( remove_captured_stones )
    - 计算目数
    - 判断胜负
    """
    
    def __init__(self, board_size=19):
        """
        初始化围棋游戏
        :param board_size: 棋盘大小，默认为19x19
        """
        self.board_size = board_size
        self.chess_board = np.zeros((board_size, board_size), dtype=int)
        self.reset()
        
    def reset(self):
        """重置游戏"""
        self.chess_board    = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1     # 1表示黑棋，-1表示白棋
        self.game_over      = False
        self.white_captures = 0     # 白棋提子数
        self.black_captures = 0     # 黑棋提子数
        self.white_mu       = 0     # 白棋目数
        self.black_mu       = 0     # 黑棋目数
        self.komi           = 6.5   # 贴目
        self.last_move      = None  # 上一步落子位置
        self.passed_last    = False # 上一步是否pass
    
    def is_valid_move(self, x, y):
        """
        判断落子是否有效
        :param x: 行坐标
        :param y: 列坐标
        :return: 是否有效
        """
        # 检查是否在棋盘内
        if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size:
            return False
        
        # 检查是否已有棋子
        if self.chess_board[x, y] != 0:
            return False
            
        # 检查是否是自杀(需要更复杂的规则判断)
        # 这里简化处理，实际围棋规则更复杂
        return True
    
    def place_stone(self, x, y):
        """
        落子
        :param x: 行坐标
        :param y: 列坐标
        :return: 是否落子成功
        """
        if self.game_over or not self.is_valid_move(x, y):
            return False
            
        # 落子
        self.chess_board[x, y] = self.current_player
        self.last_move = (x, y)
        self.passed_last = False
        
        # 检查提子
        self.remove_captured_stones(x, y)
        
        # 切换玩家
        self.current_player *= -1
        return True
    
    def pass_turn(self):
        """
        跳过回合
        """
        if self.passed_last:
            self.game_over = True
        else:
            self.passed_last = True
            self.current_player *= -1
    
    def remove_captured_stones(self, x, y):
        """
        提子(移除被包围的棋子)
        :param x: 新落子的行坐标
        :param y: 新落子的列坐标
        """
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        opponent = -self.current_player
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.chess_board[nx, ny] == opponent:
                group, liberties = self.find_group_and_liberties(nx, ny)
                if liberties == 0:
                    self.remove_group(group)
                    if opponent == 1:
                        self.black_captures += len(group)
                    else:
                        self.white_captures += len(group)
    
    def find_group_and_liberties(self, x, y):
        """
        找到棋子所在的连通区域及其气
        :param x: 行坐标
        :param y: 列坐标
        :return: (棋子组, 气数)
        """
        if self.chess_board[x, y] == 0:
            return set(), 0
            
        color = self.chess_board[x, y]
        visited = set()
        queue = [(x, y)]
        group = set()
        liberties = set()
        
        while queue:
            cx, cy = queue.pop()
            if (cx, cy) in visited:
                continue
                
            visited.add((cx, cy))
            group.add((cx, cy))
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    if self.chess_board[nx, ny] == 0:
                        liberties.add((nx, ny))
                    elif self.chess_board[nx, ny] == color and (nx, ny) not in visited:
                        queue.append((nx, ny))
        
        return group, len(liberties)
    
    def remove_group(self, group):
        """移除一组棋子"""
        for x, y in group:
            self.chess_board[x, y] = 0
    
    def calculate_score(self):
        """
        计算目数(简化版)
        实际围棋计分规则更复杂，需要考虑活棋、死棋等
        """
        # 这里简化处理，只计算围住的空点和提子数
        self.black_mu = np.sum(self.chess_board == 1) + self.black_captures
        self.white_mu = np.sum(self.chess_board == -1) + self.white_captures + self.komi
    
    def get_winner(self):
        """
        判断胜负
        :return: 1黑胜, -1白胜, 0未结束
        """
        if not self.game_over:
            return 0
            
        self.calculate_score()
        if self.black_mu > self.white_mu:
            return 1
        else:
            return -1
    
    def display_board(self):
        """打印棋盘状态"""
        symbols = {0: '.', 1: 'X', -1: 'O'}
        print('   ' + ' '.join([chr(97 + i) for i in range(self.board_size)]))
        for i in range(self.board_size):
            print(f'{i+1:2} ', end='')
            for j in range(self.board_size):
                print(symbols[self.chess_board[i, j]], end=' ')
            print()
    
    def get_board_string(self):
        """获取棋盘字符串表示"""
        symbols = {0: '.', 1: 'X', -1: 'O'}
        rows = []
        for i in range(self.board_size):
            row = ''.join([symbols[self.chess_board[i, j]] for j in range(self.board_size)])
            rows.append(row)
        return '\n'.join(rows)


if __name__ == "__main__":
    # 1: 白子, -1: 黑子, 0: 空位
    # 创建游戏
    game = GoGame(9)  # 使用9x9小棋盘便于测试

    # 下几步棋
    game.place_stone(2, 2)  # 黑棋下在(2,2)
    game.place_stone(2, 3)  # 白棋下在(2,3)
    game.place_stone(3, 2)  # 黑棋下在(3,2)
    game.place_stone(3, 3)  # 白棋下在(3,3)

    # 显示棋盘
    game.display_board()

    # 计算得分
    game.calculate_score()
    print(f"黑棋得分: {game.black_mu}, 白棋得分: {game.white_mu}")

    # 判断胜负
    winner = game.get_winner()
    if winner == 1:
        print("黑棋胜!")
    elif winner == -1:
        print("白棋胜!")
    else:
        print("游戏进行中...")
