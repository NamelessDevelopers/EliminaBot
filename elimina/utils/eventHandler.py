import discord
from discord.ext import commands

from elimina import LOGGER
from elimina.utils.fileHandler import BOT, DATA


class Events(commands.Cog):

    __cog_name__ = "Event Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener("ready")
    async def on_ready(self):
        presenceActivity = discord.Game(
            f"~help | watching {len(self.bot.guilds)} servers"
        )
        await self.bot.change_presence(
            status=discord.Status.online, activity=presenceActivity
        )
        print(f"Logged in as {self.bot}")
        # TODO: cache all enabled channel ids upon start
        # create a mapping of guild_id => set(toggled_channels)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if (
            message.author == self.bot.user
            and message.channel.id in DATA[str(message.guild.id)]
        ):
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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Events(bot))
    LOGGER.info("Cog Loaded: ", Events.__cog_name__)
