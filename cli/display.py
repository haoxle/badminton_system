from engine.matchmaking import Match


def _fit(text: str, width: int) -> str:
    text = text.strip()
    if len(text) > width:
        return text[: width - 1] + "…"
    return text.ljust(width)


def render_badminton_court(court_no: int, match: Match) -> list[str]:
    """
    Returns a list of strings representing one court.
    Visually: outer boundary + midline + net + player labels on each side.
    """
    left = " & ".join(match.team1)
    right = " & ".join(match.team2)

    # Inside width (between vertical borders)
    W = 33  # tweak if you want wider courts

    title = f"Court {court_no} ({match.format})"
    title = _fit(title, W)

    left_label = _fit(left, W)
    right_label = _fit(right, W)

    # Court drawing:
    # - Top boundary
    # - A bit of space
    # - Left team label inside left half, right team label inside right half
    # - Service-ish lines and a net
    lines = [
        f"┌{'─'*W}┐",
        f"│{title}│",
        f"├{'─'*W}┤",
        f"│{_fit('', W)}│",
        f"│{left_label}│",
        f"│{_fit('', W)}│",
        f"│{'─'*((W-1)//2)}┼{'─'*(W-1-((W-1)//2))}│",   # centre line
        f"│{' ' * ((W-1)//2)}│{' ' * (W-1-((W-1)//2))}│",  # net gap
        f"│{'='*((W-1)//2)}┼{'='*(W-1-((W-1)//2))}│",  # net
        f"│{' ' * ((W-1)//2)}│{' ' * (W-1-((W-1)//2))}│",  # net gap
        f"│{'─'*((W-1)//2)}┼{'─'*(W-1-((W-1)//2))}│",   # centre line
        f"│{_fit('', W)}│",
        f"│{right_label}│",
        f"│{_fit('', W)}│",
        f"└{'─'*W}┘",
    ]
    return lines


def print_courts_as_board(matches: list[Match], courts: int, per_row: int = 2) -> None:
    """
    Prints a board of badminton-court diagrams.
    per_row=2 makes it look like courts laid out side-by-side.
    """
    on_court = matches[:courts]
    if not on_court:
        print("\n(No matches allocated)\n")
        return

    court_blocks = [render_badminton_court(i + 1, m) for i, m in enumerate(on_court)]
    block_height = len(court_blocks[0])
    gap = "   "  # spacing between courts

    print("\n=== Courts ===")
    for r in range(0, len(court_blocks), per_row):
        row_blocks = court_blocks[r : r + per_row]
        for line_i in range(block_height):
            print(gap.join(block[line_i] for block in row_blocks))
        print()