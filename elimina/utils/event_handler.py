import discord
from discord.ext import commands

from elimina import LOGGER
from elimina.db.guild import get_guild, get_whitelists


class Events(commands.Cog):

    __cog_name__ = "Event Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.Cog.listener("ready")
    async def on_ready(self):
        presenceActivity = discord.Game(
            f"~help | watching {len(self.bot.guilds)} servers"
        )
        await self.bot.change_presence(
            status=discord.Status.online, activity=presenceActivity
        )
        print(f"Logged in as {self.bot}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # if author is not a bot
        if not message.author.bot:
            return
        # get whitelists from cache
        whitelists = await get_whitelists()
        if not whitelists:
            LOGGER.critical("Whitelist creation is failing!")
            return
        guild_id = message.guild.id
        channel_id = message.channel.id
        author_id = message.author.id

        # if author is the bot and channel is whitelisted, delete message in 60s
        if (
            author_id == self.bot_id
            and guild_id in whitelists
            and channel_id in whitelists[guild_id]["channels"]
        ):
            return await message.delete(60)

        # case where author is the bot already handled
        if author_id == self.bot_id:
            return

        # if the author is in whitelisted bots
        if guild_id in whitelists and author_id in whitelists[guild_id]["bots"]:
            return

        # case where channel is whitelisted
        if guild_id in whitelists and channel_id in whitelists[guild_id]["channels"]:
            guild = await get_guild(guild_id)
            if not guild:
                return
            delete_delay = guild[0].delete_delay
            await message.delete(delay=delete_delay)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Events(bot))
    LOGGER.info("Cog Loaded: ", Events.__cog_name__)
