import discord
import asyncio
import datetime
import activity
import parsingutil

client = discord.Client()

plannedRaids = {}

@client.event
async def on_ready():
    print("Eingelogt als")
    print(client.user.name)
    print(client.user.id)

    statusGame = discord.Game("!create raid today 8pm")
    await client.change_presence(status=discord.Status.online, activity=statusGame)
    
@client.event
async def on_message(message):
    args = message.content.split(" ")
    cmd = args.pop(0)

    channel = message.channel
    author = message.author

    if cmd == "!create":
        await parse_create(channel, author, args)


async def parse_create(channel, author, args):
    
    type = args[0]
    title = ""

    if type == "raid":
        name = author.display_name
        title=name+"'s Raid"

    date = parsingutil.parse_date(args[1])

    time = parsingutil.parse_time(args[2])

    date = date.replace(hour=time.hour, minute=time.minute, second=time.second)

    newActivity = activity.createRaid(title, date)
    result = newActivity.add_player(author)

    print(result)

    plannedGuildRaids = plannedRaids.get(channel.guild.id)
    if plannedGuildRaids == None:
        plannedRaids[channel.guild.id] = (newActivity)
    else:
        plannedRaids[channel.guild.id].append(newActivity)

    embed = newActivity.print_status()

    msg = await channel.send(embed=embed)

    await msg.add_reaction('\u2705')


client.run("NjQxNzc2MzYwMzg5NjA3NDMz.XcQFHQ.59BuUJztCiQ8-tVfbQAL8i2RKTM")