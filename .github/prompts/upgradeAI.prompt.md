Here's an enhanced, structured prompt for improving a console-based Tic-tac-toe (Caro) game:

# Technical Requirements for Enhanced Console Caro Game

## AI Intelligence Improvements
- Implement advanced minimax algorithm with:
  - State evaluation heuristics considering:
    - Count of open-ended sequences (1-4 pieces)
    - Weighted scoring based on WIN_CONDITION proximity
  - Iterative deepening with configurable time limits
  - Transposition table for move caching
  - Optional: Monte Carlo Tree Search (MCTS) implementation

## UI/UX Requirements
- Visual enhancements:
    - Square grid representation using Rich library
    - Highlight last move with distinct color/formatting
    - Mark winning sequence upon game completion
    - Display move timer for each turn
- Controls:
  - Implement difficulty selection (Easy/Medium/Hard)
  - Add WASD + Enter keyboard navigation
  - Support coordinate input (row,column)

## Game Mechanics
- Game state management:
  - Undo/redo functionality (`u`/`r` commands)
  - Move history logging to file
- Customization options:
  - Configurable board size (10x10 default, 15x15 optional)
  - Adjustable win condition
- Edge case handling:
  - Simultaneous win detection protocol
  - Draw condition logic

## Technical Architecture
- Modular structure:
  ```
  src/
  ├── ai.py         # AI logic, minimax, heuristics
  ├── ui.py         # Display, input handling
  ├── game.py       # Game mechanics, state management
  ├── board.py      # Board representation
  └── main.py       # Application entry point
  ```
- Testing requirements:
  - Unit tests for core game logic
  - AI evaluation function tests
  - Move validation tests

## Performance Optimization
- Implement smart move generation within 2-3 cell radius
- Asynchronous AI computation with progress indication
- Command-line configuration support for:
  - Board size (--size)
  - Win condition (--win)
  - AI depth (--depth)
  - Time limits (--time)

Expected output: A modular, testable, and maintainable console Caro game with enhanced AI capabilities and improved user experience.
