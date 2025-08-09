from __future__ import annotations

import asyncio
from typing import Optional, Tuple

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, Input, DataTable
from textual.containers import Horizontal, Vertical, Container
from textual import events

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

    #footer {
        padding: 0 2 1 2;
        border-top: solid #1f2937;
    }

    #main {
        height: 1fr;
    }

    #left, #right {
        height: 1fr;
    }

    #left {
        width: 1fr;
        padding: 1 2;
    }

    #right {
        width: 38;
        padding: 1 1 1 0;
        border-left: solid #1f2937;
    }

    .panel {
        border: tall #1f2937;
        padding: 1;
        margin: 0 0 1 0;
    }

    .panel-title { color: #94a3b8; }

    Input {
        width: 100%;
        border: round #334155;
        background: #0f172a;
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

    def __init__(self, size: int, win_condition: int, difficulty: str) -> None:
        super().__init__()
        self.game = Game(size=size, win_condition=win_condition)
        self.ai = CaroAI(player='O', opponent='X')
        self.difficulty = difficulty

        self.header: HeaderBar
        self.board_table: DataTable
        self.status_panel: InfoPanel
        self.moves_panel: InfoPanel
        self.help_panel: InfoPanel
        self.message_panel: InfoPanel
        self.input_box: Input

    def compose(self) -> ComposeResult:
        self.header = HeaderBar(
            title="Caro (Gomoku)",
            subtitle=f"Kích thước: {self.game.size}x{self.game.size} | Thắng: {self.game.win_condition} | Độ khó: {self.difficulty}",
        )
        self.header.id = "header"

        # Main area with board and sidebar
        self.board_table = DataTable(zebra_stripes=False, cursor_type="row")
        left = Container(self.board_table, id="left")

        self.status_panel = InfoPanel(classes="panel")
        self.moves_panel = InfoPanel(classes="panel")
        self.help_panel = InfoPanel(classes="panel")
        self.message_panel = InfoPanel(classes="panel")
        right = Container(
            Vertical(
                Static("[b]Trạng thái[/b]", classes="panel-title"), self.status_panel,
                Static("[b]Lịch sử[/b]", classes="panel-title"), self.moves_panel,
                Static("[b]Trợ giúp[/b]", classes="panel-title"), self.help_panel,
                Static("[b]Thông báo[/b]", classes="panel-title"), self.message_panel,
                id="right-inner"
            ), id="right"
        )

        main = Horizontal(left, right, id="main")

        # Footer
        self.input_box = Input(placeholder="Nhập số ô (u=undo, r=redo, q=quit) rồi Enter…")
        footer = Container(self.input_box, id="footer")

        yield self.header
        yield main
        yield footer

    async def on_mount(self) -> None:
        self._setup_board()
        self._update_sidebars()
        self._update_message("[dim]Sẵn sàng. Lượt của bạn (X).[/dim]")
        self.set_focus(self.input_box)

    def _setup_board(self) -> None:
        self.board_table.clear(columns=True)
        self.board_table.cursor_type = "cell"
        # First column header blank, others 1..N
        self.board_table.add_column(" ")
        for c in range(self.game.size):
            self.board_table.add_column(str(c + 1), width=3)
        # Add rows
        for r in range(self.game.size):
            row_data = [f"[b]{r + 1}[/b]"]
            for c in range(self.game.size):
                row_data.append(self._cell_display(r, c, show_index=True))
            self.board_table.add_row(*row_data)

    def _cell_content(self, r: int, c: int, show_index: bool = True) -> str:
        cell = self.game.board.grid[r][c]
        if cell != self.game.board.EMPTY:
            return "●" if cell == "X" else "○"
        if show_index:
            idx = r * self.game.size + c + 1
            return f"[dim]{idx}[/dim]"
        return " "

    def _cell_display(self, r: int, c: int, show_index: bool = True) -> str:
        content = self._cell_content(r, c, show_index=show_index)
        win_seq = self.game.get_winning_sequence()
        if win_seq and (r, c) in win_seq:
            return f"[on #fde68a bold]{content}[/]"
        if self.game.board.last_move and (r, c) == self.game.board.last_move:
            return f"[on #1f2937 bold]{content}[/]"
        return content

    def _refresh_board(self) -> None:
        for r in range(self.game.size):
            for c in range(self.game.size):
                self.board_table.update_cell(r, c + 1, self._cell_display(r, c, show_index=True))

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

        if self.game.move_history:
            lines = []
            for idx, (r, c, p) in enumerate(self.game.move_history, start=1):
                style = "accent" if p == 'X' else "muted"
                lines.append(f"[{style}]#{idx} {p} @ {r+1},{c+1}[/{style}]")
            self.moves_panel.set_text("\n".join(lines[-12:]))
        else:
            self.moves_panel.set_text("[dim]Chưa có nước đi[/dim]")

        self.help_panel.set_text(
            "Nhập số ô rồi Enter (vd: 37)\n"
            "u: Hoàn tác  |  n: Ván mới  |  q: Thoát\n"
            "Ô mờ: ô trống | Ô xanh: nước cuối | Ô vàng: chuỗi thắng"
        )

    def _update_message(self, text: str) -> None:
        self.message_panel.set_text(text)

    async def action_quit(self) -> None:
        await self.shutdown()

    async def action_undo(self) -> None:
        if self.thinking or self.game.finished:
            return
        if self.game.undo():
            self._refresh_board()
            self._update_sidebars()
            self._update_message("[dim]Đã hoàn tác.[/dim]")

    async def action_redo(self) -> None:
        # Redo placeholder (logic not implemented, remains unchanged)
        if self.thinking or self.game.finished:
            return
        self._update_message("[dim]Redo chưa được hỗ trợ.[/dim]")

    async def action_new(self) -> None:
        if self.thinking:
            return
        self.game.reset()
        self._refresh_board()
        self._update_sidebars()
        self._update_message("[dim]Ván mới. Lượt của bạn (X).[/dim]")
        self.set_focus(self.input_box)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.thinking:
            event.input.value = ""
            return
        text = (event.value or "").strip().lower()
        event.input.value = ""
        if not text:
            return
        if text in {"q", "quit", "exit"}:
            await self.action_quit()
            return
        if text == "u":
            await self.action_undo()
            return
        if text == "r":
            await self.action_redo()
            return
        if text == "n":
            await self.action_new()
            return
        # Try parse move index
        try:
            idx = int(text)
            if 1 <= idx <= self.game.size * self.game.size:
                row = (idx - 1) // self.game.size
                col = (idx - 1) % self.game.size
                await self._handle_player_move(row, col)
            else:
                self._update_message("[warn]Số ô không hợp lệ, hãy thử lại![/warn]")
        except Exception:
            self._update_message("[warn]Định dạng không hợp lệ, hãy nhập lại![/warn]")

    async def _handle_player_move(self, row: int, col: int) -> None:
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
        self.thinking = True
        self._update_message("[accent]AI đang suy nghĩ…[/accent]")
        self._update_sidebars()
        t0 = asyncio.get_event_loop().time()
        row, col = await asyncio.to_thread(self.ai.get_move, self.game.board, self.game.win_condition, self.difficulty)
        t1 = asyncio.get_event_loop().time()
        self.game.make_move(row, col)
        self._refresh_board()
        self._update_sidebars(ai_time=(t1 - t0))
        self.thinking = False
        if not self._maybe_finish():
            self.set_focus(self.input_box)

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        # Allow clicking on a board cell to play
        if self.thinking or self.game.finished:
            return
        r, c = event.coordinate
        if c == 0:
            return
        await self._handle_player_move(r, c - 1)


def run_textual_app(size: int, win_condition: int, difficulty: str) -> None:
    app = CaroApp(size=size, win_condition=win_condition, difficulty=difficulty)
    app.run()