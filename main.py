from core.db import init_db
from core.player import PlayerRegistry
from cli.app import run


if __name__ == "__main__":
    init_db()
    registry = PlayerRegistry()
    run(registry)