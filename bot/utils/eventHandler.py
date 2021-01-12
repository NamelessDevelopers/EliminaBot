import discord
import asyncio

from discord import Embed
from discord.ext import commands

from bot.utils.utils import COLORS
from bot.utils.fileHandler import data_update, bot_update, BOT, DATA


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        guilds = self.bot.guilds
        presenceActivity = discord.Game("~help | watching {} servers".format(len(guilds)))
        await self.bot.change_presence(status=discord.Status.online, activity=presenceActivity)
        print("Logged in as {0.user}".format(self.bot))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user and message.channel.id in DATA[str(message.guild.id)]:
            return await message.delete(60)
        
        if message.author == self.bot.user:
            return
        
        if not message.author.bot:
            return 
        
        ignored_bots = BOT[str(message.guild.id)]

        if str(message.author.id) in ignored_bots:
            return print("true\n")
        
        if str(message.channel.id) in str(DATA[str(message.guild.id)]):
            delayTime = int(DATA[str(message.guild.id)][0])
            await message.delete(delay=delayTime)
        
def setup(bot):
    bot.add_cog(Events(bot))
    print("EventHandler loaded.")