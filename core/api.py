from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.player import PlayerRegistry
from typing import Optional


app = FastAPI(title="Badminton API")
registry = PlayerRegistry()

class PlayerCreate(BaseModel):
    first_name: str
    surname: str
    rating: str = "E"
    elo: Optional[float] = None

class PlayerUpdate(BaseModel):
    first_name: str | None = None
    surname: str | None = None
    rating: str | None = None

@app.get("/players", tags=["Players"])
def list_players():
    return registry.list_players()

@app.get("/players/{player_id}", tags=["Players"])
def get_player(player_id: str):
    rows = registry.get_player(player_id=player_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Player not found")
    return rows[0]

@app.post("/players", status_code=201, tags=["Players"])
def create_player(payload: PlayerCreate):
    try:
        return registry.register_player(
            payload.first_name, payload.surname, payload.rating, payload.elo
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/players/{player_id}", tags=["Players"])
def update_player(player_id: str, payload: PlayerUpdate):
    try:
        updated = registry.update_player(
            player_id,
            first_name=payload.first_name,
            surname=payload.surname,
            rating=payload.rating,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Player not found (or no fields changed)")
        return registry.get_player(player_id=player_id)[0]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/players/{player_id}", tags=["Players"])
def delete_player(player_id: str):
    try:
        deleted = registry.delete_player(player_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Player not found")
        return {"deleted": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))