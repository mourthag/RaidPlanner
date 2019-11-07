import discord
import datetime
import uuid
from enum import Enum

def createRaid(name, date, owner):
    return activity(name, date, 6, activityType.raid, owner)

def createNightfall(name, date, owner):
    return activity(name, date, 3, activityType.nightfall, owner)

class activityType(Enum):

    raid="raid"
    nightfall="nightfall"

    def __str__(self):
        return self.value


class activity(object):
    """
    Instances of an activity represent a planned activity with a unique id, planned date, members and the type of the activity.


    """
    __slots__ = ('name', 'date', 'numPlayers', 'members', 'type', 'id', 'owner')

    def __init__(self, name, date, numPlayers, type, owner):
        self.name = name
        self.date = date
        self.numPlayers = numPlayers
        self.type = type
        self.members = []
        self.id = uuid.uuid1()
        self.owner = owner

    def add_player(self, member):

        if member in self.members:
            return False, "Already in group!"

        if len(self.members) < self.numPlayers:
            self.members.append(member)

            return True, "Success!"
        else:
            return False, "Group already full!"

    def remove_player(self, member):
        if member == self.owner:
            return False, "The owner can't leave the group. Transfer ownage first with '!activity ownage' or cancel the activity with '!activity cancel'."
        if member in self.members:
            self.members.remove(member)
            return True, "Success!"
        else:
            return False, "User: " + member.display_name + " did not join the group yet."



    def get_status_embed(self):

        memberList = ""

        for i in range(self.numPlayers):
            memberList += str(i+1) + ". "
            if i < len(self.members):
                memberList += "**" + self.members[i].display_name + "**"
            else:
                memberList += "*open spot*"
            memberList += "\n"

        embed = discord.Embed(title=self.name)
        embed.add_field(name="Planned date:", value=self.date.ctime(), inline=False)
        embed.add_field(name="Members: (" + str(len(self.members)) + "/" + str(self.numPlayers) + ")", value=memberList, inline=False)
        embed.add_field(name="ID: ", value=str(self.id.hex))

        return embed

        