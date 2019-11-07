import discord
import asyncio
import datetime
import re
import activity
import parsingutil

client = discord.Client()

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

    if cmd == "!create":
        await parse_create(channel, args)


async def parse_create(channel, args):
    
    date = parsingutil.parse_date(args[1])

    time = parsingutil.parse_time(args[2])

    date = date.replace(hour=time.hour, minute=time.minute, second=time.second)

    await channel.send(date.ctime())


client.run("NjQxNzc2MzYwMzg5NjA3NDMz.XcQFHQ.59BuUJztCiQ8-tVfbQAL8i2RKTM")