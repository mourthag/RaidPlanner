import discord
import datetime
import uuid
from enum import Enum
import simplejson

def createRaid(name, date, owner):
    return activity(name, date, 6, activityType.raid, owner)

def createNightfall(name, date, owner):
    return activity(name, date, 3, activityType.nightfall, owner)

def createMenagerie(name, date, owner):
    return activity(name, date, 3, activityType.menagerie, owner)

def createDungeon(name, date, owner):
    return activity(name, date, 3, activityType.dungeon, owner)

def createCustom(name, date, owner, numPlayers):
    return activity(name, date, numPlayers, activityType.custom, owner)

def from_json(json):

    date = datetime.datetime.strptime(json['date'], "%Y-%m-%d %H:%M:%S")

    parsedActivity = activity(json['name'], date, json['numPlayers'], json['type'], json['owner'], json['id'])

    for member in json['members']:
        parsedActivity.add_player(member)

    return parsedActivity

class activityType(Enum):

    raid="raid"
    nightfall="nightfall"
    menagerie="menagerie"
    dungeon="dungeon"
    custom="custom"

    def __str__(self):
        return self.value


class activity(object):
    """
    Instances of an activity represent a planned activity with a unique id, planned date, members and the type of the activity.


    """
    __slots__ = ('name', 'date', 'numPlayers', 'members', 'type', 'id', 'owner')

    def __init__(self, name, date, numPlayers, type, owner, id=None):
        self.name = name
        self.date = date
        self.numPlayers = numPlayers
        self.type = type
        self.members = []
        if id == None:
            self.id = uuid.uuid1()
        else:
            self.id = uuid.UUID(id)
        self.owner = owner

    def __serialize_members__(self):
        result = {}
        for i in range(len(self.members)):
            result[str(i)] = self.members[i].id
        return result

    def __json__(self):
        test = {
            'id' : self.id.hex,
            'name': self.name,
            'date' : self.date.strftime("%Y-%m-%d %H:%M:%S"),
            'type' : str(self.type),
            'owner' : self.owner.id,
            'numPlayers' : self.numPlayers,
            'members' : self.__serialize_members__(),
            }
        return test

    for_json = __json__

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

    def get_members(self):
        return self.members

    def get_date(self):
        return self.date

    def get_status_embed(self):

        memberList = ""

        for i in range(self.numPlayers):
            memberList += str(i+1) + ". "
            if i < len(self.members):
                memberList += "<@" + str(self.members[i].id) + ">"
            else:
                memberList += "*open spot*"
            memberList += "\n"

        if self.date > datetime.datetime.now():
            color = discord.colour.Color.green()
        else:
            color = discord.colour.Color.red()

        embed = discord.Embed(title=self.name, color=color)
        embed.add_field(name="Planned date:", value=self.date.ctime(), inline=False)
        embed.add_field(name="Members: (" + str(len(self.members)) + "/" + str(self.numPlayers) + ")", value=memberList, inline=False)
        embed.add_field(name="ID", value=str(self.id.hex))

        return embed

        