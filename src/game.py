# Game state management for Caro
from .board import Board

class Game:
    def __init__(self, size=10, win_condition=5):
        self.board = Board(size, win_condition)
        self.size = size
        self.win_condition = win_condition
        self.move_history = []
        self.current_player = 'X'
        self.scores = {'X': 0, 'O': 0}
        self.move_count = 0
        self.finished = False
        self.winner = None

    def reset(self):
        self.board.reset()
        self.move_history = []
        self.current_player = 'X'
        self.move_count = 0
        self.finished = False
        self.winner = None

    def make_move(self, row, col):
        if self.board.make_move(row, col, self.current_player):
            self.move_history.append((row, col, self.current_player))
            self.move_count += 1
            if self.board.check_win(self.current_player):
                self.finished = True
                self.winner = self.current_player
                self.scores[self.current_player] += 1
            elif self.board.is_full():
                self.finished = True
                self.winner = None
            else:
                self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False

    def undo(self):
        if self.move_history:
            row, col, player = self.move_history.pop()
            self.board.undo_move(row, col)
            self.current_player = player
            self.move_count -= 1
            self.finished = False
            self.winner = None
            return True
        return False

    def redo(self):
        # Placeholder for redo logic if needed
        pass

    def get_valid_moves(self):
        return self.board.get_valid_moves()

    def get_winning_sequence(self):
        return self.board.winning_sequence
