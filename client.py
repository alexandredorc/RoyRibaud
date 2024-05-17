import pygame as pg
from network import Network
from player import Player
from action import Action
import time


class Client:
    def __init__(self):
        
        self.width = 500
        self.height = 500
        self.win = pg.display.set_mode((self.width,self.height))
        pg.display.set_caption("Client")
        self.room = -1
        self.server=Network("http://0.0.0.0:5555/login")
        self.playerNb = -1
        while self.room <= 0 or 9999 <= self.room:
            txt = input("put your room number:")
            if txt.isnumeric():
                nbPlayers=self.server.send(Action("connect",int(txt)))
                if nbPlayers == 0 or nbPlayers == 1:
                    self.room= int(txt)
                    self.playerNb = nbPlayers

        print(f"The room number is {self.room}")
        
        if self.playerNb == 0:
            while True:
                time.sleep(2)
                if self.server.send(Action("check",self.room)):
                    break
        print("C'est partie pour jouer")
        self.server=Network(f"http://0.0.0.0:5555/items/{self.room}")
        

    



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