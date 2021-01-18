import discord
import pickle
import os

from discord.ext import commands
from discord import Embed
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient import discovery

from bot.utils.utils import SCOPES, COLORS

globals()
SERVICE = None
SERVICESHEET = None
CREDS = None
SHEETID = 'DATASHEETID'

DRIVE_FILES = {}
DATA = {}
BOT = {}

def data_update(guildID):
    global SHEETID
    global SERVICESHEET

    #delete old data
    dataList = list(DATA)
    dataidx = str(dataList.index(str(guildID)) + 2)
    range = 'Sheet1!A' + dataidx + ':AAA' + dataidx
    clear_values_request_body = { }
    request = SERVICESHEET.spreadsheets().values().clear(spreadsheetId=SHEETID, range=range, body=clear_values_request_body)
    request.execute()

    #append new data
    vals = DATA.get(str(guildID))
    vals.insert(0, str(guildID))
    range = 'Sheet1!A2'
    value_range_body = {'majorDimension': 'ROWS', 'values': [vals]}
    request = SERVICESHEET.spreadsheets().values().append(spreadsheetId=SHEETID, valueInputOption='RAW',range=range, body=value_range_body)
    request.execute()
    vals.remove(str(guildID))

def bot_update(guildID):
    global SHEETID
    global SERVICESHEET

    #delete old data
    dataList = list(BOT)
    dataidx = str(dataList.index(str(guildID)) + 2)
    range = 'Sheet2!A' + dataidx + ':AAA' + dataidx
    clear_values_request_body = { }
    request = SERVICESHEET.spreadsheets().values().clear(spreadsheetId=SHEETID, range=range, body=clear_values_request_body)
    request.execute()

    #append new data
    vals = BOT.get(str(guildID))
    vals.insert(0, str(guildID))
    range = 'Sheet2!A2'
    value_range_body = {'majorDimension': 'ROWS', 'values': [vals]}
    request = SERVICESHEET.spreadsheets().values().append(spreadsheetId=SHEETID, valueInputOption='RAW',range=range, body=value_range_body)
    request.execute()
    vals.remove(str(guildID))


def fileHandler():
    global CREDS
    global SERVICE
    global SHEETID
    global SERVICESHEET

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            CREDS = pickle.load(token)
    if not CREDS or not CREDS.valid:
        if CREDS and CREDS.expired and CREDS.refresh_token:
            CREDS.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            CREDS = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(CREDS, token)
    SERVICE = build('drive', 'v3', credentials=CREDS)

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            CREDS = pickle.load(token)
    if not CREDS or not CREDS.valid:
        if CREDS and CREDS.expired and CREDS.refresh_token:
            CREDS.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_sheets.json', SCOPES)
            CREDS = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(CREDS, token)
    # DO NOT DELETE
    results = SERVICE.files().list(pageSize=20, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            DRIVE_FILES[item['name']] = item['id']
    print(DRIVE_FILES)

    #build sheets
    SERVICESHEET = discovery.build('sheets', 'v4', credentials=CREDS)

    ranges = ["Sheet1!A2:AAA1000"]
    request = SERVICESHEET.spreadsheets().values().batchGet(spreadsheetId=SHEETID, ranges=ranges)
    response = request.execute()
    dataArr = response.get('valueRanges')[0].get('values') #data get values

    idx = 0
    for row in dataArr:
        try:
            DATA[dataArr[idx][0]] = dataArr[idx][1:]
            idx += 1
        except:
            idx += 1

    ranges = ["Sheet2!A2:AAA1000"]
    request = SERVICESHEET.spreadsheets().values().batchGet(spreadsheetId=SHEETID, ranges=ranges)
    response = request.execute()
    botArr = response.get('valueRanges')[0].get('values') #data get values

    idx = 0
    for row in botArr:
        try:
            BOT[dataArr[idx][0]] = botArr[idx][1:]
            idx += 1
        except:
            idx += 1

class Servers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        global SHEETID, SERVICESHEET

        fileHandler()

        guilds = self.bot.guilds
        game = discord.Game(f".help | watching {len(guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

        DATA[str(guild.id)] = ['5', '1']
        BOT[str(guild.id)] = []

        range = 'Sheet1!A2'
        value_range_body = {'majorDimension': 'ROWS', 'values': [[str(guild.id), '5', '1']]}
        request = SERVICESHEET.spreadsheets().values().append(spreadsheetId=SHEETID, valueInputOption='RAW',range=range, body=value_range_body)
        request.execute()

        range = 'Sheet2!A2'
        value_range_body = {'majorDimension': 'ROWS', 'values': [[str(guild.id)]]}
        request = SERVICESHEET.spreadsheets().values().append(spreadsheetId=SHEETID, valueInputOption='RAW',range=range, body=value_range_body)
        request.execute()

        embedJoin = discord.Embed(
            title="Joined " + guild.name,
            description="ID: " + str(guild.id),
            colour=COLORS["green"],
        )
        embedJoin.set_footer(text="Total Number of Servers: " + str(len(guilds)))
        await self.bot.get_guild(777063033301106728).get_channel(779045674557767680).send(embed=embedJoin)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        global SHEETID, SERVICESHEET

        fileHandler()

        guilds = self.bot.guilds
        game = discord.Game(f"~help | watching {len(guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

        dataList = list(DATA)
        botList = list(BOT)
        dataidx = str(dataList.index(str(guild.id)) + 2)
        botidx = str(botList.index(str(guild.id)) + 2)

        DATA.pop(str(guild.id))
        BOT.pop(str(guild.id))

        spreadsheet_data = [{"deleteDimension": {"range": {"sheetId": GID-ID, "dimension": "ROWS", "startIndex": int(dataidx) - 1, "endIndex": int(dataidx)}}}]
        update_data = {"requests": spreadsheet_data}
        request = SERVICESHEET.spreadsheets().batchUpdate(spreadsheetId=SHEETID, body=update_data)
        request.execute()

        spreadsheet_data = [{"deleteDimension": {"range": {"sheetId": GID-ID, "dimension": "ROWS", "startIndex": int(botidx) - 1, "endIndex": int(botidx)}}}]
        update_data = {"requests": spreadsheet_data}
        request = SERVICESHEET.spreadsheets().batchUpdate(spreadsheetId=SHEETID, body=update_data)
        request.execute()

        embedLeave = discord.Embed(
            title="Left " + guild.name,
            description="ID: " + str(guild.id),
            colour=COLORS["red"]
        )
        embedLeave.set_footer(text="Total Number of Servers: " + str(len(guilds)))
        await self.bot.get_guild(777063033301106728).get_channel(779045674557767680).send(embed=embedLeave)

def setup(bot):
    bot.add_cog(Servers(bot))
    print('Joins/Leaves loaded.')