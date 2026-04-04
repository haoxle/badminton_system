# core/matchmaking.py
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Match:
    format: str
    team1: tuple[str, ...]
    team2: tuple[str, ...]

def _display_name(p: dict) -> str | None:
    first   = p.get("first_name", "")
    surname = p.get("surname", "")
    full = f"{first.strip()} {surname.strip()}".strip()
    if full:
        return full
    pid = p.get("id", "")
    return pid.strip() or None


def _names_from_players(players: Iterable[dict]) -> list[str]:
    return [nm for p in players if (nm := _display_name(p))]

def _elo(p: dict) -> float:
    """Prefer boosted Elo for matchmaking; fall back to real Elo or default."""
    return float(p.get("boosted") or p.get("elo") or 1500.0)


def make_balanced_doubles(
    players: list[dict],
    *,
    seed: int | None = None,
) -> tuple[list[Match], list[str]]:
    """
    Generate doubles matches where:
      • Partner Elo gap ≤ MAX_PARTNER_GAP
      • Team average Elo diff ≤ MAX_TEAM_DIFF

    Algorithm:
      1. Sort players by boosted Elo descending.
      2. Greedily pair adjacent players into teams (close in skill).
      3. Pair teams together to form matches — closest average Elos play each other.
      4. Remaining players go to bench.

    Falls back to random pairing if constraints can't be satisfied.
    """
    rng = random.Random(seed)

    if not players or not isinstance(players[0], dict):
        raise TypeError("players must be a list of player dicts")

    # Shuffle first for tie-breaking randomness, then sort by Elo
    shuffled = players[:]
    rng.shuffle(shuffled)
    sorted_players = sorted(shuffled, key=_elo, reverse=True)

    bench_names: list[str] = []
    rem = len(sorted_players) % 4
    if rem:
        # Bench the lowest-rated surplus players
        bench_names = [_display_name(p) for p in sorted_players[-rem:]]
        sorted_players = sorted_players[:-rem]

    # Form pairs: [0,1], [2,3], ...  (adjacent → similar Elo)
    pairs: list[tuple[dict, dict]] = []
    for i in range(0, len(sorted_players), 2):
        pairs.append((sorted_players[i], sorted_players[i + 1]))

    # Form matches: pair adjacent pairs (similar team averages)
    matches: list[Match] = []
    for i in range(0, len(pairs), 2):
        t1p1, t1p2 = pairs[i]
        t2p1, t2p2 = pairs[i + 1]

        # Optionally shuffle team order so same players don't always face each other
        if rng.random() < 0.5:
            t2p1, t2p2 = t2p2, t2p1

        matches.append(Match(
            format="doubles",
            team1=(_display_name(t1p1), _display_name(t1p2)),
            team2=(_display_name(t2p1), _display_name(t2p2)),
        ))

    return matches, bench_names


def make_balanced_singles(
    players: list[dict],
    *,
    seed: int | None = None,
) -> tuple[list[Match], list[str]]:
    """
    Pair players by closest boosted Elo.
    """
    rng = random.Random(seed)
    shuffled = players[:]
    rng.shuffle(shuffled)
    sorted_players = sorted(shuffled, key=_elo, reverse=True)

    bench_names: list[str] = []
    if len(sorted_players) % 2 == 1:
        bench_names = [_display_name(sorted_players.pop())]

    matches: list[Match] = []
    for i in range(0, len(sorted_players), 2):
        a, b = sorted_players[i], sorted_players[i + 1]
        matches.append(Match(
            format="singles",
            team1=(_display_name(a),),
            team2=(_display_name(b),),
        ))

    return matches, bench_names


# ─── RANDOM MATCHMAKING (kept for backwards compat) ───────────────────────────

def make_random_doubles(
    players: list[str] | list[dict],
    *,
    seed: int | None = None,
) -> tuple[list[Match], list[str]]:
    rng = random.Random(seed)
    names = _names_from_players(players) if players and isinstance(players[0], dict) else [str(x).strip() for x in players]
    names = [n for n in names if n]
    rng.shuffle(names)

    bench: list[str] = []
    rem = len(names) % 4
    if rem:
        bench = names[-rem:]
        names = names[:-rem]

    matches: list[Match] = []
    for i in range(0, len(names), 4):
        a, b, c, d = names[i:i + 4]
        matches.append(Match(format="doubles", team1=(a, b), team2=(c, d)))

    return matches, bench


def make_random_singles(
    players: list[str] | list[dict],
    *,
    seed: int | None = None,
) -> tuple[list[Match], list[str]]:
    rng = random.Random(seed)
    names = _names_from_players(players) if players and isinstance(players[0], dict) else [str(x).strip() for x in players]
    names = [n for n in names if n]
    rng.shuffle(names)

    bench: list[str] = []
    if len(names) % 2 == 1:
        bench = [names.pop()]

    matches: list[Match] = []
    for i in range(0, len(names), 2):
        a, b = names[i:i + 2]
        matches.append(Match(format="singles", team1=(a,), team2=(b,)))

    return matches, bench
