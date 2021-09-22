from . import settings


class Player():
    def __init__(self, health=3, bombRange=2, max_bomb_range=5, trapCount=1, initX=1, initY=1, name=''):
        self.__health = health
        self.__bombRange = bombRange
        self.__trapCount = trapCount
        self.__HealthUpgradeCount = 0
        self.__bombPlaceCount = 0
        self.__trapPlaceCount = 0
        self.__max_bomb_range = max_bomb_range
        self.x = initX
        self.y = initY
        self.name = name

    # Upgrades

    def upgradeHealth(self, value=1):
        self.__health += value
        self.__HealthUpgradeCount += 1

    def upgradeBombRange(self, value=1):
        self.__bombRange = min(self.__bombRange + value, self.__max_bomb_range)

    def upgradeTrapCount(self):
        self.__trapCount += 1

    # Getters

    def getHealth(self):
        return self.__health

    def getBombRange(self):
        return self.__bombRange

    def getTrapCount(self):
        return self.__trapCount

    def getPosition(self):
        return (self.x, self.y)

    def getHealthUpgradeCount(self):
        return self.__HealthUpgradeCount

    def getBombPlaceCount(self):
        return self.__bombPlaceCount

    def getTrapPlaceCount(self):
        return self.__trapPlaceCount

    # Helpers

    def damage(self):
        if self.isAlive():
            self.__health -= 1
        return self.isAlive()

    def isAlive(self):
        return self.__health > 0

    def placeTrap(self):
        if self.isTrapAvailable():
            self.__trapCount -= 1
            self.__trapPlaceCount += 1
            return True
        return False

    def placeBomb(self):
        self.__bombPlaceCount += 1

    def isTrapAvailable(self):
        return self.__trapCount > 0
