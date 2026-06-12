from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from application.server import Server


class ConnectRequest(BaseModel):
    room_number: int = Field(..., ge=1, le=9998)


class ActionRequest(BaseModel):
    player_id: int = Field(..., ge=0, le=1)
    action: dict


app = FastAPI(title="RoyRibaud API")
server = Server()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index():
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/rooms/connect")
def connect_room(payload: ConnectRequest):
    room = server.get_or_create_room(payload.room_number)
    player_id = room.connect_player()
    if player_id < 0:
        raise HTTPException(status_code=409, detail="Room is full")

    return {
        "room_number": room.roomNumber,
        "player_id": player_id,
        "ready": room.is_ready(),
        "players_connected": room.playerConnected,
    }


@app.get("/api/rooms/{room_number}/status")
def room_status(room_number: int):
    room = server.find_room(room_number)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return {
        "room_number": room.roomNumber,
        "ready": room.is_ready(),
        "players_connected": room.playerConnected,
    }


@app.get("/api/rooms/{room_number}/state/{player_id}")
def game_state(room_number: int, player_id: int):
    room = server.find_room(room_number)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if player_id not in (0, 1):
        raise HTTPException(status_code=400, detail="Invalid player id")
    return room.game.to_public_state(player_id)


@app.post("/api/rooms/{room_number}/reset")
def reset_room(room_number: int):
    room = server.find_room(room_number)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.is_ready():
        raise HTTPException(status_code=409, detail="Room is not ready")
    room.reset_game()
    return {"ok": True}


@app.post("/api/rooms/{room_number}/action")
def game_action(room_number: int, payload: ActionRequest):
    room = server.find_room(room_number)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    if payload.player_id not in room.connected_players:
        raise HTTPException(status_code=403, detail="Player is not connected to this room")

    result = room.game.apply_action(payload.player_id, payload.action)
    state = room.game.to_public_state(payload.player_id)
    return {
        "result": result,
        "state": state,
    }
