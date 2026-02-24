PRAGMA foreign_keys = ON;

BEGIN;

-- =====================================================
-- PLAYERS
-- =====================================================
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,                    
    first_name TEXT NOT NULL,
    surname TEXT NOT NULL,
    rating TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Prevent exact duplicate full names (optional)
CREATE UNIQUE INDEX IF NOT EXISTS ux_players_full_name
ON players(first_name, surname);


-- =====================================================
-- SESSIONS (one club night)
-- =====================================================
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    courts INTEGER NOT NULL CHECK(courts >= 0)
);


-- =====================================================
-- MATCHES
-- =====================================================
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    court_no INTEGER NOT NULL,
    format TEXT NOT NULL CHECK(format IN ('singles','doubles')),
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    score_a INTEGER,
    score_b INTEGER,
    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_matches_session
ON matches(session_id);


-- =====================================================
-- MATCH PLAYERS (who played + which team)
-- =====================================================
CREATE TABLE IF NOT EXISTS match_players (
    match_id INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    team TEXT NOT NULL CHECK(team IN ('A','B')),
    PRIMARY KEY (match_id, player_id),
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE,
    FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_match_players_player
ON match_players(player_id);

COMMIT;