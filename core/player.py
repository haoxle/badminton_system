import random
import sqlite3
from core.db import get_db_connection
from core.constants import ALLOWED_GRADES


class PlayerRegistry:


    def _generate_player_id(self, first_name: str, surname: str) -> str:
        base = f"{first_name[0].upper()}{surname.capitalize()}"

        existing_ids = {p["id"] for p in self.list_players()}

        while True:
            suffix = random.randint(1000, 9999)
            new_id = f"{base}{suffix}"
            if new_id not in existing_ids:
                return new_id


    def register_player(self, first_name: str, surname: str, rating: str = "E") -> dict:
            first_name = first_name.strip()
            surname = surname.strip()
            rating = rating.strip().upper()

            if not first_name or not surname:
                raise ValueError("First name and surname cannot be empty.")
            if rating not in ALLOWED_GRADES:
                raise ValueError(f"Invalid rating '{rating}'. Must be one of {ALLOWED_GRADES}")

            player_id = self._generate_player_id(first_name, surname)

            try:
                with get_db_connection() as conn:
                    conn.execute(
                        "INSERT INTO players (id, first_name, surname, rating) VALUES (?, ?, ?, ?)",
                        (player_id, first_name, surname, rating),
                    )
                    conn.commit()
                return {"id": player_id, "first_name": first_name, "surname": surname, "rating": rating}

            except sqlite3.IntegrityError:
                raise ValueError("Player already exists.")
        

    def get_player(self, *, player_id: str | None = None,
                    first_name: str | None = None,
                    surname: str | None = None) -> list[dict]:
            with get_db_connection() as conn:
                if player_id:
                    rows = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchall()
                elif first_name and surname:
                    rows = conn.execute(
                        "SELECT * FROM players WHERE first_name = ? AND surname = ?",
                        (first_name.strip(), surname.strip()),
                    ).fetchall()
                else:
                    raise ValueError("Provide either player_id OR first_name and surname.")

            return [dict(r) for r in rows]


    def delete_player(self, player_id: str) -> bool:
        player_id = player_id.strip()
        if not player_id:
            raise ValueError("player_id cannot be empty.")

        with get_db_connection() as conn:
            cur = conn.execute("DELETE FROM players WHERE id = ?", (player_id,))
            conn.commit()
            return cur.rowcount > 0


    def list_players(self) -> list[dict]:
        with get_db_connection() as conn:
            rows = conn.execute("SELECT * FROM players ORDER BY surname, first_name").fetchall()
        return [dict(r) for r in rows]


    def update_player(self, player_id: str, *,
                        first_name: str | None = None,
                        surname: str | None = None,
                        rating: str | None = None) -> bool:
            player_id = player_id.strip()
            if not player_id:
                raise ValueError("player_id cannot be empty.")

            fields, values = [], []

            if first_name is not None:
                first_name = first_name.strip()
                if not first_name:
                    raise ValueError("first_name cannot be empty.")
                fields.append("first_name = ?")
                values.append(first_name)

            if surname is not None:
                surname = surname.strip()
                if not surname:
                    raise ValueError("surname cannot be empty.")
                fields.append("surname = ?")
                values.append(surname)

            if rating is not None:
                rating = rating.strip().upper()
                if rating not in ALLOWED_GRADES:
                    raise ValueError(f"Invalid rating '{rating}'. Must be one of {ALLOWED_GRADES}")
                fields.append("rating = ?")
                values.append(rating)

            if not fields:
                return False

            values.append(player_id)
            sql = f"UPDATE players SET {', '.join(fields)} WHERE id = ?"

            with get_db_connection() as conn:
                cur = conn.execute(sql, values)
                conn.commit()
                return cur.rowcount > 0