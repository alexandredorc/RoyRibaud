import pygame as pg
from network import Network
from player import Player
from action import Action
from game import Game
import time


class Client:
    def __init__(self,uri="https://royribaud.onrender.com"):
        self.uri=uri
        self.width = 500
        self.height = 500
        self.win = pg.display.set_mode((self.width,self.height))
        pg.display.set_caption("Client")
        self.room = -1
        self.server=Network(f"{self.uri}/login")
        self.playerId = -1
        while self.room <= 0 or 9999 <= self.room:
            txt = input("put your room number:")
            if txt.isnumeric():
                nbPlayers=self.server.send(Action("connect",int(txt)))
                if nbPlayers == 0 or nbPlayers == 1:
                    self.room= int(txt)
                    self.playerId = nbPlayers

        print(f"The room number is {self.room}")
        
        if self.playerId == 0:
            while True:
                time.sleep(2)
                if self.server.send(Action("check",self.room)):
                    break
        
        print("C'est partie pour jouer")
        self.server=Network(f"{self.uri}/items/{self.room}")
        self.clientGameLoop()
        
    def waitOtherPlayer(self):
        print("Waiting for the other player to play")
        while True:
            time.sleep(0.5)
            self.currentGame=self.server.get()
            if isinstance(self.currentGame,Game) and self.currentGame.currentPlayerId == self.playerId:
                break
        print("Its your turn to play!")

    def clientGameLoop(self):
        self.currentGame=self.server.get()
        while True:
            self.waitOtherPlayer()
            if self.currentGame.clientTurn():
                print("this is a win for you")
            self.currentGame.currentPlayerId = abs(self.currentGame.currentPlayerId - 1)
            self.server.send(self.currentGame)

def redrawWindow(win):
    pass

def main():
    run = True
    myClient = Client()
    clock = pg.time.Clock()

    while run:
        clock.tick(60)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                pg.quit()

      
        

if __name__ == "__main__":
    main()