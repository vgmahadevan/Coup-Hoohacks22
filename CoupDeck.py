import random

class CoupDeck:
    def __init__(self):
        self.deck = [0,1,2,3,4]*3
        self.deck.shuffle()

    def shuffle(self):
        self.deck.shuffle()

    def draw(self):
        return self.deck.pop()

    def add(self, card1, card2 = -1):
        self.deck.append(card1)
        if card2 != -1:
            self.deck.append(card2)
        self.deck.shuffle()