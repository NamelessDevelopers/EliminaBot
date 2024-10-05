from collections import defaultdict

import discord
from discord.ext import commands

from elimina import LOGGER, config
from elimina.constants import COLORS, SUPER_USERS
from elimina.db.guild import *
from elimina.helpers.snipe import EditSnipe, Snipe


class EventHandler(commands.Cog):
    """
    The EventHandler Class.

    Attributes
    ----------
        bot : commands.Bot
            The Discord Bot object.
        bot_id : int
            The id of the bot
        snipe_message : Dict[int, Snipe]
            Mapping of `guild_id` => Snipe. Stores most recently deleted Message in memory.
        edit_snipe_message : Dict[int, EditSnipe]
            Mapping of `guild_id` => EditSnipe. Stores most recently deleted Message in memory.

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

    __cog_name__: str = "Event Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id
        self.snipe_message: Dict[int, Snipe] = defaultdict(int)
        self.edit_snipe_message: Dict[int, EditSnipe] = defaultdict(int)

    @commands.Cog.listener()
    async def on_ready(self):
        presence_activity = discord.Game(
            f"~help | watching {len(self.bot.guilds)} servers"
        )
        await self.bot.change_presence(
            status=discord.Status.online, activity=presence_activity
        )
        LOGGER.info(f"Logged in as {self.bot.user.display_name}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        LOGGER.info(f"new message {message.content}")
        # add poll reactions if message starts with "poll:"
        if not message.author.bot and message.content.strip().startswith("poll: "):
            await message.add_reaction(config.POLL_EMOTE_YES)
            await message.add_reaction(config.POLL_EMOTE_NO)
            await message.add_reaction(config.POLL_EMOTE_MAYBE)
            return

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

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        LOGGER.info(f"guild joined {guild.name}")

        guild_id = guild.id

        await create_guild(guild_id, guild.name)

        # update presence
        guilds = self.bot.guilds
        presence = discord.Game(f"~help | watching {len(guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=presence)

        # send message to Elimina server
        embed_join = discord.Embed(
            title="Joined " + guild.name,
            description="ID: " + str(guild_id),
            colour=COLORS["green"],
        )
        embed_join.set_footer(text="Total Number of Servers: " + str(len(guilds)))
        await self.bot.get_guild(config.SUPPORT_SERVER_ID).get_channel(
            config.JOIN_LEAVE_CHANNEL
        ).send(embed=embed_join)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:

        guild_id = guild.id

        await delete_guild(guild_id)

        # delete snipe and editsnipe
        del self.snipe_message[guild_id]
        del self.edit_snipe_message[guild_id]

        # update presence
        guilds = self.bot.guilds
        presence = discord.Game(f"~help | watching {len(guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=presence)

        # send message to Elimina server
        embed_leave = discord.Embed(
            title="Left " + guild.name,
            description="ID: " + str(guild_id),
            colour=COLORS["red"],
        )
        embed_leave.set_footer(text="Total Number of Servers: " + str(len(guilds)))
        await self.bot.get_guild(777063033301106728).get_channel(
            779045674557767680
        ).send(embed=embed_leave)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        guild_id = message.guild.id

        guild = await get_guild(guild_id)

        if not guild:
            return

        if not guild[0].snipe_enabled:
            return

        # ignore if message author is a bot
        if message.author.bot:
            return

        self.snipe_message[guild_id] = message

    @commands.Cog.listener()
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        guild_id = before.guild.id

        guild = await get_guild(guild_id)

        if not guild:
            return

        if not guild[0].snipe_enabled:
            return

        # ignore if message author is bot
        if before.author.bot:
            return

        self.edit_snipe_message[guild_id] = after

    @commands.hybrid_command(name="snipe")
    async def snipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)

        if not guild:
            return

        if not guild[0].snipe_enabled:
            embed = discord.Embed(
                color=COLORS["red"], description="❌ sniping is disabled!"
            )
            return await ctx.send(embed=embed)

        has_snipe = False
        author_roles = ctx.author.roles
        for role in author_roles:
            if role.name.lower() == "sniper":
                has_snipe = True

        is_superuser = ctx.author.id in SUPER_USERS

        if (
            not is_superuser
            and not ctx.author.guild_permissions.administrator
            and not has_snipe
        ):
            error_embed = discord.Embed(
                title=None,
                color=COLORS["red"],
                description="❌ You either need a role called `sniper` or be an `Administrator` to snipe.",
            )
            msg = await ctx.send(embed=error_embed)
            return await msg.delete(delay=5)

        snipe_message = self.snipe_message[guild_id].message
        channel_id = ctx.channel.id

        if not snipe_message or channel_id != snipe_message.channel.id:
            error_embed = discord.Embed(
                title=None,
                color=COLORS["red"],
                description="❌ There is nothing to snipe.",
            )
            msg = await ctx.send(embed=error_embed)
            return await msg.delete(delay=5)

        snipe_embed = discord.Embed(
            description=snipe_message.content, color=COLORS["accent"]
        )
        snipe_embed.set_footer(
            text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=(
                ctx.author.avatar.url
                if ctx.author.avatar
                else ctx.author.display_avatar.url
            ),
        )
        if snipe_message.attachments:
            for attachment in snipe_message.attachments:
                snipe_embed.add_field(
                    attachment.filename, attachment.proxy_url, inline=True
                )
        snipe_embed.set_author(
            name=snipe_message.author.display_name,
            icon_url=(
                snipe_message.author.avatar.url
                if snipe_message.author.avatar
                else snipe_message.author.display_avatar.url
            ),
        )
        await ctx.send(snipe_embed)

        # reset snipe_message for the guild
        self.snipe_message[guild_id].message = None

    @commands.hybrid_command(name="editsnipe")
    async def editsnipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)

        if not guild:
            return

        if not guild[0].snipe_enabled:
            embed = discord.Embed(
                color=COLORS["red"], description="❌ sniping is disabled!"
            )
            return await ctx.send(embed=embed)

        has_snipe = False
        author_roles = ctx.author.roles
        for role in author_roles:
            if role.name.lower() == "sniper":
                has_snipe = True

        is_superuser = ctx.author.id in SUPER_USERS

        if (
            not is_superuser
            and not ctx.author.guild_permissions.administrator
            and not has_snipe
        ):
            error_embed = discord.Embed(
                title=None,
                color=COLORS["red"],
                description="❌ You either need a role called `sniper` or be an `Administrator` to snipe.",
            )
            msg = await ctx.send(embed=error_embed)
            return await msg.delete(delay=5)

        edit_snipe_message = self.edit_snipe_message[guild_id].message
        edited_message = self.edit_snipe_message[guild_id].edited_message
        channel_id = ctx.channel.id

        if (
            not edit_snipe_message
            or not edited_message
            or channel_id != edit_snipe_message.channel.id
        ):
            error_embed = discord.Embed(
                title=None,
                color=COLORS["red"],
                description="❌ There is nothing to snipe.",
            )
            msg = await ctx.send(embed=error_embed)
            return await msg.delete(delay=5)

        snipe_embed = discord.Embed(
            description="**Message edited:**", color=COLORS["accent"]
        )
        snipe_embed.add_field("**Before:**", edit_snipe_message.content, inline=True)
        snipe_embed.add_field("**After:**", edited_message.content, inline=True)
        snipe_embed.set_footer(
            text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=(
                ctx.author.avatar.url
                if ctx.author.avatar
                else ctx.author.display_avatar.url
            ),
        )
        if edited_message.attachments:
            for attachment in edit_snipe_message.attachments:
                snipe_embed.add_field(
                    attachment.filename, attachment.proxy_url, inline=True
                )
        snipe_embed.set_author(
            name=edit_snipe_message.author.display_name,
            icon_url=(
                edit_snipe_message.author.avatar.url
                if edit_snipe_message.author.avatar
                else edit_snipe_message.author.display_avatar.url
            ),
        )
        await ctx.send(snipe_embed)

        # reset edit_snipe_message for the guild
        self.edit_snipe_message[guild_id].message = None
        self.edit_snipe_message[guild_id].edited_message = None
    
    @commands.hybrid_command(name="togglesnipe")
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def togglesnipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)

        if not guild:
            return
        
        snipe_enabled = guild[0].snipe_enabled

        if snipe_enabled:
            del self.snipe_message[guild_id]
            del self.edit_snipe_message[guild_id]
        else:
            self.snipe_message[guild_id] = Snipe()
            self.edit_snipe_message[guild_id] = EditSnipe()

        await update_guild(guild_id, snipe_enabled=not snipe_enabled)

        embed = discord.Embed(
            title=None,
            color=COLORS["green"] if not snipe_enabled else COLORS["red"],
            description=f"✅ Successfully {"enabled"  if not snipe_enabled else "disabled"} snipe!",
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventHandler(bot))
    LOGGER.info(f"Cog Loaded: {EventHandler.__cog_name__}")
