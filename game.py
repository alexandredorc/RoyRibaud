import pygame
import random
from player import Player
from card import Card
# 0 = A/ 1 = J/ 2 = Q/ 3 = K

class Game:
    def __init__(self):
        self.players = []
        self.createPlayer()
        self.initDeck()
        self.shuffleDeck()
        self.court_cards = []
        self.dealCards()
        self.CheckPlayersDoubleQueen()
        self.displayCourt()
        self.currentPlayer = self.players[0]
        self.in_game = True

    def initDeck(self):
        self.deck = []
        for i in range(4):
            for j in range(4):
                self.deck.append(Card(j))

    def createPlayer(self):
        self.players.append(Player(1,[]))
        self.players.append(Player(2,[]))

    def shuffleDeck(self):
        random.shuffle(self.deck)

    def dealCards(self):
        for i in range(6):
            if i % 2 == 0:
                self.players[0].cards.append(self.deck.pop(0))
            else:
                self.players[1].cards.append(self.deck.pop(0))       
        for i in range(4):
            self.court_cards.append(self.deck.pop(0))
        #self.showAllCards()

    def CheckPlayersDoubleQueen(self):
        for player in self.players:
            index = []
            for i, c in enumerate(player.cards):
                if c.typeCard == 2:
                    index.append(i)
            index.sort(reverse=True)
            if len(index)==2:
                print(f"player {player.idx} has a double queen")
                new_card = []
                queens_card = []
                for i in index:
                    queens_card.append(player.cards.pop(i))
                    new_card.append(self.deck.pop(0))
                for i in range(2):
                    player.cards.append(new_card[i])
                    self.deck.append(queens_card[i])
                
        
    def swapCourtCards(self, index1, index2):
        self.court_cards[index1], self.court_cards[index2]= self.court_cards[index2], self.court_cards[index1]
    
    def returnCourtCard(self,index):
        self.court_cards[index].visible = not self.court_cards[index].visible
    
    def displayCourt(self):
        print("\nCourt Cards are:")
        for c in self.court_cards:
            if c.visible:
                print(c.name)
            else:
                print("hidden")

    def showAllCards(self):
        print("\nplayer 1 cards are:")
        for c in self.players[0].cards:
            print(c.name)
        print("\nplayer 2 cards are:")
        for c in self.players[1].cards:
            print(c.name)
        print("\ncourt cards are:")
        for c in self.court_cards:
            print(c.name, c.visible)

        print("\ndeck rest cards")
        for c in self.deck:
            print(c.name, c.visible)
    
    def testWeddingVictory(self):
        count = 0
        for c in self.currentPlayer.cards:
            if c.typeCard == 2:
                count += 1
        if count == 3:
            return True
        else:
            return False

    def testCoronationVictory(self):
        count = 0
        for c in self.court_cards:
            if c.typeCard == 3 and c.visible:
                count += 1
        if count >= 3:
            return True
        else:
            return False
        
    def testAssassinVictory(self):
        count = 0
        for i in range(2):
            for j in range(3):
                idx = i+j
                if self.court_cards[idx].visible and (j == 1 or self.court_cards[idx].typeCard == 0):
                    count += 1

        if count >= 3:
            return True
        else:
            return False



g = Game()