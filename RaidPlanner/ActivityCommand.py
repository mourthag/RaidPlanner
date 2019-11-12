import discord
import asyncio
import parsingutil
import datetime
import activity
import simplejson
import os

plannedActivities = {}


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

async def parse_activity(channel, author, args):
    cmd = args.pop(0)

    if cmd == "create":
        await parse_activity_create(channel, author, args)
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

    await channel.send("Unknown command. Please check the syntax with the '!help activity' command.")


async def parse_activity_create(channel, author, args):
    
    if len(args) < 3:
        await channel.send("Invalid number of arguments. Use command '!help activity' to get more information about the command syntax.")
        return

    #parse date and time
    try:
        date = parsingutil.parse_date(args[1])
        time = parsingutil.parse_time(args[2])
        date = date.replace(hour=time.hour, minute=time.minute, second=time.second)
    except ValueError:
        await channel.send("Invalid date or time. Please enter valid values.")
        return

    if len(args) > 3:
        name = ' '.join(args[3:])
    else:
        name = ""
        

    #parse type
    type = activity.activityType(args.pop(0))

    title = author.display_name + "'s " + name + " " + str(type)
    if type == activity.activityType.raid:
        newActivity = activity.createRaid(title, date, author)    
    elif type == activity.activityType.nightfall:
        newActivity = activity.createNightfall(title, date, author)
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

    #await msg.add_reaction('\u2705')

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
            success, error = serverActivity.add_player(author)
            if success:
                embed = serverActivity.get_status_embed()
                await channel.send("Succesfully joined activity!", embed=embed)
                return
            else:
                await channel.send(error)
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
            success, error = serverActivity.remove_player(author)
            if success:
                embed = serverActivity.get_status_embed()
                await channel.send("Succesfully left activity!", embed=embed)
                return
            else:
                await channel.send(error)
                return
    await channel.send("Cant find activity with ID: " + acitvityId)
