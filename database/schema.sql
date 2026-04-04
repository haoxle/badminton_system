PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ─── PLAYERS ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS players (
    id          TEXT PRIMARY KEY,
    first_name  TEXT NOT NULL,
    surname     TEXT NOT NULL,
    rating      TEXT NOT NULL DEFAULT 'E',
    elo         REAL NOT NULL DEFAULT 1500.0,
    boosted     REAL NOT NULL DEFAULT 1500.0,
    total_games  INTEGER NOT NULL DEFAULT 0,
    total_wins   INTEGER NOT NULL DEFAULT 0,
    total_losses INTEGER NOT NULL DEFAULT 0,
    streak_wins   INTEGER NOT NULL DEFAULT 0,
    streak_losses INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ─── SESSIONS ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id           TEXT PRIMARY KEY, 
    date         TEXT NOT NULL, 
    start_time   TEXT NOT NULL,      
    end_time     TEXT NOT NULL,
    court_count  INTEGER NOT NULL DEFAULT 4,
    format       TEXT NOT NULL DEFAULT 'doubles' CHECK(format IN ('singles','doubles')),
    status       TEXT NOT NULL DEFAULT 'open'   CHECK(status  IN ('open','in_progress','closed')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS signups (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    player_id  TEXT NOT NULL REFERENCES players(id)  ON DELETE CASCADE,
    signed_up_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(session_id, player_id)
);


CREATE TABLE IF NOT EXISTS courts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT    NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    court_number INTEGER NOT NULL,     
    status     TEXT NOT NULL DEFAULT 'idle'
                   CHECK(status IN ('idle','in_progress','finished')),
    UNIQUE(session_id, court_number)
);

CREATE TABLE IF NOT EXISTS matches (
    id          TEXT PRIMARY KEY,   -- UUID
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    court_id    INTEGER NOT NULL REFERENCES courts(id),
    format      TEXT NOT NULL CHECK(format IN ('singles','doubles')),

    team1_ids   TEXT NOT NULL,
    team2_ids   TEXT NOT NULL,

    score_team1 INTEGER,
    score_team2 INTEGER,

    status      TEXT NOT NULL DEFAULT 'pending'
                   CHECK(status IN ('pending','in_progress','completed')),

    started_at   TEXT,
    completed_at TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);


CREATE TABLE IF NOT EXISTS match_players (
    match_id  TEXT    NOT NULL REFERENCES matches(id) ON DELETE CASCADE,
    player_id TEXT    NOT NULL REFERENCES players(id),
    team      INTEGER NOT NULL CHECK(team IN (1,2)),
    PRIMARY KEY (match_id, player_id)
);

CREATE INDEX IF NOT EXISTS idx_match_players_player ON match_players(player_id);
CREATE INDEX IF NOT EXISTS idx_matches_session      ON matches(session_id);
CREATE INDEX IF NOT EXISTS idx_signups_session      ON signups(session_id);
