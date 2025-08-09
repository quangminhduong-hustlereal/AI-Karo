from __future__ import annotations

import asyncio
from typing import Optional, Any

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, DataTable, Button
from textual.containers import Horizontal, Vertical, Container

from .game import Game
from .ai import CaroAI


class HeaderBar(Static):
    def __init__(self, title: str, subtitle: str) -> None:
        super().__init__(expand=True)
        self.title_text = title
        self.subtitle_text = subtitle

    def on_mount(self) -> None:
        self.update(self._render_content())

    def set_subtitle(self, subtitle: str) -> None:
        self.subtitle_text = subtitle
        self.update(self._render_content())

    def _render_content(self) -> str:
        return (
            f"[b] {self.title_text} [/b]\n"
            f"[dim]{self.subtitle_text}[/dim]"
        )


class InfoPanel(Static):
    def set_text(self, text: str) -> None:
        self.update(text)


class CaroApp(App):
    CSS = """
    Screen {
        layout: vertical;
        background: #0b0f17;
        color: #cbd5e1;
    }

    .accent { color: #80d0ff; }
    .muted { color: #64748b; }
    .good { color: #22c55e; }
    .warn { color: #f59e0b; }
    .bad { color: #ef4444; }

    #header {
        padding: 1 2;
        border-bottom: solid #1f2937;
    }

    #main {
        height: 1fr;
    }

    #left, #right {
        height: 1fr;
    }

    #left {
        width: auto;
    padding: 1 2;
    content-align: left top;
    }

    #right {
    width: 36;
        padding: 1 1 1 0;
        border-left: solid #1f2937;
    overflow: auto;
    }

    .panel {
        border: tall #1f2937;
        padding: 1;
        margin: 0 0 1 0;
    }

    .panel-title { color: #94a3b8; }

    .toolbar { height: auto; padding: 1 0; }
    DataTable {
        width: auto;
    }
    Button {
        background: #111827;
        border: tall #334155;
        color: #cbd5e1;
    }
    Button.-primary {
        background: #0ea5e9;
        color: black;
        border: tall #38bdf8;
    }
    Button.-danger {
        background: #ef4444;
        color: black;
        border: tall #f97316;
    }

    /* Size hint bar shown when terminal is too small */
    #size-hint {
        dock: top;
        height: auto;
        padding: 1 2;
        background: #7f1d1d;
        color: #fff;
        border: tall #ef4444;
    }
    """

    BINDINGS = [
        ("q", "quit", "Thoát"),
        ("u", "undo", "Hoàn tác"),
        ("r", "redo", "Làm lại"),
        ("n", "new", "Ván mới"),
    ]

    game: Game
    ai: CaroAI

    current_player: reactive[str] = reactive("X")
    thinking: reactive[bool] = reactive(False)
    size_ok: reactive[bool] = reactive(True)

    def __init__(self, size: int, win_condition: int, difficulty: str) -> None:
        super().__init__()
        self.game = Game(size=size, win_condition=win_condition)
        self.ai = CaroAI(player='O', opponent='X')
        self.difficulty = difficulty

        # UI element placeholders (initialized in compose)
        self.header = None  # type: ignore[assignment]
        self.board_table = None  # type: ignore[assignment]
        self.status_panel = None  # type: ignore[assignment]
        self.help_panel = None  # type: ignore[assignment]
        self.message_panel = None  # type: ignore[assignment]
        self.size_hint = None  # type: ignore[assignment]

        # DataTable key caches
        self.row_keys = []
        self.col_keys = []  # includes the first label column at index 0
        self.row_index_by_key = {}
        self.col_index_by_key = {}
        self.label_col_key = None

    def compose(self) -> ComposeResult:
        self.header = HeaderBar(
            title="Caro (Gomoku)",
            subtitle=f"Kích thước: {self.game.size}x{self.game.size} | Thắng: {self.game.win_condition} | Độ khó: {self.difficulty}",
        )
        self.header.id = "header"

        # Main area with board and sidebar
        self.board_table = DataTable(zebra_stripes=False, cursor_type="cell")
        self.board_table.styles.border = ("solid", "#334155")
        self.board_table.styles.background = "#0b0f17"

        # Left column: Board, Message, Toolbar
        self.message_panel = InfoPanel(classes="panel")
        left = Container(
            Vertical(
                self.board_table,
                Static("[b]Thông báo[/b]", classes="panel-title"),
                self.message_panel,
                Horizontal(
                    Button("↩ Hoàn tác (U)", id="btn-undo"),
                    Button("↪ Làm lại (R)", id="btn-redo"),
                    Button("⎌ Ván mới (N)", id="btn-new", classes="-primary"),
                    Button("⏻ Thoát (Q)", id="btn-quit", classes="-danger"),
                    classes="toolbar",
                    id="toolbar",
                ),
            ),
            id="left",
        )

        # Right column: Status & Help
        self.status_panel = InfoPanel(classes="panel")
        self.help_panel = InfoPanel(classes="panel")
        right = Container(
            Vertical(
                Static("[b]Trạng thái[/b]", classes="panel-title"), self.status_panel,
                Static("[b]Trợ giúp[/b]", classes="panel-title"), self.help_panel,
                id="right-inner"
            ), id="right"
        )

        main = Horizontal(left, right, id="main")

        yield self.header
        yield main
        # Size hint overlay bar (initially hidden)
        self.size_hint = Static("", id="size-hint")
        self.size_hint.styles.display = "none"
        yield self.size_hint

    async def on_mount(self) -> None:
        self._setup_board()
        # Ensure the board doesn't stretch to fill horizontally
        self.board_table.styles.width = "auto"
        self._update_sidebars()
        self._update_message("[dim]Sẵn sàng. Lượt của bạn (X).[/dim]")
        self.set_focus(self.board_table)
        # Apply responsive tweaks and show size hint if needed
        self._apply_responsive_layout()
        self._update_size_hint()

    def on_resize(self, event) -> None:
        # Update layout and size hint when terminal size changes
        self._apply_responsive_layout()
        self._update_size_hint()

    def _setup_board(self) -> None:
        self.board_table.clear(columns=True)
        self.row_keys = []
        self.col_keys = []
        self.row_index_by_key = {}
        self.col_index_by_key = {}
        self.label_col_key = None
        # First column header blank, others 1..N
        blank_key = self.board_table.add_column(" ")
        self.col_keys.append(blank_key)
        self.label_col_key = blank_key
        for c in range(self.game.size):
            col_key = self.board_table.add_column(str(c + 1), width=3)
            self.col_keys.append(col_key)
            self.col_index_by_key[col_key] = c
        # Add rows
        for r in range(self.game.size):
            row_data = [f"[b]{r + 1}[/b]"]
            for c in range(self.game.size):
                row_data.append(self._cell_display(r, c, show_index=False))
            row_key = self.board_table.add_row(*row_data)
            self.row_keys.append(row_key)
            self.row_index_by_key[row_key] = r

    def _cell_content(self, r: int, c: int, show_index: bool = True) -> str:
        cell = self.game.board.grid[r][c]
        if cell != self.game.board.EMPTY:
            # Base rendering: human 'x' red, AI 'o' cyan
            return "[red]x[/red]" if cell == "X" else "[cyan]o[/cyan]"
        # Draw lattice intersection for empty cells to create a visible grid
        return "[dim]┼[/dim]"

    def _cell_display(self, r: int, c: int, show_index: bool = True) -> str:
        cell_val = self.game.board.grid[r][c]
        content = self._cell_content(r, c, show_index=show_index)
        win_seq = self.game.get_winning_sequence()
        if win_seq and (r, c) in win_seq:
            return f"[on #fde68a bold]{content}[/]"
        if self.game.board.last_move and (r, c) == self.game.board.last_move and cell_val != self.game.board.EMPTY:
            # Revert to full-cell background highlight for last move
            return f"[on #1f2937]{content}[/]"
        return content

    def _refresh_board(self) -> None:
        for r, row_key in enumerate(self.row_keys):
            for c in range(self.game.size):
                col_key = self.col_keys[c + 1]
                self.board_table.update_cell(row_key, col_key, self._cell_display(r, c, show_index=False))

    def _apply_responsive_layout(self) -> None:
        """Adjust widths based on current terminal size and center the board."""
        try:
            width, height = self.size.width, self.size.height  # type: ignore[attr-defined]
        except Exception:
            return

        # Sidebar width scales a bit with terminal width
        right = self.query_one("#right")
        if width < 96:
            right.styles.width = 26
        elif width < 120:
            right.styles.width = 32
        else:
            right.styles.width = 36

        # Keep board at content-size
        self.board_table.styles.width = "auto"

    def _update_sidebars(self, ai_time: Optional[float] = None) -> None:
        status = (
            f"[accent]Người chơi (X): {self.game.scores['X']}[/accent]\n"
            f"[accent]AI (O): {self.game.scores['O']}[/accent]\n"
            f"Lượt: [b]{self.game.current_player}[/b]  |  "
            f"Số nước đi: {self.game.move_count}"
        )
        if ai_time is not None:
            status += f"\n[warn]Thời gian AI: {ai_time:.1f}s[/warn]"
        self.status_panel.set_text(status)

        self.help_panel.set_text(
            "Nhấp chuột vào ô để đánh.\n"
            "Phím tắt: U = Hoàn tác, R = Làm lại, N = Ván mới, Q = Thoát.\n"
            "Nút nhanh ở dưới cùng. Ô mờ: ô trống (giao điểm) | Ô vàng: chuỗi thắng"
        )

    def _update_message(self, text: str) -> None:
        self.message_panel.set_text(text)

    def _update_size_hint(self) -> None:
        """Show or hide the size hint depending on terminal size."""
        try:
            width, height = self.size.width, self.size.height  # type: ignore[attr-defined]
        except Exception:
            return
        # Minimal size to show board, message and toolbar on left, and status/help on right
        MIN_COLS = 100
        MIN_ROWS = 28
        ok = width >= MIN_COLS and height >= MIN_ROWS
        self.size_ok = ok
        if ok:
            self.size_hint.styles.display = "none"
        else:
            self.size_hint.update(
                f"Màn hình terminal quá nhỏ. Hãy mở rộng tới tối thiểu [b]{MIN_COLS}x{MIN_ROWS}[/b]. "
                f"Hiện tại: {width}x{height}."
            )
            self.size_hint.styles.display = "block"

    def action_quit(self) -> None:
        self.exit()

    async def action_undo(self) -> None:
        if self.thinking or self.game.finished:
            return
        if self.game.undo():
            self._refresh_board()
            self._update_sidebars()
            self._update_message("[dim]Đã hoàn tác.[/dim]")

    async def action_redo(self) -> None:
        if self.thinking or self.game.finished:
            return
        if self.game.redo():
            self._refresh_board()
            self._update_sidebars()
            self._update_message("[dim]Đã làm lại.[/dim]")
        else:
            self._update_message("[warn]Không có nước để làm lại.[/warn]")

    async def action_new(self) -> None:
        if self.thinking:
            return
        self.game.reset()
        self._refresh_board()
        self._update_sidebars()
        self._update_message("[dim]Ván mới. Lượt của bạn (X).[/dim]")
        self.set_focus(self.board_table)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "btn-undo":
            asyncio.create_task(self.action_undo())
        elif bid == "btn-redo":
            asyncio.create_task(self.action_redo())
        elif bid == "btn-new":
            asyncio.create_task(self.action_new())
        elif bid == "btn-quit":
            self.action_quit()

    async def _handle_player_move(self, row: int, col: int) -> None:
        try:
            if self.game.current_player != 'X':
                return
            if not self.game.make_move(row, col):
                self._update_message("[warn]Nước đi không hợp lệ, hãy thử lại![/warn]")
                return
            self._refresh_board()
            self._update_sidebars()
            if self._maybe_finish():
                return
            await self._ai_turn()
        except Exception as e:
            self._update_message(f"[bad]Lỗi khi xử lý nước đi: {type(e).__name__}: {e}[/bad]")

    def _maybe_finish(self) -> bool:
        if self.game.finished:
            self._refresh_board()
            if self.game.winner:
                if self.game.winner == 'X':
                    self._update_message("[good]Bạn đã thắng![/good]")
                else:
                    self._update_message("[bad]AI đã thắng![/bad]")
            else:
                self._update_message("[warn]Hòa! Không còn nước đi.[/warn]")
            return True
        return False

    async def _ai_turn(self) -> None:
        try:
            self.thinking = True
            self._update_message("[accent]AI đang suy nghĩ…[/accent]")
            self._update_sidebars()
            loop = asyncio.get_event_loop()
            t0 = loop.time()
            row, col = await asyncio.to_thread(
                self.ai.get_move, self.game.board, self.game.win_condition, self.difficulty
            )
            t1 = loop.time()
            self.game.make_move(row, col)
            self._refresh_board()
            self._update_sidebars(ai_time=(t1 - t0))
            self.thinking = False
            if not self._maybe_finish():
                self.set_focus(self.board_table)
        except Exception as e:
            self.thinking = False
            self._update_message(f"[bad]Lỗi AI: {type(e).__name__}: {e}[/bad]")

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        # Allow clicking on a board cell to play
        if self.thinking or self.game.finished:
            return
        try:
            # Ensure caches are initialized
            if not self.row_keys or not self.col_keys:
                return

            # Prefer keys if available
            row_index: int | None = None
            col_index: int | None = None

            cell_key = getattr(event, "cell_key", None)
            if cell_key is not None:
                rk = getattr(cell_key, "row_key", None)
                ck = getattr(cell_key, "column_key", None)
                # Ignore label column
                if self.label_col_key is not None and ck == self.label_col_key:
                    return
                if rk in self.row_index_by_key and ck in self.col_index_by_key:
                    row_index = self.row_index_by_key[rk]
                    col_index = self.col_index_by_key[ck]

            # Fallback: coordinate may be ints or keys
            if row_index is None or col_index is None:
                coord_r, coord_c = event.coordinate
                # Numeric indices
                if isinstance(coord_r, int) and isinstance(coord_c, int):
                    if coord_c == 0:  # label column
                        return
                    row_index = coord_r
                    col_index = coord_c - 1
                else:
                    # Keys directly
                    if self.label_col_key is not None and coord_c == self.label_col_key:
                        return
                    if coord_r in self.row_index_by_key and coord_c in self.col_index_by_key:
                        row_index = self.row_index_by_key[coord_r]
                        col_index = self.col_index_by_key[coord_c]

            if row_index is None or col_index is None:
                return

            # Guard against any out-of-range coordinate
            if not (0 <= row_index < self.game.size and 0 <= col_index < self.game.size):
                return
            await self._handle_player_move(row_index, col_index)
        except Exception as e:
            # Fail safely: show a message instead of crashing
            self._update_message(f"[bad]Lỗi khi chọn ô: {type(e).__name__}: {e}[/bad]")


def run_textual_app(size: int, win_condition: int, difficulty: str) -> None:
    app = CaroApp(size=size, win_condition=win_condition, difficulty=difficulty)
    app.run()
