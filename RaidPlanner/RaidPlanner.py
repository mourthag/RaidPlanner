import discord
import asyncio
import datetime
import parsingutil
import random
import ActivityCommand

client = discord.Client()

reminderUpdateTimedelta = datetime.timedelta(seconds=60)
cleanupUpdateTimedelta = datetime.timedelta(seconds=60)

defaultRemindingTimedelta = datetime.timedelta(minutes=30)
userRemindSettings = {}

defaultTimeoutTimedelta = datetime.timedelta(hours=1)
serverTimeoutSettings = {}

commandExamples = ("!create raid today 8pm", "!activity list raid", "!activity leave", "!activity join", "!activity server", "!activity server nightfall")

async def status_loop():
    while True:
        statusGame = discord.Game(random.choice(commandExamples))
        await client.change_presence(status=discord.Status.online, activity=statusGame)
        await asyncio.sleep(10)


async def reminder_loop():
    while True:
        now = datetime.datetime.now()

        for guild in ActivityCommand.plannedActivities:
            serverActivities = ActivityCommand.plannedActivities.get(guild)
            for serverActivity in serverActivities:

                embed = serverActivity.get_status_embed()

                for member in serverActivity.get_members():
                    
                    timedelta = userRemindSettings.get(member.id)
                    if timedelta == None:
                        timedelta = defaultRemindingTimedelta

                    if now + timedelta > serverActivity.get_date() and now + timedelta - reminderUpdateTimedelta < serverActivity.get_date():
                        msgText = "Heads up: You have an activity scheduled starting within the next " + str(timedelta.seconds / 60) + " minutes."                    
                        channel = member.dm_channel
                        if channel == None:
                            channel = await member.create_dm()
                        await channel.send(msgText, embed=embed)


        await asyncio.sleep(reminderUpdateTimedelta.seconds)


async def cleanup_loop():
    while True:
        activitiesToRemove = []
        now = datetime.datetime.now()

        for guild in ActivityCommand.plannedActivities:
            serverActivities = ActivityCommand.plannedActivities.get(guild)

            serverTimeout = serverTimeoutSettings.get(guild)
            if serverTimeout == None:
                serverTimeout = defaultTimeoutTimedelta

            for serverActivity in serverActivities:
                if now - serverTimeout > serverActivity.get_date():
                    activitiesToRemove.append(serverActivity)

        for activ in activitiesToRemove:
            for guild in ActivityCommand.plannedActivities:
                ActivityCommand.plannedActivities.get(guild).remove(activ)

        ActivityCommand.save_activities('ActivityBackup.txt')
        await asyncio.sleep(cleanupUpdateTimedelta.seconds)


@client.event
async def on_ready():
    print("Eingelogt als")
    print(client.user.name)
    print(client.user.id)

    ActivityCommand.try_load_file('ActivityBackup.txt', client)

    client.loop.create_task(status_loop())
    client.loop.create_task(reminder_loop())
    client.loop.create_task(cleanup_loop())
    
@client.event
async def on_message(message):
    args = message.content.split(" ")
    cmd = args.pop(0)

    channel = message.channel
    author = message.author

    if cmd == "!activity":
        await ActivityCommand.parse_activity(channel, author, args)


client.run("NjQxNzc2MzYwMzg5NjA3NDMz.XcQFHQ.59BuUJztCiQ8-tVfbQAL8i2RKTM")