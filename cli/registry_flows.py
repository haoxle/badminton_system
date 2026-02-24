from core.player import PlayerRegistry


def player_label(p: dict) -> str:
    return f"{p.get('id')} | {p.get('first_name')} {p.get('surname')} | rating={p.get('rating')}"


def print_players(players: list[dict]) -> None:
    for p in players:
        print(f"- {player_label(p)}")


def register_player_flow(registry: PlayerRegistry) -> None:
    first_name = input("Player first name: ").strip()
    if not first_name:
        print("First name cannot be empty.")
        return

    surname = input("Player surname: ").strip()
    if not surname:
        print("Surname cannot be empty.")
        return

    rating = input("Rating (A/B/C/D/E) [default C]: ").strip().upper() or "C"

    try:
        registry.register_player(first_name, surname, rating=rating)
    except Exception as e:
        print(f"Could not register player: {e}")


def list_players_flow(registry: PlayerRegistry) -> None:
    players = registry.list_players()
    if not players:
        print("No players registered yet.")
        return

    print("\nPlayers in database:")
    print_players(players)