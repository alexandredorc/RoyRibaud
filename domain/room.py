from domain.game.game import Game


class Room:
    """Represents a 2-player game room and its current game state."""

    MAX_PLAYERS = 2

    def __init__(self, number: int):
        # Keep legacy attribute names for compatibility with existing code.
        self.nbPlayerMax = self.MAX_PLAYERS
        self.roomNumber = number
        self.status = True
        self.game = Game()
        self.connected_players: list[int] = []
        self.playerConnected = 0

    def _sync_connected_count(self) -> None:
        self.playerConnected = len(self.connected_players)

    def connect_player(self) -> int:
        if len(self.connected_players) >= self.nbPlayerMax:
            return -1

        player_id = len(self.connected_players)
        self.connected_players.append(player_id)
        self._sync_connected_count()
        return player_id

    def is_ready(self) -> bool:
        return len(self.connected_players) >= self.nbPlayerMax

    def reset_game(self) -> None:
        """Replace the current game with a fresh one, keeping players connected."""
        self.game = Game()
