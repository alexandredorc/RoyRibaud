import pygame as pg
import random
import os
from player import Player
from card import Card
import time

# 0 = A/ 1 = J/ 2 = Q/ 3 = K

class Game:
    def __init__(self):
        self.firstPlayer = random.randint(0,1)
        self.players = []
        self.createPlayer()
        self.initDeck()
        self.shuffleDeck()
        self.court_cards = []
        self.dealCards()
        self.CheckPlayersDoubleQueen()
        self.displayCourt()
        self.currentPlayerId = self.firstPlayer
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
                print(f"Le Joueur {player.idx} à une Double")
                new_card = []
                queens_card = []
                for i in index:
                    queens_card.append(player.cards.pop(i))
                    new_card.append(self.deck.pop(0))
                for i in range(2):
                    player.cards.append(new_card[i])
                    self.deck.append(queens_card[i])

    def swapCourtPlayerCards(self, courtIndex, playerIndex,visibility):
        self.court_cards[courtIndex], self.players[self.currentPlayerId].cards[playerIndex]= self.players[self.currentPlayerId].cards[playerIndex], self.court_cards[courtIndex]
        self.court_cards[courtIndex].visible=bool(visibility)
        self.displayCourt()
        if visibility:
            if self.cardEffect(self.court_cards[courtIndex].typeCard):
                return True
            else: 
                return False

    def swapCourtCards(self, index1, index2):
        self.court_cards[index1], self.court_cards[index2]= self.court_cards[index2], self.court_cards[index1]
        self.displayCourt()
        
    def returnCourtCard(self,index):
        self.court_cards[index].visible = not self.court_cards[index].visible
        self.displayCourt()
        if self.court_cards[index].visible:
            if self.cardEffect(self.court_cards[index].typeCard):
                return True
            else: 
                return False
    
    def cardEffect(self,typeCard):
        if self.testAssassinVictory() or self.testCoronationVictory():
            return True
        
        if typeCard == 0:
            self.AssassinEffect()
        if typeCard == 1:
            self.KnightEffect()
        if typeCard == 2:
            self.QueenEffect()
        if typeCard == 3:
            self.KingEffect()
        if self.testAssassinVictory() or self.testCoronationVictory():
            return True
        return False
    
    def AssassinEffect(self):
        card1 = int(input("Donne le numéro de la carte de la court que tu veux regarder 1-4: ")) -1
        card2 = int(input("Donne le numéro de la carte de la court que tu veux regarder  1-4: ")) -1

        print(self.court_cards[card1].name)
        print(self.court_cards[card2].name)
        print()
    
    def KnightEffect(self):
        card1 = int(input("Donne le numéro de la carte de la court que tu veux échanger 1-4: ")) -1
        card2 = card1
        while card2 == card1:
            card2 = int(input("Donne le numéro de la carte de la court que tu veux échanger 1-4: ")) -1
        self.swapCourtCards(card1,card2)
        card = int(input("Donne le numéro de la carte de la court que tu veux retourner 1-4 : ")) -1
        self.court_cards[card].visible = not self.court_cards[card].visible
        self.displayCourt()
      
    def QueenEffect(self):
        card1 = int(input("Donne le numéro de la carte du joueur adverse que tu veux regargé 1-3: ")) -1
        card2 = card1
        while card2 == card1:
            card2 = int(input("Donne le numéro de la carte du joueur adverse que tu veux regargé 1-3: ")) -1
        nextPlayerID = abs(self.currentPlayerId -1)
        cardPlayer1 = self.players[nextPlayerID].cards[card1]
        cardPlayer2 = self.players[nextPlayerID].cards[card2]
        print(cardPlayer1.name)
        print(cardPlayer2.name)
        if cardPlayer1.typeCard == 2:
            self.players[nextPlayerID].cards.pop(card1)
            self.players[nextPlayerID].cards.append(self.deck.pop(0))
            self.deck.append(cardPlayer1)
        if cardPlayer2.typeCard == 2:
            self.players[nextPlayerID].cards.pop(card2)
            self.players[nextPlayerID].cards.append(self.deck.pop(0))
            self.deck.append(cardPlayer2)

    def KingEffect(self):
        action = int(input("tape 1: pour retourner une carte et activé sa capacité; tape 2: pour choisir deux cartes de la pioche et reposer deux cartes: "))
        if action == 1:
            card = int(input("Donne le numéro de la carte de la court que tu veux retourner  1-4: ")) -1
            self.returnCourtCard(card)
        if action == 2:
            self.players[self.currentPlayerId].cards.append(self.deck.pop(0))
            self.players[self.currentPlayerId].cards.append(self.deck.pop(0))
            self.players[self.currentPlayerId].showPlayerHand()
            card1 = int(input("Donne le numéro de la carte de ta main que tu veux retirer  1-5: ")) -1
            card2 = int(input("Donne le numéro de la carte de ta main que tu veux retirer 1-5: ")) -1
            cardPlayer1 = self.players[self.currentPlayerId].cards[card1]
            cardPlayer2 = self.players[self.currentPlayerId].cards[card2]
            cards=[card1,card2]
            print(cards)
            cards.sort(reverse=True)
            print(cards)
            self.players[self.currentPlayerId].cards.pop(cards[0])
            self.deck.append(cardPlayer1)
            self.players[self.currentPlayerId].cards.pop(cards[1])
            self.deck.append(cardPlayer2)
            self.players[self.currentPlayerId].showPlayerHand()
            print()
    

    def clearTerminal(self):
        if os.name == 'nt':
            # For Windows
            os.system('cls')
        else:
            # For Mac and Linux (posix systems)
            os.system('clear')

    def displayCourt(self):
        print("\n Les cartes de la court sont:")
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
        
        print("Clearing in progress!")
        time.sleep(10)
        self.clearTerminal()
    
    def testWeddingVictory(self):
        count = 0
        for c in self.players[self.currentPlayerId].cards:
            if c.typeCard == 2:
                count += 1
        if count == 3:
            print("Victoire Royal: Le Mariage")
            return True
        else:
            return False

    def testCoronationVictory(self):
        count = 0
        for c in self.court_cards:
            if c.typeCard == 3 and c.visible:
                count += 1
        if count >= 3:
            print("Victoire Royal: Le Couronnement")
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
            print("Victoire Royal: L'Assassinat")
            return True
        else:
            return False

    def clientTurn(self):
        self.clearTerminal()
        self.displayCourt()
        self.players[self.currentPlayerId].showPlayerHand()
        if self.testWeddingVictory():
            return True
        action = int(input("A ton tour de jouer - tape 1: pour retourner, tape 2 pour remplacer: "))
        if action == 1:
            card = int(input("choisit une carte de la court à retourner 1 - 4: "))-1
            self.returnCourtCard(card)
        elif action == 2:
            playercard = int(input("Choisit une carte de la main à échanger 1 - 3: "))-1
            courtcard = int(input("choisit une carte de la court à prendre 1 - 4: "))-1
            visibility = int(input("mettre 1 pour mettre la carte face visible & 0 pour face caché: "))
            self.swapCourtPlayerCards(courtcard,playercard,visibility)
        else:
            print('you dumb!')
            return False

        if self.testCoronationVictory():
            return True
        if self.testAssassinVictory():
            return True
        self.displayCourt()
        return False


