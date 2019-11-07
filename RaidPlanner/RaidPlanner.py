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
    if cmd == "!activity":
        await parse_activity(channel, author, args)


async def parse_create(channel, author, args):
    
    if len(args) < 3:
        await channel.send("Invalid number of arguments. Use command '!help create' to get more information about the command syntax.")
        return

    #parse date and time
    date = parsingutil.parse_date(args[1])
    time = parsingutil.parse_time(args[2])
    date = date.replace(hour=time.hour, minute=time.minute, second=time.second)

    if len(args) > 3:
        name = ' '.join(args[3:])
    else:
        name = ""
        

    #parse type
    type = activity.activityType(args.pop(0))

    title = author.display_name + "'s " + name + " " + str(type)
    if type == activity.activityType.raid:
        newActivity = activity.createRaid(title, date)    
    elif type == activity.activityType.nightfall:
        newActivity = activity.createNightfall(title, date)
    else:
        await channel.send("Unknown activity type. Please check the syntax with the '!help create' command.")
    
    success, error = newActivity.add_player(author)

    if success == False:
        print(error)
        return

    plannedGuildRaids = plannedRaids.get(channel.guild.id)
    if plannedGuildRaids == None:
        plannedRaids[channel.guild.id] = [newActivity]
    else:
        plannedRaids[channel.guild.id].append(newActivity)

    embed = newActivity.get_status_embed()

    msg = await channel.send(embed=embed)

    #await msg.add_reaction('\u2705')


async def parse_activity(channel, author, args):
    cmd = args.pop(0)

    if cmd == "list":
        await parse_activity_list(channel, author, args)
        return

    if cmd == "server":
        await parse_activity_server(channel, args)
        return

    if cmd == "join":
        await parse_activity_join(channel, author, args)
        return

    await channel.send("Unknown command. Please check the syntax with the '!help activity' command.")

async def parse_activity_list(channel, author, args):
    if plannedRaids.get(channel.guild.id) == None:
        await channel.send("There are no raids planned on this server yet!")
        return
    userActivities = filter(lambda x: author in x.members, plannedRaids.get(channel.guild.id))

    if len(args) > 1:
        await channel.send("Invalid number of arguments. Use command '!help activity' to get more information about the command syntax.")
        return
    elif len(args) == 1:
        activityType = activity.activityType(args.pop(0))
    else:
        activityType = None

    hasEntries = False
    for userActivity in userActivities:
        
        if activityType != None and userActivity.type != activityType:
            continue

        embed = userActivity.get_status_embed()
        msg = await channel.send(embed=embed)
        hasEntries=True
    
    if hasEntries == False:
        if activityType != None:
            activitystr = str(activityType) + "s"
        else:
            activitystr = "activities"
        await channel.send("You aren't a member for any " + activitystr + " planned on this server yet!") 


async def parse_activity_server(channel, args):
    if plannedRaids.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return
    activities = plannedRaids.get(channel.guild.id)
    
    hasEntries = False
    if len(args) > 1:
        await channel.send("Invalid number of arguments. Use command '!help activity' to get more information about the command syntax.")
        return
    elif len(args) == 1:
        activityType = activity.activityType(args.pop(0))
    else:
        activityType = None

    for i in range(len(activities)):

        if activityType != None and activities[i].type != activityType:
            continue

        embed = activities[i].get_status_embed()
        msg = await channel.send(embed=embed)
        hasEntries = True

    if hasEntries == False:        
        if activityType != None:
            activitystr = str(activityType) + "s"
        else:
            activitystr = "activities"
            
        await channel.send("There are no " + activitystr + " planned on this server yet!") 
        


async def parse_activity_join(channel, author, args):
    acitvityId = args.pop(0)

    if plannedRaids.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return

    serverActivities = plannedRaids.get(channel.guild.id)
    
    for i in range(len(serverActivities)):
        serverActivity = serverActivities[i]

        if serverActivity.id.hex == acitvityId:
            success, error = serverActivity.add_player(author)
            if success:
                embed = serverActivity.get_status_embed()
                await channel.send("Succesfully joined activity!", embed=embed)
                return
            else:
                await channel.send(error)
                return
    await channel.send("Cant find activity with ID: " + acitvityId)


client.run("NjQxNzc2MzYwMzg5NjA3NDMz.XcQFHQ.59BuUJztCiQ8-tVfbQAL8i2RKTM")