from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional, Tuple, Iterable

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Header, Footer, Button
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual import events

from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich import box

from .game import Game
from .ai import CaroAI


ACCENT_COLOR = "cyan"


def _piece_symbol(player: str, use_unicode: bool = True) -> str:
    if not player or player.strip() == "":
        return " "
    if use_unicode:
        return "●" if player == "X" else "○"
    return player


def _build_board_table(game: Game, cursor: Tuple[int, int] | None = None, show_index: bool = True) -> Table:
    board = game.board
    table = Table(
        show_header=True,
        header_style="grey50",
        box=box.ROUNDED,
        pad_edge=False,
        show_lines=False,
    )
    table.add_column(" ", justify="center", style="bold")
    for col in range(board.size):
        table.add_column(str(col + 1), justify="center", style="grey50")

    last = board.last_move
    win_seq = set(game.get_winning_sequence() or [])

    for i, row in enumerate(board.grid):
        cells: list[str] = [f"[bold]{i + 1}[/bold]"]
        for j, cell in enumerate(row):
            style = ""
            if (i, j) in win_seq:
                style = "on #FFF3B0 bold"
            elif last and (i, j) == last:
                style = "on #2B3A55 bold"
            elif cell == 'X':
                style = "bold cyan"
            elif cell == 'O':
                style = "bold magenta"

            if show_index and cell == board.EMPTY:
                idx = i * board.size + j + 1
                content = f"[dim]{idx}[/dim]"
            else:
                content = _piece_symbol(cell) if cell != board.EMPTY else ' '

            # Cursor highlight overlay
            if cursor and (i, j) == cursor:
                content = f"[black on {ACCENT_COLOR}]{content}[/]"

            if style:
                cells.append(f"[{style}]{content}[/{style}]")
            else:
                cells.append(f"{content}")
        table.add_row(*cells)
    return table


class BoardWidget(Widget):
    """Board widget that renders the game board and handles user navigation."""

    cursor_row: int = reactive(0)
    cursor_col: int = reactive(0)

    def __init__(self, game: Game, name: Optional[str] = None) -> None:
        super().__init__(name=name)
        self.game = game

    def render(self) -> Table:
        return _build_board_table(self.game, (self.cursor_row, self.cursor_col), show_index=True)

    def on_mount(self) -> None:
        # Ensure cursor starts on a valid empty cell if possible
        if self.game.board.grid[self.cursor_row][self.cursor_col] != self.game.board.EMPTY:
            # Find first empty
            for (r, c) in self.game.board.get_valid_moves():
                self.cursor_row, self.cursor_col = r, c
                break
        self.focus()

    def key_move(self, dr: int, dc: int) -> None:
        size = self.game.board.size
        self.cursor_row = max(0, min(size - 1, self.cursor_row + dr))
        self.cursor_col = max(0, min(size - 1, self.cursor_col + dc))

    async def on_key(self, event: events.Key) -> None:
        key = event.key
        if key in ("up", "w"):
            self.key_move(-1, 0)
            event.stop()
            return
        if key in ("down", "s"):
            self.key_move(1, 0)
            event.stop()
            return
        if key in ("left", "a"):
            self.key_move(0, -1)
            event.stop()
            return
        if key in ("right", "d"):
            self.key_move(0, 1)
            event.stop()
            return
        if key == "enter":
            # Request to place a move at cursor
            await self.post_message(PlaceMove(self, self.cursor_row, self.cursor_col))
            event.stop()
            return
        if key in ("u", "U"):
            await self.post_message(RequestUndo(self))
            event.stop()
            return
        if key in ("r", "R"):
            await self.post_message(RequestRedo(self))
            event.stop()
            return


class PlaceMove(events.Message):
    def __init__(self, sender: Widget, row: int, col: int) -> None:
        self.row = row
        self.col = col
        super().__init__(sender)


class RequestUndo(events.Message):
    pass


class RequestRedo(events.Message):
    pass


class Sidebar(Static):
    def __init__(self, game: Game, difficulty: str) -> None:
        super().__init__()
        self.game = game
        self.difficulty = difficulty

    def render(self) -> Panel:
        # Status
        status = (
            f"[bold cyan]Người chơi (X): {self.game.scores['X']}[/]  "
            f"| [bold magenta]AI (O): {self.game.scores['O']}[/]  "
            f"| [green]Lượt: {self.game.current_player}[/]  "
            f"| [magenta]Số nước đi: {self.game.move_count}[/]"
        )
        # Moves history (last 10)
        if self.game.move_history:
            start = max(0, len(self.game.move_history) - 10)
            lines = []
            for idx, (r, c, p) in enumerate(self.game.move_history[start:], start=start + 1):
                color = "bold cyan" if p == 'X' else "bold magenta"
                lines.append(f"[{color}]#{idx} {p} @ {r+1},{c+1}[/]")
            moves = "\n".join(lines)
        else:
            moves = "[dim]Chưa có nước đi[/dim]"

        help_text = (
            "[bold]Điều khiển[/]\n"
            "- Mũi tên/WASD: Di chuyển\n"
            "- Enter: Đánh\n"
            "- U: Undo | R: Redo | Q: Thoát\n"
        )
        group = Text()
        group.append(status + "\n\n")
        group.append("[bold]Lịch sử[/]\n" + moves + "\n\n")
        group.append("[bold]Trợ giúp[/]\n" + help_text)
        title = f"Kích thước: {self.game.size}x{self.game.size} | Thắng: {self.game.win_condition} | Độ khó: {self.difficulty}"
        return Panel(group, title=title, border_style=ACCENT_COLOR, box=box.ROUNDED)


class CaroApp(App):
    CSS_PATH = "tui.css"

    # Reactive state
    thinking: bool = reactive(False)

    def __init__(self, size: int = 10, win_condition: int = 5, difficulty: str = "medium") -> None:
        super().__init__()
        self.game = Game(size=size, win_condition=win_condition)
        self.ai = CaroAI(player='O', opponent='X')
        self.difficulty = difficulty
        self.board_widget = BoardWidget(self.game)
        self.sidebar = Sidebar(self.game, difficulty)
        self.status_bar = Static()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="body"):
            yield self.board_widget
            with Vertical(id="right"):
                yield self.sidebar
                yield self.status_bar
        yield Footer()

    def on_mount(self) -> None:
        self._update_status("Sẵn sàng. Lượt X.")
        # If AI starts first
        if self.game.current_player == 'O':
            self.call_after_refresh(self._ai_turn)

    def _update_status(self, msg: str) -> None:
        self.status_bar.update(Panel(Text(msg), border_style=ACCENT_COLOR, box=box.ROUNDED))

    async def _ai_turn(self) -> None:
        self.thinking = True
        self._update_status("AI đang suy nghĩ…")
        t0 = asyncio.get_event_loop().time()
        # Run AI in a thread to avoid blocking the UI loop
        row, col = await asyncio.to_thread(self.ai.get_move, self.game.board, self.game.win_condition, self.difficulty)
        t1 = asyncio.get_event_loop().time()
        self.game.make_move(row, col)
        self._update_status(f"AI xong sau {t1 - t0:.1f}s. Lượt {self.game.current_player}.")
        self.thinking = False
        self._check_end_or_continue()
        self.refresh()

    def _check_end_or_continue(self) -> None:
        if self.game.finished:
            if self.game.winner is None:
                msg = "[bold yellow]Hòa! Không còn nước đi.[/]"
            elif self.game.winner == 'X':
                msg = "[bold green]Bạn đã thắng![/]"
            else:
                msg = "[bold red]AI đã thắng![/]"
            self._update_status(msg + "  Nhấn Y để chơi lại, N để thoát.")
        else:
            # If now is AI's turn, trigger AI move
            if self.game.current_player == 'O':
                self.call_after_refresh(self._ai_turn)

    async def handle_place_move(self, message: PlaceMove) -> None:
        if self.thinking or self.game.finished:
            return
        if self.game.current_player != 'X':
            return
        r, c = message.row, message.col
        if not self.game.board.is_valid_move(r, c):
            self._update_status("[yellow]Nước đi không hợp lệ, hãy thử lại![/]")
            return
        self.game.make_move(r, c)
        self._update_status("Đã đặt quân. Đến lượt AI…")
        self.refresh()
        self._check_end_or_continue()

    async def handle_request_undo(self, _: RequestUndo) -> None:
        if self.thinking:
            return
        if self.game.undo():
            self._update_status("Đã undo.")
            self.refresh()

    async def handle_request_redo(self, _: RequestRedo) -> None:
        # Redo placeholder (logic not implemented)
        self._update_status("[dim]Redo chưa khả dụng.[/]")

    async def on_key(self, event: events.Key) -> None:
        if event.key in ("q", "Q"):
            await self.action_quit()
        if self.game.finished:
            if event.key in ("y", "Y"):
                # Restart
                self.game.reset()
                self._update_status("Bắt đầu ván mới. Lượt X.")
                self.refresh()
            elif event.key in ("n", "N"):
                await self.action_quit()


def run_textual(size: int = 10, win: int = 5, difficulty: str = "medium") -> None:
    app = CaroApp(size=size, win_condition=win, difficulty=difficulty)
    app.run()