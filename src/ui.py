# UI and input handling for Caro game using Rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import time

console = Console()

def print_board(board, highlight=None, win_seq=None, show_index=False):
    from rich import box
    table = Table(show_header=True, header_style="bold magenta", box=box.SQUARE)
    table.add_column(" ", justify="center")
    for col in range(board.size):
        table.add_column(str(col+1), justify="center")
    for i, row in enumerate(board.grid):
        row_cells = [str(i+1)]
        for j, cell in enumerate(row):
            style = ""
            if win_seq and (i, j) in win_seq:
                style = "on yellow bold"
            elif highlight and (i, j) == highlight:
                style = "on green bold"
            elif cell == 'X':
                style = "bold blue"
            elif cell == 'O':
                style = "bold red"
            if show_index and cell == board.EMPTY:
                idx = i * board.size + j + 1
                content = f"[dim]{idx}[/dim]"
            else:
                content = cell if cell != board.EMPTY else ' '
            if style:
                row_cells.append(f"[{style}]{content}[/{style}]")
            else:
                row_cells.append(f"{content}")
        table.add_row(*row_cells)
    console.print(table)

def show_status(game, timer=None):
    status = f"[bold blue]Người chơi (X): {game.scores['X']}[/bold blue] | [bold red]AI (O): {game.scores['O']}[/bold red] | [green]Lượt: {game.current_player}[/green] | [magenta]Số nước đi: {game.move_count}[/magenta]"
    if timer is not None:
        status += f" | [yellow]Thời gian: {timer:.1f}s[/yellow]"
    console.print(Panel(status, title="[bold]Trạng thái trận đấu[/bold]", expand=False))

def get_player_move(board):
    while True:
        move = console.input("[bold blue]Nhập số ô muốn đánh (u=undo, r=redo, q=quit): [/bold blue]")
        if move.lower() in ["q", "quit", "exit"]:
            return 'quit'
        if move.lower() == 'u':
            return 'undo'
        if move.lower() == 'r':
            return 'redo'
        try:
            idx = int(move)
            if 1 <= idx <= board.size * board.size:
                row = (idx - 1) // board.size
                col = (idx - 1) % board.size
                return row, col
            else:
                console.print("[bold yellow]Số ô không hợp lệ, hãy thử lại![/bold yellow]")
        except Exception:
            console.print("[bold yellow]Định dạng không hợp lệ, hãy nhập lại![/bold yellow]")
