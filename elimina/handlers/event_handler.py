import discord
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS
from elimina.db.guild import *


class EventHandler(commands.Cog):
    """
    The EventHandler Class.

    Events Handled
    --------------
        Ready : on_ready
            The event triggered once the bot establishes connection with Discord servers.
        Message : on_message
            The event triggered whenever the bot receives a message - core functionality of Elimina.
        Guild Join : on_guild_join
            The event triggered whenever the bot is added to a new guild.
        Guild Remove : on_guild_remove
            The event triggered whenever the bot is removed from a guild.
    """

    __cog_name__ = "Event Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.Cog.listener("ready")
    async def on_ready(self):
        presence_activity = discord.Game(
            f"~help | watching {len(self.bot.guilds)} servers"
        )
        await self.bot.change_presence(
            status=discord.Status.online, activity=presence_activity
        )
        print(f"Logged in as {self.bot}")

    @commands.Cog.listener("Message")
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

    @commands.Cog.listener("Guild Join")
    async def on_guild_join(self, guild: discord.Guild) -> None:

        await create_guild(guild.id, guild.name)

        # update presence
        guilds = self.bot.guilds
        presence = discord.Game(f"~help | watching {len(guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=presence)

        # send message to Elimina server
        embed_join = discord.Embed(
            title="Joined " + guild.name,
            description="ID: " + str(guild.id),
            colour=COLORS["green"],
        )
        embed_join.set_footer(text="Total Number of Servers: " + str(len(guilds)))
        await self.bot.get_guild(777063033301106728).get_channel(
            779045674557767680
        ).send(embed=embed_join)

    @commands.Cog.listener("Guild Remove")
    async def on_guild_remove(self, guild: discord.Guild) -> None:

        await delete_guild(guild.id)

        # update presence
        guilds = self.bot.guilds
        presence = discord.Game(f"~help | watching {len(guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=presence)

        # send message to Elimina server
        embed_leave = discord.Embed(
            title="Left " + guild.name,
            description="ID: " + str(guild.id),
            colour=COLORS["red"],
        )
        embed_leave.set_footer(text="Total Number of Servers: " + str(len(guilds)))
        await self.bot.get_guild(777063033301106728).get_channel(
            779045674557767680
        ).send(embed=embed_leave)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(EventHandler(bot))
    LOGGER.info("Cog Loaded: ", EventHandler.__cog_name__)
