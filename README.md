# Caro Console Game (Gomoku)

Một trò chơi Caro (Gomoku) console hiện đại, sử dụng Python và thư viện Rich, hỗ trợ Người chơi vs AI với AI thông minh (minimax + heuristic), giao diện đẹp, undo/redo, highlight nước đi, chọn độ khó, và nhiều tính năng mở rộng.

## Tính năng nổi bật
- Bảng 10x10 (hoặc tuỳ chỉnh), thắng với 5 quân liên tiếp
- Giao diện console đẹp với Rich: màu sắc, highlight nước đi cuối, chuỗi thắng
- AI mạnh với minimax, heuristic, transposition table, chọn độ khó
- Undo/redo, nhập nước đi bằng số ô hoặc lệnh
- Chọn kích thước bảng, điều kiện thắng, độ sâu AI qua dòng lệnh
- Hiển thị trạng thái, điểm số, thời gian suy nghĩ của AI

## Cài đặt
Yêu cầu Python >= 3.10 và trình quản lý gói [uv](https://github.com/astral-sh/uv)

```sh
uv pip install rich
```

Nếu môi trường không có pip/uv, có thể cài Rich qua hệ thống (nếu có):

```sh
# Debian/Ubuntu (ví dụ)
sudo apt-get update && sudo apt-get install -y python3-rich
```

Hoặc dùng venv:

```sh
sudo apt-get install -y python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip install rich
```

## Khởi chạy trò chơi
Bạn có thể chạy game với nhiều tuỳ chọn dòng lệnh:

```sh
uv run main.py [--size N] [--win K] [--difficulty easy|medium|hard]
```

Hoặc nếu không có uv:

```sh
python3 main.py [--size N] [--win K] [--difficulty easy|medium|hard]
```

### Các tuỳ chọn dòng lệnh
- `--size N`         : Kích thước bảng (mặc định 10, ví dụ 15 cho 15x15)
- `--win K`          : Số quân liên tiếp để thắng (mặc định 5)
- `--difficulty`     : Độ khó AI (`easy`, `medium`, `hard`)

### Ví dụ lệnh chạy
- Chơi mặc định:
  ```sh
  uv run main.py
  ```
- Chơi bảng 15x15, thắng 5:
  ```sh
  uv run main.py --size 15 --win 5
  ```
- Chơi với AI khó:
  ```sh
  uv run main.py --difficulty hard
  ```

## Các lệnh trong khi chơi
- Nhập **số thứ tự ô** (hiện trên bàn cờ) để đánh vào ô đó (ví dụ: `37`)
- `u` : Undo (quay lại nước trước)
- `r` : Redo (nếu có)
- `q` : Thoát game

## Giao diện & trải nghiệm
- Bàn cờ hiển thị số thứ tự các ô trống, chỉ cần nhập số để đánh
- Highlight nước đi cuối, chuỗi thắng
- Hiển thị trạng thái, điểm số, thời gian AI suy nghĩ
- AI tự động đánh sau lượt người chơi
- Kết thúc ván: chọn chơi lại hoặc thoát
- Có thể bật fallback ASCII cho viền hộp khi terminal không hỗ trợ Unicode: `ASCII_BOX=1 python3 main.py`

## Cấu trúc dự án
```
src/
  ai.py      # AI logic, minimax, heuristic
  board.py   # Board representation
  game.py    # Game state, undo/redo
  ui.py      # Giao diện, nhập xuất
main.py      # Điểm khởi động
```

## Đóng góp & mở rộng
- Có thể mở rộng thêm WASD navigation, logging, async AI, unit test...
- PR và góp ý luôn được chào đón!

## Giấy phép
MIT License
