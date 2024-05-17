
class Player:
    def __init__(self, idx, cards):
        self.cards = cards
        self.idx = idx
        self.wins = 0
    
    def showPlayerHand(self):
        print(f"\nplayer {self.idx} hand is:")
        for c in self.cards:
            print(c.name)