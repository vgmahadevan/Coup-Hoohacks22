import CoupDeck
import CoupPlayer

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
        self.deck = CoupDeck()

    def addPlayer(self, name):
        self.playerCount += 1
        self.alive.append(CoupPlayer(name))

    def deal(self):
        for i in range(self.playerCount):
            self.alive[i].cards[0] = self.deck.draw()
            self.alive[i].cards[1] = self.deck.draw()

    def takeTurn(self):
        player = self.alive[self.currentPlayer]
        possibleActions = player.getActions()
        if (3 in possibleActions and self.noSteal()):
            possibleActions.remove(3)
        action = self.getChosenAct(possibleActions, player)
        target = self.getTarget(action)
        self.displayAction(action, target)
        challenger = self.challenge(action, target)
        if challenger:
            actionWentThrough = self.resolveChallenge(challenger, player, action)
        if actionWentThrough:
            card, blocker = self.getBlocker(action, target)
            if card != -1:
                actionWentThrough = False
                challenger = self.challenge(card, blocker)
                if challenger:
                    actionWentThrough = not self.resolveChallenge(challenger, blocker, card)


        self.currentPlayer += 1
        self.currentPlayer %= self.playerCount

    def getBlocker(action, target):
        # returns card, blocker
        # card is integer
        # blocker is a player object
        if action == 1:
            # Ask target if they want to block with contessa
            pass
        elif action == 3:
            # Give all players a chance to block with captain or ambassador
            pass
        return -1, None

    def challenge(self, action, target):
        # Start timer
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
        player.lose_card()
        if not player.isAlive:
            self.playerCount -= 1
            ind = self.alive.index(player)
            self.dead.append(self.alive.pop(ind))
            if ind <= self.currentPlayer:
                # to offset adding 1
                self.currentPlayer -= 1

    def noSteal(self):
        for i in range(self.playerCount):
            if (i != self.currentPlayer and self.alive[i].coins > 0):
                return False
        return True

    def getChosenAct(actions, player):
        # Ask player which action they want to take
        # Return an integer corresponding to the action
        pass

    def getTarget(self, action):
        if action == 1 or action == 7:
            return self.askForTarget()
        if action == 3:
            return self.askForTarget(True)
        return -1

    def displayTargets(self, listOfPlayers):
        pass

    def displayAction(self, action, target):
        pass

    def askForTarget(self, captain = False):
        possibleTargets = []
        for i in range(self.playerCount):
            if (i != self.currentPlayer) and (not captain or self.alive[i].coins > 0):
                possibleTargets.append(i)
        self.displayTargets(possibleTargets)
        # Placeholder
        integer = -1
        return integer
            


