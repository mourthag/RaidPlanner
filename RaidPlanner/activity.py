class activity(object):
    
    __slots__ = ('name', 'date', 'numPlayers', 'playerIds')

    def __init__(self, name, date, numPlayers):
        self.name = name
        self.date = date
        self.numPlayers = numPlayers
        playerIds = ()

    def add_player(self, playerId):
        if self.playerIds.length < self.numPlayers:
            playerIds.append(playerId)
            return True, "Success"
        else:
            return False, "Group already full"