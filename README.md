# Snake Game

A classic Snake game implemented in Python using the standard-library `turtle`
graphics module. Built as a small project to practice clean object-oriented
design, event-driven input handling, and persistent local state — with no
third-party dependencies.

## Features

- **Object-oriented architecture** — `Snake`, `Food`, `Scoreboard`, and `Game`
  classes with clear responsibilities, instead of a single-script global-state
  loop.
- **Persistent high score** — automatically saved to
  `~/.snake_high_score.json` and reloaded across sessions.
- **Grid-aligned movement and food spawning** — food never appears between
  cells, and the spawn routine retries to avoid placing food on the snake.
- **Adaptive difficulty** — the game speeds up each time food is eaten, with a
  floor that keeps it playable.
- **Pause and quit controls** — pause anytime with `P`, exit cleanly with `Q`.
- **Anti-reverse input handling** — opposite-direction key presses are ignored
  so the snake can't fold back into itself in a single step.
- **Graceful shutdown** — handles window-close (`turtle.Terminator`) without a
  crash and persists the high score on exit.

## Tech Stack

- **Language:** Python 3.9+
- **Graphics:** `turtle` (standard library)
- **Persistence:** JSON file in the user's home directory

## Getting Started

### Prerequisites

- Python 3.9 or newer. `turtle` ships with the standard library, so on most
  systems no additional install is required. On some Linux distributions you
  may need the Tk bindings:

  ```bash
  sudo apt-get install python3-tk   # Debian/Ubuntu
  ```

### Run

```bash
git clone https://github.com/<your-username>/Python-snake-game.git
cd Python-snake-game
python3 snake_game.py
```

## Controls

| Key            | Action          |
| -------------- | --------------- |
| `W` / `↑`      | Move up         |
| `S` / `↓`      | Move down       |
| `A` / `←`      | Move left       |
| `D` / `→`      | Move right      |
| `P`            | Pause / resume  |
| `Q`            | Quit            |

## Project Structure

```
Python-snake-game/
├── snake_game.py      # Game entrypoint and all game classes
├── requirements.txt   # (Empty — stdlib only; kept for tooling compatibility)
├── .gitignore
└── README.md
```

The single-module layout reflects the project's size; the code is organized
into self-contained classes that could be split into a package if the game
grew (e.g. multiple levels, sound, sprites).

## Design Notes

- **Why turtle?** It's part of the standard library, runs everywhere Python
  does, and demonstrates that polished projects don't always need a heavy
  framework.
- **Why a JSON file for the high score?** A plain text file would have worked,
  but JSON keeps the format extensible (e.g. adding per-mode scores later)
  with no extra code.
- **Why guard `Food.respawn` with a retry loop?** Random placement can land on
  the snake's body. A small bounded retry keeps the spawn logic O(1) on
  average without ever blocking the game loop.

## Future Improvements

- Optional walls / obstacles mode
- Sound effects (would require an external library such as `pygame.mixer`)
- Configurable themes via a small JSON config
- Unit tests for the pure game-state logic (collision checks, direction
  guard, scoring)

## Author

**Rushikesh Pawar** — pawar.rush@northeastern.edu

## License

MIT — see `LICENSE` if/when added.
