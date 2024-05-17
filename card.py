class Card:
    def __init__(self, typeCard, visible = False):
        self.typeCard = typeCard
        self.typeCardName()
        self.visible = visible

    def typeCardName(self):
        if self.typeCard == 0:
            self.name = 'Assasin'
        if self.typeCard == 1:
            self.name = 'Chevalier'
        if self.typeCard == 2:
            self.name = 'Reine'
        if self.typeCard == 3:
            self.name = 'Roi'

    def returnCard(self):
        self.visible = not self.visible