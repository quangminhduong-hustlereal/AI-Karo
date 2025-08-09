import argparse
from src.tui_app import run_textual


def main():
    parser = argparse.ArgumentParser(description="Caro console game (Textual UI)")
    parser.add_argument('--size', type=int, default=10, help='Board size (default: 10)')
    parser.add_argument('--win', type=int, default=5, help='Win condition (default: 5)')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'], default='medium', help='AI difficulty')
    args = parser.parse_args()
    run_textual(size=args.size, win=args.win, difficulty=args.difficulty)


if __name__ == "__main__":
    main()