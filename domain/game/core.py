import random
from domain.entities.card import Card
from domain.entities.player import Player


class GameCoreMixin:
    def __init__(self):
        self.firstPlayer = random.randint(0, 1)
        self.players = []
        self.createPlayer()
        self.initDeck()
        self.shuffleDeck()
        self.court_cards = []
        self.dealCards()
        self.CheckPlayersDoubleQueen()
        self.currentPlayerId = self.firstPlayer
        self.pending_effect = None
        self.in_game = True
        self.winner = None
        self.last_message = "Game started"

    def initDeck(self):
        self.deck = []
        for _ in range(4):
            for kind in range(4):
                self.deck.append(Card(kind))

    def createPlayer(self):
        self.players.append(Player(1, []))
        self.players.append(Player(2, []))

    def shuffleDeck(self):
        random.shuffle(self.deck)

    def dealCards(self):
        for i in range(6):
            if i % 2 == 0:
                self.players[0].cards.append(self.deck.pop(0))
            else:
                self.players[1].cards.append(self.deck.pop(0))
        for _ in range(4):
            self.court_cards.append(self.deck.pop(0))

    def CheckPlayersDoubleQueen(self):
        for player in self.players:
            index = []
            for i, card in enumerate(player.cards):
                if card.typeCard == 2:
                    index.append(i)
            index.sort(reverse=True)
            if len(index) == 2 and len(self.deck) >= 2:
                new_cards = []
                queens_cards = []
                for i in index:
                    queens_cards.append(player.cards.pop(i))
                    new_cards.append(self.deck.pop(0))
                for i in range(2):
                    player.cards.append(new_cards[i])
                    self.deck.append(queens_cards[i])

    def _draw_card(self):
        if not self.deck:
            return None
        return self.deck.pop(0)

    def _validate_index(self, idx, min_value, max_value):
        return isinstance(idx, int) and min_value <= idx <= max_value

    def _opponent_id(self, player_id):
        return abs(player_id - 1)

    def _set_winner(self, reason):
        self.winner = {
            "player_id": self.currentPlayerId,
            "reason": reason,
        }
        self.in_game = False

    def testWeddingVictory(self):
        count = 0
        for card in self.players[self.currentPlayerId].cards:
            if card.typeCard == 2:
                count += 1
        if count == 3:
            self._set_winner("wedding")
            self.last_message = "Wedding victory"
            return True
        return False

    def testCoronationVictory(self):
        count = 0
        for card in self.court_cards:
            if card.typeCard == 3 and card.visible:
                count += 1
        if count >= 3:
            self._set_winner("coronation")
            self.last_message = "Coronation victory"
            return True
        return False

    def testAssassinVictory(self):
        for i in range(2):
            count = 0
            for j in range(3):
                idx = i + j
                if self.court_cards[idx].visible and (j == 1 or self.court_cards[idx].typeCard == 0):
                    count += 1
            if count >= 3:
                self._set_winner("assassination")
                self.last_message = "Assassination victory"
                return True
        return False

    def check_start_turn_victory(self):
        if self.winner is not None:
            return True
        return self.testWeddingVictory()

    def _check_court_victories(self):
        if self.testCoronationVictory():
            return True
        if self.testAssassinVictory():
            return True
        return False

    def _complete_turn(self, message):
        if self.winner is None:
            self.currentPlayerId = self._opponent_id(self.currentPlayerId)
            self.check_start_turn_victory()
        self.pending_effect = None
        self.last_message = message
        return {
            "ok": True,
            "turn_completed": True,
            "message": message,
            "winner": self.winner,
        }

    def _serialize_card(self, card, reveal):
        if reveal:
            return {
                "type": card.typeCard,
                "name": card.name,
                "visible": card.visible,
            }
        return {
            "type": None,
            "name": "Hidden",
            "visible": card.visible,
        }

    def to_public_state(self, viewer_player_id):
        self.check_start_turn_victory()

        my_hand = [
            self._serialize_card(card, True)
            for card in self.players[viewer_player_id].cards
        ]
        opponent_hand_count = len(self.players[self._opponent_id(viewer_player_id)].cards)

        court = []
        for card in self.court_cards:
            court.append(self._serialize_card(card, card.visible))

        pending_effect = None
        if self.pending_effect is not None and viewer_player_id == self.currentPlayerId:
            pending_effect = self.pending_effect

        return {
            "in_game": self.in_game,
            "winner": self.winner,
            "current_player_id": self.currentPlayerId,
            "viewer_player_id": viewer_player_id,
            "is_my_turn": viewer_player_id == self.currentPlayerId,
            "pending_effect": pending_effect,
            "court_cards": court,
            "my_hand": my_hand,
            "opponent_hand_count": opponent_hand_count,
            "deck_count": len(self.deck),
            "message": self.last_message,
        }
