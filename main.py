from src.game import Game
from src.ai import CaroAI
from src.ui import print_board, show_status, get_player_move, console
import time

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Caro console game")
    parser.add_argument('--size', type=int, default=10, help='Board size (default: 10)')
    parser.add_argument('--win', type=int, default=5, help='Win condition (default: 5)')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'], default='medium', help='AI difficulty')
    args = parser.parse_args()
    size = args.size
    win_condition = args.win
    difficulty = args.difficulty
    game = Game(size, win_condition)
    ai = CaroAI(player='O', opponent='X')
    while True:
        game.reset()
        while not game.finished:
            console.clear()
            print_board(game.board, highlight=game.board.last_move, win_seq=game.get_winning_sequence(), show_index=True)
            show_status(game)
            if game.current_player == 'X':
                move = get_player_move(game.board)
                if move == 'quit':
                    return
                if move == 'undo':
                    game.undo()
                    continue
                if move == 'redo':
                    # Redo logic placeholder
                    continue
                row, col = move
                if not game.make_move(row, col):
                    console.print("[bold yellow]Nước đi không hợp lệ, hãy thử lại![/bold yellow]")
                    time.sleep(1)
            else:
                console.print("[bold red]AI đang suy nghĩ...[/bold red]")
                t0 = time.time()
                row, col = ai.get_move(game.board, win_condition, difficulty)
                t1 = time.time()
                game.make_move(row, col)
                print_board(game.board, highlight=(row, col), win_seq=game.get_winning_sequence(), show_index=True)
                show_status(game, timer=t1-t0)
                time.sleep(0.5)
        # End of game
        console.clear()
        print_board(game.board, win_seq=game.get_winning_sequence(), show_index=True)
        show_status(game)
        if game.winner:
            if game.winner == 'X':
                console.print("[bold green]Bạn đã thắng![/bold green]")
            else:
                console.print("[bold red]AI đã thắng![/bold red]")
        else:
            console.print("[bold yellow]Hòa! Không còn nước đi.[/bold yellow]")
        again = console.input("[bold magenta]Chơi lại? (y/n): [/bold magenta]")
        if again.lower() not in ["y", "yes"]:
            break

if __name__ == "__main__":
    main()
