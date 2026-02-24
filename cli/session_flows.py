from __future__ import annotations

from dataclasses import dataclass, field
import random

from core.player import PlayerRegistry
from engine.matchmaking import Match
from cli.prompts import prompt_choice, prompt_int
from cli.registry_flows import print_players, player_label
from cli.display import print_courts_as_board


# -----------------------------
# Session State (court-based)
# -----------------------------

@dataclass
class SessionState:
    attendee_ids: set[str] = field(default_factory=set)
    phase: str = "lobby"
    fmt: str = "d"  # "d" doubles, "s" singles
    courts: int = 1
    seed: int | None = None

    court_matches: list[Match] = field(default_factory=list)              
    court_player_ids: list[tuple[str, ...]] = field(default_factory=list)
    waiting_ids: list[str] = field(default_factory=list) 
    paused_ids: set[str] = field(default_factory=set)
    games_played: dict[str, int] = field(default_factory=dict)
    rng: random.Random = field(default_factory=random.Random)


# -----------------------------
# Helpers
# -----------------------------

def _display_name(p: dict) -> str:
    first = p.get("first_name")
    surname = p.get("surname")
    if isinstance(first, str) and isinstance(surname, str):
        full = f"{first.strip()} {surname.strip()}".strip()
        if full:
            return full

    pid = p.get("id")
    return str(pid) if pid is not None else "?"


def _choose_players_from_db(registry: PlayerRegistry) -> list[dict]:
    """Enter one or more player IDs (comma/space separated). Returns found player dicts."""
    raw = input("\nEnter player ID(s) to add (comma/space separated, blank to cancel): ").strip()
    if not raw:
        return []

    ids = [x.strip() for x in raw.replace(",", " ").split() if x.strip()]

    chosen: list[dict] = []
    for pid in ids:
        rows = registry.get_player(player_id=pid)
        if not rows:
            print(f"No player found with id '{pid}'. Skipping.")
            continue
        chosen.append(rows[0])

    return chosen


def _get_attendees(registry: PlayerRegistry, state: SessionState) -> list[dict]:
    attendees: list[dict] = []
    for pid in sorted(state.attendee_ids):
        rows = registry.get_player(player_id=pid)
        if rows:
            attendees.append(rows[0])
    return attendees


def _empty_match(fmt: str) -> Match:
    if fmt == "d":
        return Match(format="doubles", team1=("—", "—"), team2=("—", "—"))
    return Match(format="singles", team1=("—",), team2=("—",))


def _pick_next_players(state: SessionState, needed: int) -> list[str]:
    """Pick the next N player IDs from waiting, prioritising those with fewer games played."""
    if len(state.waiting_ids) < needed:
        return []

    scored: list[tuple[int, float, str]] = []
    for pid in state.waiting_ids:
        gp = state.games_played.get(pid, 0)
        scored.append((gp, state.rng.random(), pid))

    scored.sort(key=lambda t: (t[0], t[1]))
    picked = [pid for _, _, pid in scored[:needed]]

    picked_set = set(picked)
    state.waiting_ids = [pid for pid in state.waiting_ids if pid not in picked_set]

    return picked


def _make_match_for_ids(
    registry: PlayerRegistry,
    fmt: str,
    ids: list[str],
    rng: random.Random,
) -> tuple[Match, tuple[str, ...]]:
    """Create a Match for display + return the exact IDs used."""

    # Build display names
    name_map: dict[str, str] = {}
    for pid in ids:
        rows = registry.get_player(player_id=pid)
        name_map[pid] = _display_name(rows[0]) if rows else pid

    ids_shuffled = ids[:]
    rng.shuffle(ids_shuffled)

    if fmt == "d":
        a, b, c, d = ids_shuffled
        m = Match(format="doubles", team1=(name_map[a], name_map[b]), team2=(name_map[c], name_map[d]))
        return m, (a, b, c, d)

    a, b = ids_shuffled
    m = Match(format="singles", team1=(name_map[a],), team2=(name_map[b],))
    return m, (a, b)


# -----------------------------
# Lobby flows
# -----------------------------

def add_attendee_flow(registry: PlayerRegistry, state: SessionState) -> None:
    database_players = registry.list_players()
    available_players = [p for p in database_players if p.get("id") not in state.attendee_ids]

    if not available_players:
        print("No available players to add.")
        return

    print("\nAvailable players in database:")
    print_players(available_players)

    players = _choose_players_from_db(registry)
    if not players:
        return

    added_any = False
    for player in players:
        pid = player.get("id")
        if not pid:
            continue

        if pid in state.attendee_ids:
            print(f"Already in session: {pid}")
            continue

        state.attendee_ids.add(pid)
        state.games_played.setdefault(pid, 0)  # harmless in lobby too

        # If session is running, join the waiting list (unless paused)
        if state.phase == "running" and pid not in state.paused_ids:
            state.waiting_ids.append(pid)

        print(f"Added to session: {player_label(player)}")
        added_any = True

    if not added_any:
        print("No new attendees were added.")

def show_attendees_flow(registry: PlayerRegistry, state: SessionState) -> None:
    attendees = _get_attendees(registry, state)
    if not attendees:
        print("No attendees yet.")
        return

    print("\nSession attendees:")
    print_players(attendees)


def remove_attendee_flow(registry: PlayerRegistry, state: SessionState) -> None:
    attendees = _get_attendees(registry, state)
    if not attendees:
        print("No attendees to remove.")
        return

    print("\nSession attendees:")
    print_players(attendees)

    pid = input("\nEnter attendee ID to remove (or blank to cancel): ").strip()
    if not pid:
        return

    if pid not in state.attendee_ids:
        print("That player is not in the session.")
        return

    if state.phase == "running" and _is_on_court(state, pid):
        print("That player is currently on court. Remove them after their game finishes.")
        return

    state.attendee_ids.discard(pid)
    state.paused_ids.discard(pid)
    state.waiting_ids = [x for x in state.waiting_ids if x != pid]
    state.games_played.pop(pid, None)

    print(f"Removed attendee id '{pid}'.")


def start_session_flow(registry: PlayerRegistry, state: SessionState) -> None:
    if state.phase != "lobby":
        print("Session already started.")
        return

    if not state.attendee_ids:
        print("No attendees. Add attendees first.")
        return

    fmt = prompt_choice("Singles or Doubles? (s/d): ", {"s", "d"})
    courts = prompt_int("How many courts? ", default=1)
    if courts <= 0:
        print("Courts must be at least 1.")
        return

    seed_raw = input("Random seed (optional, press Enter to skip): ").strip()
    seed = int(seed_raw) if seed_raw else None

    # lock in settings
    state.phase = "running"
    state.fmt = fmt
    state.courts = courts
    state.seed = seed
    state.rng = random.Random(seed)

    # init games played
    for pid in state.attendee_ids:
        state.games_played.setdefault(pid, 0)

    # everyone starts waiting
    state.waiting_ids = [pid for pid in sorted(state.attendee_ids) if pid not in state.paused_ids]
    # allocate courts immediately
    state.court_matches = []
    state.court_player_ids = []

    needed = 4 if fmt == "d" else 2
    for _ in range(courts):
        picked = _pick_next_players(state, needed)
        if not picked:
            state.court_matches.append(_empty_match(fmt))
            state.court_player_ids.append(tuple())
            continue

        match, ids_tuple = _make_match_for_ids(registry, fmt, picked, state.rng)
        state.court_matches.append(match)
        state.court_player_ids.append(ids_tuple)

    print("\nSession started and courts allocated. Use 'Show courts' to view.")


# -----------------------------
# Running flows
# -----------------------------

def show_courts_flow(state: SessionState) -> None:
    if state.phase != "running":
        print("No allocation yet. Start the session first.")
        return

    print_courts_as_board(state.court_matches, state.courts, per_row=2)

    if state.waiting_ids:
        parts: list[str] = []
        for pid in state.waiting_ids:
            gp = state.games_played.get(pid, 0)
            parts.append(f"{pid}({gp})")
        print("Waiting/Bench:", ", ".join(parts))


def complete_court_flow(registry: PlayerRegistry, state: SessionState) -> None:
    if state.phase != "running":
        print("Session not running.")
        return

    court_no = prompt_int("Which court finished? (number): ", default=0)
    if court_no <= 0 or court_no > state.courts:
        print("Invalid court number.")
        return

    idx = court_no - 1
    ids_on_court = state.court_player_ids[idx]
    if not ids_on_court:
        print("That court has no match allocated.")
        return

    # update fairness stats and send them to the back of the waiting list
    for pid in ids_on_court:
        state.games_played[pid] = state.games_played.get(pid, 0) + 1
        if pid not in state.paused_ids:
            state.waiting_ids.append(pid)

    # refill this court
    needed = 4 if state.fmt == "d" else 2
    picked = _pick_next_players(state, needed)
    if not picked:
        state.court_matches[idx] = _empty_match(state.fmt)
        state.court_player_ids[idx] = tuple()
        print("Not enough waiting players to refill that court right now.")
        return

    match, ids_tuple = _make_match_for_ids(registry, state.fmt, picked, state.rng)
    state.court_matches[idx] = match
    state.court_player_ids[idx] = ids_tuple

    print(f"Court {court_no} updated.")


def show_games_played_flow(registry: PlayerRegistry, state: SessionState) -> None:
    if not state.games_played:
        print("No session stats yet.")
        return

    rows: list[tuple[int, str, str]] = []
    for pid, gp in state.games_played.items():
        players = registry.get_player(player_id=pid)
        name = _display_name(players[0]) if players else pid
        rows.append((gp, pid, name))

    rows.sort(key=lambda t: (t[0], t[2]))

    print("\nGames played:")
    for gp, pid, name in rows:
        print(f"- {name} ({pid}): {gp}")
        
        
def _is_on_court(state: SessionState, pid: str) -> bool:
    for ids_tuple in state.court_player_ids:
        if pid in ids_tuple:
            return True
    return False

def pause_attendee_flow(state: SessionState) -> None:
    pid = input("\nEnter attendee ID to pause (blank to cancel): ").strip()
    if not pid:
        return

    if pid not in state.attendee_ids:
        print("That player is not in the session.")
        return

    if _is_on_court(state, pid):
        print("That player is currently on court. Pause them after their game finishes.")
        return

    state.paused_ids.add(pid)
    state.waiting_ids = [x for x in state.waiting_ids if x != pid]
    print(f"Paused attendee id '{pid}'.")
    
def unpause_attendee_flow(state: SessionState) -> None:
    pid = input("\nEnter attendee ID to unpause (blank to cancel): ").strip()
    if not pid:
        return

    if pid not in state.attendee_ids:
        print("That player is not in the session.")
        return

    if pid not in state.paused_ids:
        print("That player is not paused.")
        return

    state.paused_ids.discard(pid)

    if state.phase == "running":
        state.waiting_ids.append(pid)

    print(f"Unpaused attendee id '{pid}'.")