from game import Game

class Room:
    def __init__(self,number):
        self.nbPlayerMax = 2
        self.roomNumber = number
        self.status = True
        self.playerConnected = 1
        self.game = Game()
        
    