import pygame as pg
from network import Network
from player import Player
from action import Action


class Client:
    def __init__(self):
        
        self.width = 500
        self.height = 500
        self.win = pg.display.set_mode((self.width,self.height))
        self.room = -1
        self.server=Network("http://0.0.0.0:5555/login")
        self.playerNb = -1
        while self.room <= 0 or 9999 <= self.room:
            txt = input("put your room number:")
            if txt.isnumeric():
                nbPlayers=self.server.send(Action("connect",int(txt)))
                print(nbPlayers)
                if nbPlayers == 0 or nbPlayers == 1:
                    self.room= int(txt)
                    self.playerNb = nbPlayers
            print(self.room)
            print(self.playerNb)

        print(f"The room number is {self.room}")
        
        self.server=Network(f"http://0.0.0.0:5555/items/{self.room}")
        pg.display.set_caption("Client")



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