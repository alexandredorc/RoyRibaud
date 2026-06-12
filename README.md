# Le Roy des Ribauds

Turn-based 2-player card game with a FastAPI backend and a browser frontend.

## Project structure

- `domain/`
- `domain/entities/`: Core entities (`Card`, `Player`)
- `domain/game/`: Game aggregate and rule engine (`core`, `actions`, `legacy`)
- `domain/room.py`: Room aggregate
- `application/`
- `application/server.py`: Room lifecycle and orchestration service
- `application/dto/`: Application DTOs (`Action`)
- `infrastructure/`
- `infrastructure/web/api.py`: FastAPI transport layer
- `infrastructure/web/static/`: Browser frontend assets
- `infrastructure/network/legacy_network.py`: Legacy HTTP/pickle client transport
- `infrastructure/cli/legacy_client.py`: Legacy CLI client
- `main.py`: Entry point exposing `app`

## Rules summary

Each player has 3 cards in hand.
A shared court has 4 cards.
Win with one of these conditions:

- Wedding: start your turn with 3 Queens in hand.
- Coronation: reveal 3 Kings on the court.
- Assassination: reveal any visible card surrounded by 2 visible Assassins.

Card effects when a card is revealed on court:

- Assassin: peek at 2 court cards.
- Knight: swap 2 court cards, then flip one court card (no effect triggered).
- Queen: inspect 2 enemy hand cards; remove revealed Queens and replace from deck.
- King: choose either flip mode or draw/discard mode.

## Run locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start server:

```bash
uvicorn main:app --reload
```

This command runs the FastAPI app from `main.py` and auto-reloads when files change.

Open in browser:

- <http://127.0.0.1:8000>

## Web flow

1. Player 1 joins a room number.
2. Player 2 joins the same room number.
3. Both players play in separate browser tabs/windows.
4. UI polls game state and enables actions only on your turn.

## API endpoints

- `POST /api/rooms/connect`
- `GET /api/rooms/{room_number}/status`
- `GET /api/rooms/{room_number}/state/{player_id}`
- `POST /api/rooms/{room_number}/action`

## Notes

- Active transport is JSON (no pickle on active API routes).
- Legacy CLI flow is no longer the primary entry point.
