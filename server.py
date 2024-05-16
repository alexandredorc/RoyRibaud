from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
from player import Player

app = FastAPI()

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

players = [Player(0, 0, 50, 50, (255, 0, 0)), Player(100, 100, 50, 50, (0, 0, 255))]

class PlayerUpdate(BaseModel):
    x: int
    y: int
    width: int
    height: int
    color: tuple

connected_clients = []

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        await websocket.send_bytes(pickle.dumps(players[player_id]))
        while True:
            data = await websocket.receive_bytes()
            players[player_id] = pickle.loads(data)
            reply = players[1] if player_id == 0 else players[0]
            await websocket.send_bytes(pickle.dumps(reply))
    except WebSocketDisconnect:
        print(f"Player {player_id} disconnected")
        connected_clients.remove(websocket)
    except Exception as e:
        print(f"Error: {e}")
        connected_clients.remove(websocket)
