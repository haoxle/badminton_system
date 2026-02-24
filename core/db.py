import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "badminton.db"
SCHEMA_FILE = BASE_DIR / "schema.sql"

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_db_connection() as conn:
        conn.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        conn.commit()