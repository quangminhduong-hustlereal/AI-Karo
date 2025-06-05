# AI logic for Caro game: minimax, heuristic, transposition table
import random
import time

class CaroAI:
    def __init__(self, player='O', opponent='X', depth=2, time_limit=2.0):
        self.player = player
        self.opponent = opponent
        self.depth = depth
        self.time_limit = time_limit
        self.transposition = {}

    def evaluate(self, board, win_condition):
        # Heuristic: count open-ended sequences for both players
        def count_sequences(player):
            score = 0
            directions = [(0,1), (1,0), (1,1), (1,-1)]
            for i in range(board.size):
                for j in range(board.size):
                    if board.grid[i][j] != player:
                        continue
                    for dx, dy in directions:
                        count = 1
                        open_ends = 0
                        for d in [1, -1]:
                            k = 1
                            while True:
                                ni, nj = i + dx*k*d, j + dy*k*d
                                if 0 <= ni < board.size and 0 <= nj < board.size:
                                    if board.grid[ni][nj] == player:
                                        count += 1
                                    elif board.grid[ni][nj] == board.EMPTY:
                                        open_ends += 1
                                        break
                                    else:
                                        break
                                else:
                                    break
                                k += 1
                        if count >= win_condition:
                            score += 100000
                        elif count == win_condition-1 and open_ends == 2:
                            score += 10000
                        elif count == win_condition-2 and open_ends == 2:
                            score += 1000
                        elif count == win_condition-3 and open_ends == 2:
                            score += 100
                        elif count == win_condition-4 and open_ends == 2:
                            score += 10
            return score
        return count_sequences(self.player) - count_sequences(self.opponent)

    def minimax(self, board, win_condition, depth, alpha, beta, maximizing, start_time):
        key = tuple(tuple(row) for row in board.grid)
        if key in self.transposition:
            return self.transposition[key]
        if board.check_win(self.player):
            return 100000, None
        if board.check_win(self.opponent):
            return -100000, None
        if board.is_full() or depth == 0 or (time.time() - start_time) > self.time_limit:
            return self.evaluate(board, win_condition), None
        moves = self.smart_moves(board)
        best_move = None
        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                board.make_move(*move, self.player)
                eval, _ = self.minimax(board, win_condition, depth-1, alpha, beta, False, start_time)
                board.undo_move(*move)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition[key] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                board.make_move(*move, self.opponent)
                eval, _ = self.minimax(board, win_condition, depth-1, alpha, beta, True, start_time)
                board.undo_move(*move)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition[key] = (min_eval, best_move)
            return min_eval, best_move

    def smart_moves(self, board):
        # Only consider moves within 2 cells of existing pieces
        moves = set()
        for i in range(board.size):
            for j in range(board.size):
                if board.grid[i][j] != board.EMPTY:
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            ni, nj = i + dx, j + dy
                            if 0 <= ni < board.size and 0 <= nj < board.size and board.grid[ni][nj] == board.EMPTY:
                                moves.add((ni, nj))
        if not moves:
            return board.get_valid_moves()
        return list(moves)

    def get_move(self, board, win_condition, difficulty='medium'):
        if difficulty == 'easy':
            return random.choice(board.get_valid_moves())
        elif difficulty == 'hard':
            self.depth = 4
            self.time_limit = 3.0
        else:
            self.depth = 2
            self.time_limit = 1.0
        self.transposition = {}
        start_time = time.time()
        _, move = self.minimax(board, win_condition, self.depth, -float('inf'), float('inf'), True, start_time)
        if move is None:
            move = random.choice(board.get_valid_moves())
        return move
