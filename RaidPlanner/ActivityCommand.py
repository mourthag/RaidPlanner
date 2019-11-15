import discord
import asyncio
import parsingutil
import datetime
import activity
import simplejson
import os

plannedActivities = {}

joinEmoji = '\u2705'

def try_load_file(file, client, additive=False):
    if os.path.isfile(file) == False:
        print("Can't find log at: " + file)
        return

    with open(file, 'r') as json_file:
        data = simplejson.load(json_file)

        for guildId in data['guilds']:
            guild = discord.utils.find(lambda g: g.id == int(guildId), client.guilds)

            if guild == None:
                print("Can't find guild ID:" + guildId)
                continue

            activitiesData = data['guilds'][guildId]

            parsedActivities = []

            for activityData in activitiesData:

                parsedActivityData = activityData

                parsedOwner = discord.utils.find(lambda m: m.id == activityData['owner'], guild.members)
                if parsedOwner == None:
                    print("Can't find member ID: " + activityData['owner'])
                    continue
                parsedActivityData['owner'] = parsedOwner

                parsedMembers = []
                for memberId in activityData['members']:
                    parsedMember = discord.utils.find(lambda m: m.id == activityData['members'][memberId], guild.members)
                    if parsedMember == None:
                        print("Can't find member ID: " + memberId)
                        continue
                    parsedMembers.append(parsedMember)
                parsedActivityData['members'] = parsedMembers
            
                parsedActivity = activity.from_json(parsedActivityData)
                parsedActivities.append(parsedActivity)


            plannedGuildActivities = plannedActivities.get(id)

            if plannedGuildActivities == None or additive == False:
                plannedActivities[int(guildId)] = parsedActivities
            else:
                plannedActivities[int(guildId)].append(parsedActivities)

def save_activities(file):

    data = {}
    data['guilds'] = plannedActivities
    json_string = simplejson.dumps(data, separators=(',', ':'), indent=4, for_json=True)

    with open(file, 'w+') as json_file:
        json_file.write(json_string)

def find_activity_by_id(activityId, guildId=None):

    if guildId == None:
        for availableGuildId in plannedActivities:
            guildActivities = plannedActivities[availableGuildId]

            foundActivity = discord.utils.find(lambda a: str(a.id.hex) == activityId, guildActivities)
            if foundActivity != None:
                return foundActivity
        return None
    else:
        guildActivities = plannedActivities[guildId]
        return discord.utils.find(lambda a: str(a.id.hex) == activityId, guildActivities)

async def parse_reaction(reaction, author):
    
    message = reaction.message
    embeds = message.embeds

    activityId = None

    for embed in embeds:
        embedFields = embed.fields

        idField = discord.utils.find(lambda e: e.name == "ID", embedFields)

        if activityId != None:
            continue

        activityId = idField.value

    if activityId == None:
        return

    parsedActivity = find_activity_by_id(activityId, message.channel.guild.id)

    if reaction.emoji == joinEmoji:
        success, message = parsedActivity.add_player(author)
        authorMention = "<@" + str(author.id) + "> "
        if success:
            embed = parsedActivity.get_status_embed()
            await message.channel.send(authorMention + "Succesfully joined activity!", embed=embed)
            return
        else:
            await message.channel.send(authorMention + message)
            return



async def parse_activity(channel, author, args):
    cmd = args.pop(0)

    if cmd == "create":
        await parse_activity_create(channel, author, args)
        return

    if cmd == "reschedule":
        await parse_activity_reschedule(channel, author, args)
        return

    if cmd == "list":
        await parse_activity_list(channel, author, args)
        return

    if cmd == "server":
        await parse_activity_server(channel, args)
        return

    if cmd == "join":
        await parse_activity_join(channel, author, args)
        return

    if cmd == "leave":
        await parse_activity_leave(channel, author, args)
        return
    
    if cmd == "cancel":
        await parse_activity_cancel(channel, author, args)
        return

    await channel.send("Unknown command. Please check the syntax with the '!help activity' command.")


async def parse_activity_create(channel, author, args):
    
    if len(args) < 3:
        await channel.send("Invalid number of arguments. Use command '!help activity' to get more information about the command syntax.")
        return
    
    #parse type
    type = activity.activityType(args.pop(0))

    #parse date and time
    try:
        date = parsingutil.parse_date(args.pop(0))
        time = parsingutil.parse_time(args.pop(0))
        date = date.replace(hour=time.hour, minute=time.minute, second=time.second)
    except ValueError:
        await channel.send("Invalid date or time. Please enter valid values.")
        return

    if type == activity.activityType.custom:
        numPlayers = int(args.pop(0))


    if len(args) > 0:
        name = ' '.join(args[0:])
    else:
        name = ""

        
    if type == activity.activityType.custom:        
        title = author.display_name + "'s " + name
    else:
        title = author.display_name + "'s " + name + " " + str(type)

    if type == activity.activityType.raid:
        newActivity = activity.createRaid(title, date, author)    
    elif type == activity.activityType.nightfall:
        newActivity = activity.createNightfall(title, date, author)    
    elif type == activity.activityType.menagerie:
        newActivity = activity.createMenagerie(title, date, author)
    elif type == activity.activityType.dungeon:
        newActivity = activity.createDungeon(title, date, author)
    elif type == activity.activityType.custom:
        newActivity = activity.createCustom(title, date, author, numPlayers)
    else:
        await channel.send("Unknown activity type. Please check the syntax with the '!help create' command.")
    
    success, error = newActivity.add_player(author)

    if success == False:
        print(error)
        return

    plannedGuildRaids = plannedActivities.get(channel.guild.id)
    if plannedGuildRaids == None:
        plannedActivities[channel.guild.id] = [newActivity]
    else:
        plannedActivities[channel.guild.id].append(newActivity)

    save_activities("ActivityBackup.txt")

    embed = newActivity.get_status_embed()

    msg = await channel.send( "<@" + str(author.id) + "> created an activity. You can join by typing '!activity join " + str(newActivity.id.hex) + "'.", embed=embed)

    await msg.add_reaction(joinEmoji)

async def parse_activity_reschedule(channel, author, args):
    acitvityId = args.pop(0)

    #parse date and time
    try:
        date = parsingutil.parse_date(args.pop(0))
        time = parsingutil.parse_time(args.pop(0))
        date = date.replace(hour=time.hour, minute=time.minute, second=time.second)
    except ValueError:
        await channel.send("Invalid date or time. Please enter valid values.")
        return

    if plannedActivities.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return

    serverActivities = plannedActivities.get(channel.guild.id)
    
    for serverActivity in serverActivities:

        if serverActivity.id.hex == acitvityId:
            if serverActivity.owner == author:
                serverActivity.date = date
                embed = serverActivity.get_status_embed()
                await channel.send("Succesfully rescheduled activity!", embed=embed)
                return
            else:
                await channel.send("Only the activity owner can reschedule the activity.")
                return
    await channel.send("Cant find activity with ID: " + acitvityId)


async def parse_activity_list(channel, author, args):
    if plannedActivities.get(channel.guild.id) == None:
        await channel.send("There are no raids planned on this server yet!")
        return
    userActivities = filter(lambda x: author in x.members, plannedActivities.get(channel.guild.id))

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
    if plannedActivities.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return
    serverActivities = plannedActivities.get(channel.guild.id)
    
    hasEntries = False
    if len(args) > 1:
        await channel.send("Invalid number of arguments. Use command '!help activity' to get more information about the command syntax.")
        return
    elif len(args) == 1:
        activityType = activity.activityType(args.pop(0))
    else:
        activityType = None

    for serverActivity in serverActivities:

        if activityType != None and serverActivity.type != activityType:
            continue

        embed = serverActivity.get_status_embed()
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

    if plannedActivities.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return

    serverActivities = plannedActivities.get(channel.guild.id)
    
    for serverActivity in serverActivities:

        if serverActivity.id.hex == acitvityId:
            success, message = serverActivity.add_player(author)
            if success:
                embed = serverActivity.get_status_embed()
                await channel.send("Succesfully joined activity!", embed=embed)
                return
            else:
                await channel.send(message)
                return
    await channel.send("Cant find activity with ID: " + acitvityId)

async def parse_activity_leave(channel, author, args):
    acitvityId = args.pop(0)

    if plannedActivities.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return

    serverActivities = plannedActivities.get(channel.guild.id)
    
    for serverActivity in serverActivities:

        if serverActivity.id.hex == acitvityId:
            success, message = serverActivity.remove_player(author)
            if success:
                embed = serverActivity.get_status_embed()
                await channel.send("Succesfully left activity!", embed=embed)
                return
            else:
                await channel.send(message)
                return
    await channel.send("Cant find activity with ID: " + acitvityId)

async def parse_activity_cancel(channel, author, args):
    acitvityId = args.pop(0)

    if plannedActivities.get(channel.guild.id) == None:
        await channel.send("There are no activities planned on this server yet!")
        return

    serverActivities = plannedActivities.get(channel.guild.id)
    
    for i in range(len(serverActivities)):
        serverActivity = serverActivities[i]
        if serverActivity.id.hex == acitvityId:
            if serverActivity.owner == author:
                del plannedActivities[channel.guild.id][i]
                save_activities("ActivityBackup.txt")
                await channel.send("Cancelled activity: " + acitvityId)
                return
            else:
                await channel.send("Only the activity owner can cancel an activity!")
                return
    await channel.send("Cant find activity with ID: " + acitvityId)