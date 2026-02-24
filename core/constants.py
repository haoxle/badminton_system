"""
Central configuration for the badminton ranking system.
All tunable values live here.
"""
ALLOWED_GRADES = (
    "E", 
    "D", 
    "C-",
    "C",
    "C+",
    "B-",
    "B",
    "B+",
    "A", 
)

GRADE_THRESHOLDS = [
    ("E", 0),
    ("D", 1200),
    ("C-", 1350),
    ("C", 1450),
    ("C+", 1550),
    ("B-", 1650),
    ("B", 1750),
    ("B+", 1850),
    ("A", 1950),
]

DEFAULT_ELO = 1500.0
DEFAULT_BOOSTED = 1500.0

K_RANKED = 24.0

K_BALANCED = 8.0

ELO_DIVISOR = 400.0


# BOOSTED (ANTI-CARRY) SYSTEM

# How strongly carry behaviour increases boosted rating
BOOST_ALPHA = 0.04

# How quickly boosted drifts back toward real Elo
BOOST_GAMMA = 0.05


# MATCH SPLITTING CONFIGURATION

# Power used when splitting rating change inside a team.
# 2.0 = stronger player gets noticeably larger share.
SPLIT_POWER = 2.0




PROMOTION_MATCH_STREAK = 8

DEMOTION_MATCH_STREAK = 8



MAX_PARTNER_GAP = 250

MAX_TEAM_DIFF = 300

DATABASE_PATH = "database/club.db"
