# UI and input handling for Caro game using Rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.align import Align
from rich.theme import Theme
from rich.console import Group
import os
import time

# Theme and Console
THEME = Theme({
    "title": "bold white on blue",
    "subtitle": "bold white on dark_blue",
    "player_x": "bold bright_cyan",
    "player_o": "bold bright_red",
    "status": "bold",
    "hint": "dim",
    "warn": "bold yellow",
    "ok": "bold green",
    "error": "bold red",
})

console = Console(theme=THEME)


def _get_box_style() -> box.Box:
    # Allow ASCII fallback via env var
    if os.environ.get("ASCII_BOX", "0") in ("1", "true", "True"):
        return box.ASCII2
    return box.SQUARE


def build_board_table(board, highlight=None, win_seq=None, show_index=False) -> Table:
    table = Table(show_header=True, header_style="bold magenta", box=_get_box_style(), pad_edge=False)
    table.add_column(" ", justify="center", style="bold")
    for col in range(board.size):
        table.add_column(str(col + 1), justify="center")

    for i, row in enumerate(board.grid):
        row_cells = [f"[bold]{i + 1}[/bold]"]
        for j, cell in enumerate(row):
            style = ""
            if win_seq and (i, j) in win_seq:
                style = "on yellow bold"
            elif highlight and (i, j) == highlight:
                style = "on green bold"
            elif cell == 'X':
                style = "player_x"
            elif cell == 'O':
                style = "player_o"

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
    return table


def render_status_panel(game, timer=None) -> Panel:
    status_text = (
        f"[player_x]Người chơi (X): {game.scores['X']}[/player_x]  "
        f"| [player_o]AI (O): {game.scores['O']}[/player_o]  "
        f"| [green]Lượt: {game.current_player}[/green]  "
        f"| [magenta]Số nước đi: {game.move_count}[/magenta]"
    )
    if timer is not None:
        status_text += f"  | [yellow]Thời gian AI: {timer:.1f}s[/yellow]"
    return Panel(status_text, title="[bold]Trạng thái[/bold]", expand=True, box=_get_box_style())


def render_help_panel() -> Panel:
    help_text = Text()
    help_text.append("Điều khiển\n", style="bold")
    help_text.append("- Nhập số ô trống để đánh (ví dụ 37)\n")
    help_text.append("- u: Undo | r: Redo | q: Thoát\n")
    help_text.append("\nGợi ý\n", style="bold")
    help_text.append("- Số mờ là các ô trống có thể đánh\n", style="hint")
    help_text.append("- Ô xanh: nước đi cuối | Ô vàng: chuỗi thắng\n", style="hint")
    return Panel(help_text, title="[bold]Trợ giúp[/bold]", expand=True, box=_get_box_style())


def render_header(title: str = "Caro (Gomoku)") -> Panel:
    header = Align.center(Text(title, style="title"))
    return Panel(header, box=_get_box_style(), padding=(0, 1))


def render_footer(prompt_hint: str = "Nhập số ô (u=undo, r=redo, q=quit) và nhấn Enter") -> Panel:
    return Panel(Text(prompt_hint, style="hint"), box=_get_box_style())


def draw_screen(game, difficulty: str | None = None, thinking: bool = False, timer: float | None = None, show_index: bool = True):
    """Render a complete screen with header/main/sidebar/footer in one go."""
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )
    layout["body"].split_row(
        Layout(name="main", ratio=3),
        Layout(name="sidebar", size=34),
    )

    # Header
    subtitle = f"Kích thước: {game.size}x{game.size} | Thắng: {game.win_condition}"
    if difficulty:
        subtitle += f" | Độ khó: {difficulty}"
    header_group = Group(
        Align.center(Text("Caro (Gomoku)", style="title")),
        Align.center(Text(subtitle, style="subtitle")),
    )
    layout["header"].update(Panel(header_group, box=_get_box_style()))

    # Main board area
    board_table = build_board_table(
        game.board,
        highlight=game.board.last_move,
        win_seq=game.get_winning_sequence(),
        show_index=show_index,
    )
    main_group = [board_table]
    if thinking:
        main_group.append(Align.center(Text("AI đang suy nghĩ…", style="warn")))
    layout["main"].update(Group(*main_group))

    # Sidebar with status + help
    sidebar = Group(
        render_status_panel(game, timer=timer),
        render_help_panel(),
    )
    layout["sidebar"].update(sidebar)

    # Footer
    layout["footer"].update(render_footer())

    console.print(layout)


# Backwards-compatible functions kept below

def print_board(board, highlight=None, win_seq=None, show_index=False):
    table = build_board_table(board, highlight=highlight, win_seq=win_seq, show_index=show_index)
    console.print(table)


def show_status(game, timer=None):
    console.print(render_status_panel(game, timer=timer))


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
                console.print("[warn]Số ô không hợp lệ, hãy thử lại![/warn]")
        except Exception:
            console.print("[warn]Định dạng không hợp lệ, hãy nhập lại![/warn]")
