# Badminton System

A small Python + SQLite project for managing badminton club players and running a club-night **session** with **court allocation**, **bench rotation**, and a simple **terminal UI**.

## What it does

### Player registry (SQLite)
- Register players with:
  - `first_name`
  - `surname`
  - `rating` (grade)
- List players (sorted by surname/first name)
- Basic CRUD support in `core/player.py`

### Session runner (terminal)
- Session **Lobby**
  - Add attendees from the database (by player ID)
  - Show/remove attendees
  - Register a new player mid-session
- Session **Running**
  - Allocate players to courts (singles or doubles)
  - Mark a court finished → players rotate back into the waiting list
  - Track **games played** per attendee (fairness)
  - Pause/unpause attendees (paused players won’t be picked)

### Matchmaking helpers
- `engine/matchmaking.py` can generate random singles/doubles matches and bench players:
  - Doubles: groups of 4 → remainder goes to bench
  - Singles: pairs of 2 → odd one goes to bench

### Terminal court display
- Renders courts as ASCII diagrams side-by-side (`cli/display.py`).

## Setup

python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

SCHEMA_FILE = BASE_DIR / "schema.sql"

python main.py


