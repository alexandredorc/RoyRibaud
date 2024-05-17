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
        while self.room <= 0 or 9999 <= self.room:
            txt = input("put your room number:")
            if txt.isnumeric() and self.testRoomAvailable(int(txt)):
                self.room = int(txt)
        self.server=Network("https://royribaud.onrender.com",self.room)
        print(f"The room number is {self.room}")
        self.createRooom()
        pg.display.set_caption("Client")

    def testRoomAvailable(self,room):
        if room != -1:
            return True
        
    def createRooom(self):
        self.server.send(Action("create",self.room))


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