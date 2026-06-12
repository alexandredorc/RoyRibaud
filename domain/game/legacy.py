import os


class GameLegacyMixin:
    # Compatibility helpers used by old CLI flow.
    def displayCourt(self):
        print("\nCourt cards:")
        for card in self.court_cards:
            if card.visible:
                print(card.name)
            else:
                print("Hidden")

    def showAllCards(self):
        print("\nPlayer 1 cards:")
        for card in self.players[0].cards:
            print(card.name)
        print("\nPlayer 2 cards:")
        for card in self.players[1].cards:
            print(card.name)
        print("\nCourt cards:")
        for card in self.court_cards:
            print(card.name, card.visible)

    def clearTerminal(self):
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

    def returnCourtCard(self, index):
        result = self._flip_court(index, trigger_effect=True)
        return result.get("winner") is not None

    def swapCourtPlayerCards(self, courtIndex, playerIndex, visibility):
        result = self._swap_hand_court(playerIndex, courtIndex, visibility)
        return result.get("winner") is not None

    def cardEffect(self, typeCard):
        result = self._trigger_visible_effect(typeCard)
        return result.get("winner") is not None

    def clientTurn(self):
        raise NotImplementedError("CLI turn loop is replaced by web action APIs.")
