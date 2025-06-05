# Board representation and logic for Caro game

class Board:
    def __init__(self, size=10, win_condition=5):
        self.size = size
        self.win_condition = win_condition
        self.EMPTY = ' '
        self.grid = [[self.EMPTY for _ in range(size)] for _ in range(size)]
        self.last_move = None
        self.winning_sequence = []

    def reset(self):
        self.grid = [[self.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.last_move = None
        self.winning_sequence = []

    def is_valid_move(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.grid[row][col] == self.EMPTY

    def make_move(self, row, col, player):
        if self.is_valid_move(row, col):
            self.grid[row][col] = player
            self.last_move = (row, col)
            return True
        return False

    def undo_move(self, row, col):
        self.grid[row][col] = self.EMPTY
        self.last_move = None

    def get_valid_moves(self):
        moves = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == self.EMPTY:
                    moves.append((i, j))
        return moves

    def is_full(self):
        return all(cell != self.EMPTY for row in self.grid for cell in row)

    def check_win(self, player):
        # Returns True and winning sequence if player wins
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] != player:
                    continue
                for dx, dy in directions:
                    seq = [(i, j)]
                    for k in range(1, self.win_condition):
                        ni, nj = i + dx*k, j + dy*k
                        if 0 <= ni < self.size and 0 <= nj < self.size and self.grid[ni][nj] == player:
                            seq.append((ni, nj))
                        else:
                            break
                    if len(seq) == self.win_condition:
                        self.winning_sequence = seq
                        return True
        return False
