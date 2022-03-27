class CoupPlayer:
    def __init__(self, name):
        self.name = name
        self.coins = 2
        self.cards = [-2, -2]
        self.numCards = 2
        self.isAlive = True

    def die(self):
        self.isAlive = False

    def lose_card(self):
        # gets card player wants to lose from terminal
        lost = int(input("Lose what card?"))

        # check if the card is possible
        if(lost==-2 or lost not in self.cards):
            print("Try again!")
            self.lose_card()
        else:
            # replace the card with the "dead" card
            self.numCards -= 1
            if(lost==self.cards[0]):
                self.cards[0] = -2
            else:
                self.cards[1] = -2
        
        #check if player is alive
        if(self.numCards == 0):
            self.die()

        return lost
    
    def getActions(self):
        if self.coins < 3:
            return([0, 2, 3, 5, 6])
        elif self.coins < 7:
            return([0, 1, 2, 3, 5, 6])
        elif self.coins < 10:
            return([0, 1, 2, 3, 5, 6, 7])
        else:
            return([7])

    
        




