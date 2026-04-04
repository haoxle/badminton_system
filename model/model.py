from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Player:
    id:            str
    first_name:    str
    surname:       str
    rating:        str
    elo:           float
    boosted:       float
    total_games:   int
    total_wins:    int
    total_losses:  int
    streak_wins:   int
    streak_losses: int


@dataclass
class Session:
    id:           str
    date:         str     
    start_time:   str  
    end_time:     str    
    court_count:  int
    format:       str 
    status:       str        


@dataclass
class Court:
    id:            int
    session_id:    str
    court_number:  int
    status:        str     


@dataclass
class Match:
    id:           str
    session_id:   str
    court_id:     int
    format:       str
    team1_ids:    list[str]
    team2_ids:    list[str]
    score_team1:  Optional[int]
    score_team2:  Optional[int]
    status:       str
    started_at:   Optional[str]
    completed_at: Optional[str]


@dataclass
class MatchResult:
    """Passed to the ranking engine after a game finishes."""
    match_id:    str
    winner_team: int        
    team1_ids:   list[str]
    team2_ids:   list[str]
    format:      str      
