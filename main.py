from src.ui_textual import run_textual_app


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Caro console game (Textual UI)")
    parser.add_argument('--size', type=int, default=10, help='Board size (default: 10)')
    parser.add_argument('--win', type=int, default=5, help='Win condition (default: 5)')
    parser.add_argument('--difficulty', choices=['easy', 'medium', 'hard'], default='medium', help='AI difficulty')
    args = parser.parse_args()
    size = args.size
    win_condition = args.win
    difficulty = args.difficulty

    run_textual_app(size=size, win_condition=win_condition, difficulty=difficulty)


if __name__ == "__main__":
    main()
