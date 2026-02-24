from dataclasses import dataclass

@dataclass
class Player:
    id: str
    first_name: str
    surname: str
    rating: str
    elo: float
    boosted: float
    total_games: int
    total_wins: int
    total_losses: int