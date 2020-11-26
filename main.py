import discord
import pickle
import os.path
import os
import dbl
import aiohttp
import asyncio

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from random import randrange
from discord.ext import commands

globals()
SERVICE = ''
CREDS = None
driveFiles = {}
data = {}
bot = {}
snipe_message_id = None
snipe_message_content = None
snipe_message_author = None
snipe_message_attachment = None
snipe_message_guild = None
snipe_message_channel = None

# add sudo users (the developers)
SUDO_USERS = ['379269487532310530', '454342857239691306', '310860262624460801']

# discord embed colors
EMBED_COLORS = [
    discord.Colour.magenta(),
    discord.Colour.dark_teal(),
    discord.Colour.blue(),
    discord.Colour.dark_blue(),
    discord.Colour.dark_gold(),
    discord.Colour.dark_green(),
    discord.Colour.dark_grey(),
    discord.Colour.dark_magenta(),
    discord.Colour.dark_orange(),
    discord.Colour.dark_purple(),
    discord.Colour.dark_red(),
    discord.Colour.darker_grey(),
    discord.Colour.gold(),
    discord.Colour.green(),
    discord.Colour.orange(),
    discord.Colour.purple(),
    discord.Colour.magenta(),
]
randomColor = randrange(len(EMBED_COLORS))

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.appdata',
          'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file']

client = commands.Bot(command_prefix='~', status='Online', case_insensitive=True)
client.remove_command("help")
client.remove_command("timer")

#from google
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        CREDS = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not CREDS or not CREDS.valid:
    if CREDS and CREDS.expired and CREDS.refresh_token:
        CREDS.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        CREDS = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(CREDS, token)

SERVICE = build('drive', 'v3', credentials=CREDS)

# Call the Drive v3 API
results = SERVICE.files().list(
    pageSize=20, fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])

if not items:
    print('No files found.')
else:
    print('Files:')
    for item in items:
        driveFiles[item['name']] = item['id']

print(driveFiles)

@client.event
async def on_ready():
    game = discord.Game("~help")
    await client.change_presence(status=discord.Status.online, activity=game)
    print('We have logged in as {0.user}'.format(client))


def main():
    fileReadIntoDict("data.txt", data, " : ")
    print("done reading data : ")
    print(data)
    fileReadIntoDict("bot.txt", bot, " : ")
    print("done reading bot :")
    print(bot)

# reads the data files from Google drive. Data file is a .txt file stored
# in the following format with a new line for each server which **sets up** Passel
# ServerID : mode number | pins channel ID | any blacklisted channels separated by ' | '
def fileReadIntoDict(fileName, dictionary, separator):
    global SERVICE
    file = SERVICE.files().get(fileId=driveFiles[fileName]).execute()
    dataread = str(SERVICE.files().get_media(fileId=driveFiles[fileName]).execute())
    length = len(dataread)
    dataStripped = dataread[2: length - 1]

    dataList = dataStripped.split('\\n')
    f = open('tempfile.txt', 'w')

    for elem in dataList:
        f.write(elem)
        f.write('\n')
    f.close()

    f = open('tempfile.txt', 'r')
    with f as reader:
        line = reader.readline()
        while line != '':
            try:
                lineTuple = line.partition(separator)
                listVal = lineTuple[2].split(' | ')
                dictionary[int(lineTuple[0])] = listVal
                counter = int(lineTuple[0])
                line = reader.readline()
            except:
                dictionary[counter] += line
                line = reader.readline()

    for val in dictionary:
        for elem in dictionary[val]:
            if elem == '' or elem == "\n" :
                dictionary[val].remove(elem)

    f.close()


# file writes the data file
def fileWrite(dictionary, fileName):
    file = open(fileName, "w")
    for val in dictionary:
        try:
            file.write(str(val) + " : ")
            for num in dictionary[val]:
                if num != '' and num != "\n":
                    file.write(str(num).rstrip() + " | ")
            file.write("\n")
        except:
            print('Invalid when writing file.')
    file.close()

if __name__ == '__main__':
    main()


@client.event
async def on_message(message):
    if message.author == client.user  and str(message.channel.id) in str(data[message.guild.id]):
        await message.delete(delay=60)
        return

    if message.author == client.user:
        return

    if message.author.bot and str(message.channel.id) in str(data[message.guild.id]):
        delayTime = int(data[message.guild.id][0])
        await message.delete(delay=delayTime)

    await client.process_commands(message)


@client.command(name='help', pass_context=True)
async def _help(ctx):

    embedHelp = discord.Embed(
        title="**Commands**",
        colour=EMBED_COLORS[randomColor]
    )

    embedHelp.add_field(name="`~info` :", value="  *To get information about how Elimina is setup in this sever.*", inline=False)
    embedHelp.add_field(name="`~toggle` :  __(Admin only)__", value="  *Type in channel to activate or deactivate the bot in the respective channel.*", inline=False)
    embedHelp.add_field(name="`~purge` <number of messages>[optional]:", value="  *Type in channel to manually clear recent(or if specified, n number of) messages sent by bots*", inline=False)
    embedHelp.add_field(name="`~timer <time in seconds>` :  __(Admin Only)__", value="  *Change default timer after which the bot messages are deleted. Default: 15 seconds*", inline=False)
    embedHelp.add_field(name="`~invite` :", value="  *To provide an invite link for a Discord server.*", inline=False)
    embedHelp.add_field(name="`~ignore <bot>` :", value="*Add or Remove the bot(s) from server's Elimina whitelist*")
    embedHelp.add_field(name="`~snipe` :", value="*To show the last text message or image deleted by a user within a minute on the same channel. __Does not snipe messages sent by bots.__*")
    embedHelp.add_field(name='\u200B', value='\u200B')
    embedHelp.add_field(name="Support Server",value='*https://discord.gg/vFmFTjPpZ4*', inline=False)
    embedHelp.add_field(name="_Messages from Elimina are deleted after 1 minute in toggled on channels_",value='*For help contact: eliminabot@gmail.com*', inline=False)
    embedHelp.set_author(name='Elimina Bot', url="https://github.com/stoir/EliminaBot" , icon_url=client.user.avatar_url)
    embedHelp.set_footer(
        text="Requested by: " + ctx.message.author.name)
    await ctx.send(embed=embedHelp)


@client.event
async def on_guild_join(guild):
    data[guild.id] = ['5']
    print("Joined data ")
    print(data)
    update_data_file()

    guildsJoined = client.guilds
    embedJoin = discord.Embed(
        title="Joined " + guild.name,
        description="ID: " + str(guild.id),
        colour=discord.Colour.green(),
    )
    embedJoin.set_footer(text="Total Number of Servers: " + str(len(guildsJoined)))
    await client.get_guild(777063033301106728).get_channel(779045674557767680).send(embed=embedJoin)


@client.command(name='purge')
async def purge(ctx, count:int=300):
    if not ctx.author.guild_permissions.manage_messages:
        return
    try:
        msgs = await ctx.channel.purge(limit=count+1, before=ctx.message, check=lambda m: m.author.bot and not m.pinned)
    except discord.HTTPException:
        x = await ctx.send("Unable to delete the messages older than 14 days.")
        return await x.delete(delay=4)

    if not len(msgs):
        x = await ctx.send("No messages to delete!")
    else:
        x = await ctx.send(f"Successfully deleted **{len(msgs)}** messages sent by bots!")
    await ctx.message.delete()
    await x.delete(delay=4)

@client.command(name='toggle')
async def toggle(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        return

    try:
        channelBL = ctx.message.channel.id
        isWhitelisted = False

        if str(ctx.message.author.guild.id) in str(data):
            if str(channelBL) in data[ctx.message.author.guild.id]:
                isWhitelisted = True

        if isWhitelisted:
            channelIndex = data[ctx.message.author.guild.id].index(str(channelBL))
            data[ctx.message.author.guild.id][channelIndex] = ''

            await ctx.send("Successfully de-activated " + ctx.message.author.guild.get_channel(channelBL).mention)

        if not isWhitelisted:
            data[ctx.message.author.guild.id].append(str(channelBL))
            await ctx.send("Successfully activated " + ctx.message.author.guild.get_channel(channelBL).mention)

        update_data_file()

    except:
        return


@client.command(name='timer')
async def _timer(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        return

    time = ctx.message.content[7:]

    if not time.isdigit():
        await ctx.send("Invalid time. Must be between 1 and 300")
        return

    if int(time) <= 0 or int(time) > 300:
        await ctx.send("Invalid time. Must be between 1 and 300")
        return

    data[ctx.message.author.guild.id][0] = time
    await ctx.send("Changed timer to **" + data[ctx.message.author.guild.id][0] + " seconds.**")
    update_data_file()


@client.command(name='info')
async def info(ctx):

    embedInfo = discord.Embed(
        title="Server Setup Information",
        description="Elimina is a bot that can delete messages"
        ' sent from bot users after X number of seconds in toggled on channels. '
        "Messages can be deleted after 1 second to after 300 seconds (5 minutes)!\nUse `~help` for more information",
        colour=EMBED_COLORS[randomColor]
    )

    val = int(ctx.guild.id)
    mentionStr = ''
    for elem in data[val]:
        try:
            int(elem)
        except:
            continue
        if elem != '' and elem != "\n" and int(elem) > 300:
            try:
                mentionStr += ctx.guild.get_channel(int(elem)).mention + " "
            except:
                continue


    embedInfo.set_author(name='Elimina Bot', url="https://github.com/stoir/EliminaBot" , icon_url=client.user.avatar_url)

    botStr = ''
    for e in bot[val]:
        try:
            int(e)
        except:
            continue
        if e != '' and e != "\n" and int(e) > 300:
            try:
                mem = await ctx.guild.fetch_member(int(e))
                botStr += mem.mention + " "
            except:
                continue

    if mentionStr == '':
        embedInfo.add_field(name="This server has the following channels toggled on: ", value="No Channels toggled on use ~toggle", inline=False)
    else:
        embedInfo.add_field(name="This server has the following channels toggled on: ", value=mentionStr, inline=False)

    if botStr == '':
        embedInfo.add_field(name="This server has the following bots ignored: ", value="No bots are ignored ~ignore <@bot>", inline=False)
    else:
        embedInfo.add_field(name="This server has the following bots ignored: ", value=botStr, inline=False)

    embedInfo.add_field(name="Timer set at: __" + str(data[val][0]) + " seconds__", value="\u200b", inline=False)
    embedInfo.add_field(name="_Messages from Elimina are deleted after 1 minute in toggled on channels_",value='*For help contact: eliminabot@gmail.com*', inline=False)
    embedInfo.add_field(name="Support Server",value='*https://discord.gg/vFmFTjPpZ4*', inline=False)
    embedInfo.set_footer(text="Requested by: " + ctx.message.author.name + "\nAuthors: AyamDobhal#1672, moizmoizmoizmoiz#5923, sc#2714")
    await ctx.send(embed=embedInfo)

#https://discord.gg/vFmFTjPpZ4
def update_data_file():
   # rewrites data to the data.txt file
    fileWrite(dictionary=data, fileName="data.txt")
    file_metadata = {'name': 'data.txt'}

    media = MediaFileUpload('data.txt',
                            mimetype='text/plain')

    file = SERVICE.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()

    SERVICE.files().delete(fileId=driveFiles['data.txt']).execute()

    driveFiles['data.txt'] = file.get('id')

    if os.path.exists("data.txt"):
        os.remove("data.txt")
    else:
        print("The file does not exist")

def update_bot_file():
    fileWrite(dictionary=bot, fileName="bot.txt")
    file_metadata = {'name': 'bot.txt'}

    media = MediaFileUpload('bot.txt',
                            mimetype='text/plain')

    file = SERVICE.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()

    SERVICE.files().delete(fileId=driveFiles['bot.txt']).execute()

    driveFiles['bot.txt'] = file.get('id')

    if os.path.exists("bot.txt"):
        os.remove("bot.txt")
    else:
        print("The file does not exist")

@client.event
async def on_guild_remove(guild):
    data.pop(int(guild.id))
    print(data)
    update_data_file()

    guildsJoined = client.guilds
    embedLeave = discord.Embed(
        title="Left " + guild.name,
        description="ID: " + str(guild.id),
        colour=discord.Colour.dark_red()
    )
    embedLeave.add_field(name="Support Server",value='*https://discord.gg/vFmFTjPpZ4*', inline=False)
    embedLeave.set_footer(text="Total Number of Servers: " + str(len(guildsJoined)))
    await client.get_guild(777063033301106728).get_channel(779045674557767680).send(embed=embedLeave)


@client.command(name='invite', pass_context=True)
async def invite(ctx):
    embed_invite = discord.Embed(
        title="Click here to invite me",
        colour=EMBED_COLORS[randomColor],
        url='https://discord.com/api/oauth2/authorize?client_id=777575449957498890&permissions=90112&scope=bot'
    )
    embed_invite.add_field(name="Support Server",value='*https://discord.gg/vFmFTjPpZ4*', inline=False)
    embed_invite.set_footer(text="\nFor help contact eliminabot@gmail.com")
    await ctx.send(embed=embed_invite)

@client.command(name='ignore', pass_context=True)
async def ignore(ctx, user: discord.User):
    if not ctx.message.author.guild_permissions.administrator:
        return

    if not user.bot:
        await ctx.send("The user mentioned is not a bot!")
        return

    try:
        userBL = user.id
        isWhitelisted = False

        if str(ctx.message.author.guild.id) in str(bot):
            if str(userBL) in bot[ctx.message.author.guild.id]:
                isWhitelisted = True

        if isWhitelisted:
            botIndex = bot[ctx.message.author.guild.id].index(str(userBL))
            bot[ctx.message.author.guild.id][botIndex] = ''
            await ctx.send("Successfully un-ignored " + user.mention)

        if not isWhitelisted:
            bot[ctx.message.author.guild.id].append(str(userBL))
            await ctx.send("successfully ignored " + user.mention)

        update_bot_file()

    except:
        return

@client.event
async def on_message_delete(message):

    if message.author.bot:
        return
    
    global snipe_message_author
    global snipe_message_content
    global snipe_message_id
    global snipe_message_attachment
    global snipe_message_guild
    global snipe_message_channel

    snipe_message_id = message.id
    snipe_message_author = message.author
    snipe_message_content = message.content
    snipe_message_guild = message.guild
    snipe_message_channel = message.channel

    if message.attachments is not None:
        snipe_message_attachment = message.attachments[0].proxy_url
    await asyncio.sleep(60)

    if message.id == snipe_message_id:
        snipe_message_id = None
        snipe_message_author = None
        snipe_message_content = None
        snipe_message_attachment = None
        snipe_message_guild = None
        snipe_message_channel = None

@client.command(name='snipe')
async def snipe(ctx):

    global snipe_message_attachment

    has_snipe = False
    author_roles = ctx.author.roles
    for role in author_roles:
        if role.name.lower() == 'sniper':
            has_snipe = True

    if not ctx.author.guild_permissions.administrator and not has_snipe:
        x = await ctx.send("You either need a role called `sniper` or be an `Administrator` to snipe.")
        await x.delete(delay=4)
        return

    if snipe_message_guild != ctx.guild or snipe_message_channel != ctx.channel or snipe_message_content == None:
        x = await ctx.send("There is nothing to snipe!")
        await x.delete(delay=4)
        return
    embed = discord.Embed(description=str(snipe_message_content), colour=EMBED_COLORS[randomColor])
    embed.set_footer(text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
    if snipe_message_attachment is not None:
        embed.set_image(url=snipe_message_attachment)
    embed.set_author(name=f"{snipe_message_author.name}#{snipe_message_author.discriminator}", icon_url=snipe_message_author.avatar_url)
    await ctx.send(embed=embed)
    snipe_message_attachment = None

client.run('TOKEN')
