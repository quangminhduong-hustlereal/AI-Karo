# Game state management for Caro
from .board import Board

class Game:
    def __init__(self, size: int = 10, win_condition: int = 5):
        self.board = Board(size, win_condition)
        self.size = size
        self.win_condition = win_condition
        self.move_history: list[tuple[int, int, str]] = []
        self.redo_stack: list[tuple[int, int, str]] = []
        self.current_player: str = 'X'
        self.scores: dict[str, int] = {'X': 0, 'O': 0}
        self.move_count: int = 0
        self.finished: bool = False
        self.winner: str | None = None

    def reset(self):
        self.board.reset()
        self.move_history = []
        self.redo_stack = []
        self.current_player = 'X'
        self.move_count = 0
        self.finished = False
        self.winner = None

    def make_move(self, row, col):
        if self.board.make_move(row, col, self.current_player):
            self.move_history.append((row, col, self.current_player))
            # any new move invalidates redo history
            self.redo_stack = []
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
            # push to redo stack
            self.redo_stack.append((row, col, player))
            # restore current player to who made the undone move
            self.current_player = player
            self.move_count -= 1
            self.finished = False
            self.winner = None
            return True
        return False

    def redo(self):
        if self.redo_stack:
            row, col, player = self.redo_stack.pop()
            # ensure consistency: current player should match the player of the move to redo
            if self.board.is_valid_move(row, col):
                self.board.make_move(row, col, player)
                self.move_history.append((row, col, player))
                self.move_count += 1
                if self.board.check_win(player):
                    self.finished = True
                    self.winner = player
                    self.scores[player] += 1
                elif self.board.is_full():
                    self.finished = True
                    self.winner = None
                else:
                    # toggle to the opposite player after redoing this move
                    self.current_player = 'O' if player == 'X' else 'X'
                return True
        return False

    def get_valid_moves(self):
        return self.board.get_valid_moves()

    def get_winning_sequence(self):
        return self.board.winning_sequence
