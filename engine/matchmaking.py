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
    """
    Build a display name from a player row dict.
    Supports both old schema (name) and new schema (first_name + surname).
    """
    first = p.get("first_name")
    surname = p.get("surname")
    if isinstance(first, str) and isinstance(surname, str):
        full = f"{first.strip()} {surname.strip()}".strip()
        if full and full != "":
            return full

    pid = p.get("id")
    if isinstance(pid, str) and pid.strip():
        return pid.strip()

    return None


def _names_from_players(players: Iterable[dict]) -> list[str]:
    names: list[str] = []
    for p in players:
        nm = _display_name(p)
        if nm:
            names.append(nm)
    return names


def make_random_doubles(
    players: list[str] | list[dict],
    *,
    seed: int | None = None,
) -> tuple[list[Match], list[str]]:
    
    rng = random.Random(seed)

    if players and isinstance(players[0], dict):
        names = _names_from_players(players)
    else:
        names = [str(x).strip() for x in players]
        names = [n for n in names if n]

    rng.shuffle(names)

    matches: list[Match] = []
    bench: list[str] = []

    rem = len(names) % 4
    if rem:
        bench = names[-rem:]
        names = names[:-rem]

    for i in range(0, len(names), 4):
        a, b, c, d = names[i : i + 4]
        matches.append(Match(format="doubles", team1=(a, b), team2=(c, d)))

    return matches, bench


def make_random_singles(
    players: list[str] | list[dict],
    *,
    seed: int | None = None,
) -> tuple[list[Match], list[str]]:
    rng = random.Random(seed)

    if players and isinstance(players[0], dict):
        names = _names_from_players(players)
    else:
        names = [str(x).strip() for x in players]
        names = [n for n in names if n]

    rng.shuffle(names)

    matches: list[Match] = []
    bench: list[str] = []

    if len(names) % 2 == 1:
        bench = [names.pop()]

    for i in range(0, len(names), 2):
        a, b = names[i : i + 2]
        matches.append(Match(format="singles", team1=(a,), team2=(b,)))

    return matches, bench