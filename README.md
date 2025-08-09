# AI-Karo (Caro / Gomoku) – Textual UI

Trò chơi Caro (Gomoku) hiện đại trên terminal với Textual: click chuột để đánh, giao diện tối giản, Undo/Redo/New/Quit, AI đối kháng, và lưới bàn cờ rõ ràng giúp quan sát đường chéo tốt hơn.

## Tính năng

- Bàn cờ kích thước tuỳ chỉnh (mặc định 10x10), thắng với 5 quân liên tiếp.
- Giao diện Textual: thanh công cụ Undo/Redo/New/Quit, tiêu đề “Caro (Gomoku)” ở đầu.
- Đặt quân bằng chuột: click vào ô để đánh; phím tắt U/R/N/Q.
- Nước đi gần nhất được highlight nhẹ; chuỗi thắng tô vàng.
- Quân người: x đỏ; quân AI: o xanh.
- Lưới bàn cờ mô phỏng bằng giao điểm “┼” và viền ô, giúp nhìn rõ nước chéo.

## Cài đặt

- Yêu cầu Python >= 3.10 và [uv](https://github.com/astral-sh/uv)
- Phụ thuộc: `textual` (Rich đã được gỡ bỏ)

## Chạy game

```bash
uv run main.py [--size N] [--win K] [--difficulty easy|medium|hard]
```

Nếu không dùng uv, có thể:

```bash
python3 main.py [--size N] [--win K] [--difficulty easy|medium|hard]
```

Lưu ý import: script `main.py` tự thêm thư mục `src` vào `sys.path`, nên chỉ cần chạy ở thư mục gốc repo.

### Tham số

- `--size N`  : Kích thước bàn cờ (mặc định 10)
- `--win K`   : Số quân liên tiếp để thắng (mặc định 5)
- `--difficulty` : Độ khó AI (`easy`, `medium`, `hard`)

## Điều khiển

- Click chuột vào ô để đánh
- U: Undo • R: Redo • N: Ván mới • Q: Thoát

## Cấu trúc dự án

```text
src/
  ai.py        # AI logic
  board.py     # Board representation
  game.py      # Game state, undo/redo
  ui.py        # Giao diện Textual (chính)
main.py        # Điểm khởi động – thêm src vào sys.path và chạy Textual UI
```

## Góp ý & mở rộng

- Có thể tăng độ đậm của lưới, kích thước ô, hiệu ứng chuyển lượt, modal cấu hình trong app.
- PR và góp ý luôn được chào đón!

## Giấy phép

MIT License
