import discord
import datetime
from enum import Enum

def createRaid(name, date):
    return activity(name, date, 6, activityType.raid)

class activityType(Enum):

    raid="Raid"
    nightfall="Nightfall"

    def __str__(self):
        return self.value

class activity(object):
    
    __slots__ = ('name', 'date', 'numPlayers', 'members', 'type')

    def __init__(self, name, date, numPlayers, type):
        self.name = name
        self.date = date
        self.numPlayers = numPlayers
        self.type = type
        self.members = []

    def add_player(self, member):
        if len(self.members) < self.numPlayers:
            self.members.append(member)
            return True, "Success"
        else:
            return False, "Group already full"

    def print_status(self):

        memberList = ""

        for i in range(self.numPlayers):
            memberList += str(i+1) + ". "
            if i < len(self.members):
                memberList += "**" + self.members[i].display_name + "**"
            else:
                memberList += "*still open*"
            memberList += "\n"

        embed = discord.Embed(title=self.name)
        embed.add_field(name="Planned date:", value=self.date.ctime(), inline=False)
        embed.add_field(name="Members:", value=memberList, inline=False)

        return embed

        