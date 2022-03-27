from turtle import pos
from CoupDeck import CoupDeck
from CoupPlayer import CoupPlayer
import math

class CoupGame:
    actionToString = {0: 'Tax',
                        1: 'Assassinate',
                        2: 'Exchange',
                        3: 'Steal',
                        5: 'Income',
                        6: 'Foreign Aid',
                        7: 'Coup'}

    def __init__(self):
        self.playerCount = 0
        self.currentPlayer = 0
        # Lists of names
        self.alive = []
        self.dead = []
        self.cardsRemoved = [0,0,0,0,0]
        self.deck = CoupDeck()

    def addPlayer(self, name):
        self.playerCount += 1
        self.alive.append(CoupPlayer(name))

    def deal(self):
        for i in range(self.playerCount):
            self.alive[i].cards[0] = self.deck.draw()
            self.alive[i].cards[1] = self.deck.draw()

    def takeTurn(self, action):
        player = self.alive[self.currentPlayer]
        possibleActions = player.getActions()

        if action not in possibleActions:
            return False

        if (3 in possibleActions and self.noSteal()):
            possibleActions.remove(3)
        action = self.getChosenAct(possibleActions, player)
        target = self.getTarget(action)
        self.displayAction(action, target)
        # assass must spend
        if action == 1:
            player.coins -= 3
        if action == 7:
            player.coins -= 7

        # challenge
        challenger = self.challenge(action, player)
        if challenger:
            actionWentThrough = self.resolveChallenge(challenger, player, action)

        # block
        if actionWentThrough:
            card, blocker = self.getBlocker(action, target)
            if card != -1:
                actionWentThrough = False
                # challenge block
                challenger = self.challenge(card, blocker)
                if challenger:
                    actionWentThrough = not self.resolveChallenge(challenger, blocker, card)

        # execute
        if actionWentThrough:
            if action == 0:
                self.tax(player)
            elif action == 1:
                self.assass(player, target)
            elif action == 2:
                self.exchange(player)
            elif action == 3:
                self.steal(player, target)
            elif action == 5:
                self.income(player)
            elif action == 6:
                self.foreignAid(player)
            else:
                self.coup(player, target)

        self.currentPlayer += 1
        self.currentPlayer %= self.playerCount
        return True

    def tax(self, player):
        player.coins += 3

    def income(self, player):
        player.coins += 1

    def foreignAid(self, player):
        player.coins += 2

    def steal(self, player, target):
        player.coins += min(2, target.coins)
        target.coins -= min(2, target.coins)

    def exchange(self, player):
        newHand = []
        toChoose = []
        for card in player.cards:
            if card == -2:
                newHand.append(card)
            else:
                toChoose.append(card)
        toChoose.append(self.deck.draw())
        toChoose.append(self.deck.draw())
        # Ask player which of the cards in toChoose they want
        # Choose 2 - len(newHand) of them
        # newHand.append(choice) for each choice
        player.cards = newHand

        # player mentioned so that x assassinated y could be displayed
    def assass(self, player, target):
        self.loseCard(target)

    # player mentioned so that x couped y could be displayed
    def coup(self, player, target):
        self.loseCard(target)    
        

    # getBlocker requires player input
    def getBlocker(action, target):
        # returns card, blocker
        # card is integer
        # blocker is a player object
        if action == 1:
            # Ask target if they want to block with contessa (card 4)
            pass
        elif action == 3:
            # Give all players a chance to block with captain (card 3) or ambassador (card 2)
            pass
        elif action == 6:
            # Give all players a chance to block with duke (card 0)
            pass

        return -1, None

    # challenge method requires player input
    def challenge(self, action, target):
        if action > 4:
            return None
        ind = self.alive.index(target)
        # Start timer
        # send this message to each player:
        for i in range(self.playerCount):
            if i != ind:
                numLeft = 3 - self.cardsRemoved[action]
                totalLeft = 15 - sum(self.cardsRemoved) - self.alive[i].numCards - target.numCards
                for card in self.alive[i]:
                    if card == action:
                        numLeft -= 1
                prob = 1 - math.comb(totalLeft, numLeft) / math.comb(totalLeft + target.numCards, numLeft)
                # tell alive[i]
                pass
        # If someone clicks challenge in that time, that player object
        # Otherwise return None
        return None

    def resolveChallenge(self, challenger, personChallenged, action):
        if (action in personChallenged.cards):
            personChallenged.cards.remove(action)
            self.deck.add(action)
            personChallenged.cards.append(self.deck.draw())

            self.loseCard(challenger)
            return True
        else:
            self.loseCard(personChallenged)
            return False

    def loseCard(self, player):
        lostCard = player.lose_card()
        self.cardsRemoved[lostCard] += 1
        if not player.isAlive:
            self.playerCount -= 1
            ind = self.alive.index(player)
            self.dead.append(self.alive.pop(ind))
            if ind <= self.currentPlayer:
                # to offset adding 1
                self.currentPlayer -= 1

    # return true if you CAN'T steal at all
    def noSteal(self):
        for i in range(self.playerCount):
            if (i != self.currentPlayer and self.alive[i].coins > 0):
                return False
        return True

    # getChosenAct requires player input
    def getChosenAct(actions, player):
        # Ask player which action they want to take
        # Return an integer corresponding to the action
        pass

    # returns a player object
    def getTarget(self, action):
        if action == 1 or action == 7:
            return self.askForTarget()
        if action == 3:
            return self.askForTarget(True)
        return None

    def displayTargets(self, listOfPlayers):
        pass

    def displayAction(self, action, target):
        pass

    # returns a player object, requires input
    def askForTarget(self, captain = False):
        possibleTargets = []
        for i in range(self.playerCount):
            if (i != self.currentPlayer) and (not captain or self.alive[i].coins > 0):
                possibleTargets.append(i)
        self.displayTargets(possibleTargets)
        # Placeholder
        return None



            


