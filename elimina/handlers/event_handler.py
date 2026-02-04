import discord
from discord.ext import commands

from elimina import LOGGER, config
from elimina.constants import COLORS, SUPER_USERS
from elimina.db.guild import (
    create_guild,
    delete_guild,
    get_guild,
    get_whitelists,
    update_guild,
)
from elimina.helpers.snipe import SnipeManager


class EventHandler(commands.Cog):
    """
    Core event handler for Elimina.

    Handles message auto-deletion in toggled channels, snipe/editsnipe,
    guild join/leave tracking, and presence updates.
    """

    __cog_name__: str = "Event Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id
        self.snipes = SnipeManager(ttl=60)

    # ── lifecycle ──

    @commands.Cog.listener()
    async def on_ready(self):
        presence_activity = discord.Game(
            f"~help | watching {len(self.bot.guilds)} servers"
        )
        await self.bot.change_presence(
            status=discord.Status.online, activity=presence_activity
        )
        LOGGER.info("Logged in as %s", self.bot.user.display_name)

    # ── core: auto-delete bot messages ──

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild:
            return

        # poll reactions
        if not message.author.bot and message.content.strip().startswith("poll: "):
            await message.add_reaction(config.POLL_EMOTE_YES)
            await message.add_reaction(config.POLL_EMOTE_NO)
            await message.add_reaction(config.POLL_EMOTE_MAYBE)
            return

        if not message.author.bot:
            return

        whitelists = await get_whitelists()
        if not whitelists:
            return

        guild_id = message.guild.id
        channel_id = message.channel.id
        author_id = message.author.id

        # own messages in toggled channels: delete after 60s
        if (
            author_id == self.bot_id
            and guild_id in whitelists
            and channel_id in whitelists[guild_id]["channels"]
        ):
            return await message.delete(delay=60)

        if author_id == self.bot_id:
            return

        # ignored bots
        if guild_id in whitelists and author_id in whitelists[guild_id]["bots"]:
            return

        # toggled channel: delete after configured delay
        if guild_id in whitelists and channel_id in whitelists[guild_id]["channels"]:
            guild = await get_guild(guild_id)
            if not guild:
                return
            await message.delete(delay=guild[0].delete_delay)

    # ── guild tracking ──

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        LOGGER.info("Guild joined: %s (%d)", guild.name, guild.id)
        await create_guild(guild.id, guild.name)
        await self._update_presence()
        await self._send_join_leave_log(
            title="Joined " + guild.name,
            guild_id=guild.id,
            color=COLORS["green"],
        )

    @commands.Cog.listener()
    async def on_guild_update(
        self, before: discord.Guild, after: discord.Guild
    ) -> None:
        if before.name != after.name:
            await update_guild(before.id, guild_name=after.name)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        LOGGER.info("Guild removed: %s (%d)", guild.name, guild.id)
        await delete_guild(guild.id)
        self.snipes.clear_guild(guild.id)
        await self._update_presence()
        await self._send_join_leave_log(
            title="Left " + guild.name,
            guild_id=guild.id,
            color=COLORS["red"],
        )

    async def _update_presence(self) -> None:
        presence = discord.Game(f"~help | watching {len(self.bot.guilds)} servers")
        await self.bot.change_presence(status=discord.Status.online, activity=presence)

    async def _send_join_leave_log(
        self, title: str, guild_id: int, color: discord.Color
    ) -> None:
        try:
            support = self.bot.get_guild(config.SUPPORT_SERVER_ID)
            if not support:
                return
            channel = support.get_channel(config.JOIN_LEAVE_CHANNEL)
            if not channel:
                return
            embed = discord.Embed(
                title=title,
                description=f"ID: {guild_id}",
                colour=color,
            )
            embed.set_footer(
                text=f"Total Number of Servers: {len(self.bot.guilds)}"
            )
            await channel.send(embed=embed)
        except Exception:
            LOGGER.exception("Failed to send join/leave notification")

    # ── snipe listeners ──

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot:
            return

        guild = await get_guild(message.guild.id)
        if not guild or not guild[0].snipe_enabled:
            return

        self.snipes.store_snipe(
            message.guild.id, message.channel.id, message
        )

    @commands.Cog.listener()
    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        if not before.guild or before.author.bot:
            return

        guild = await get_guild(before.guild.id)
        if not guild or not guild[0].snipe_enabled:
            return

        self.snipes.store_edit_snipe(
            before.guild.id, before.channel.id, before, after
        )

    # ── snipe commands ──

    async def _check_snipe_perms(self, ctx: commands.Context) -> bool:
        """Check if user has snipe permissions. Returns True if allowed."""
        if ctx.author.id in SUPER_USERS:
            return True
        if ctx.author.guild_permissions.administrator:
            return True
        if any(r.name.lower() == "sniper" for r in ctx.author.roles):
            return True

        embed = discord.Embed(
            color=COLORS["red"],
            description="❌ You need a role called `sniper` or be an `Administrator` to snipe.",
        )
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=5)
        return False

    @commands.hybrid_command(name="snipe")
    @commands.guild_only()
    async def snipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)
        if not guild:
            return

        if not guild[0].snipe_enabled:
            embed = discord.Embed(
                color=COLORS["red"], description="❌ Sniping is disabled!"
            )
            return await ctx.send(embed=embed)

        if not await self._check_snipe_perms(ctx):
            return

        message = self.snipes.get_snipe(guild_id, ctx.channel.id)
        if not message:
            embed = discord.Embed(
                color=COLORS["red"],
                description="❌ There is nothing to snipe.",
            )
            msg = await ctx.send(embed=embed)
            return await msg.delete(delay=5)

        embed = discord.Embed(
            description=message.content, color=COLORS["accent"]
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=(
                message.author.avatar.url
                if message.author.avatar
                else message.author.display_avatar.url
            ),
        )
        if message.attachments:
            for att in message.attachments:
                embed.add_field(
                    name=att.filename, value=att.proxy_url, inline=True
                )
        embed.set_footer(
            text=f"sniped by {ctx.author.name}",
            icon_url=(
                ctx.author.avatar.url
                if ctx.author.avatar
                else ctx.author.display_avatar.url
            ),
        )
        await ctx.send(embed=embed)
        self.snipes.clear_snipe(guild_id, ctx.channel.id)

    @commands.hybrid_command(name="editsnipe")
    @commands.guild_only()
    async def editsnipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)
        if not guild:
            return

        if not guild[0].snipe_enabled:
            embed = discord.Embed(
                color=COLORS["red"], description="❌ Sniping is disabled!"
            )
            return await ctx.send(embed=embed)

        if not await self._check_snipe_perms(ctx):
            return

        result = self.snipes.get_edit_snipe(guild_id, ctx.channel.id)
        if not result:
            embed = discord.Embed(
                color=COLORS["red"],
                description="❌ There is nothing to snipe.",
            )
            msg = await ctx.send(embed=embed)
            return await msg.delete(delay=5)

        before_msg, after_msg = result

        embed = discord.Embed(
            description="**Message edited:**", color=COLORS["accent"]
        )
        embed.add_field(
            name="**Before:**", value=before_msg.content or "*empty*", inline=True
        )
        embed.add_field(
            name="**After:**", value=after_msg.content or "*empty*", inline=True
        )
        embed.set_author(
            name=before_msg.author.display_name,
            icon_url=(
                before_msg.author.avatar.url
                if before_msg.author.avatar
                else before_msg.author.display_avatar.url
            ),
        )
        if after_msg.attachments:
            for att in after_msg.attachments:
                embed.add_field(
                    name=att.filename, value=att.proxy_url, inline=True
                )
        embed.set_footer(
            text=f"sniped by {ctx.author.name}",
            icon_url=(
                ctx.author.avatar.url
                if ctx.author.avatar
                else ctx.author.display_avatar.url
            ),
        )
        await ctx.send(embed=embed)
        self.snipes.clear_edit_snipe(guild_id, ctx.channel.id)

    @commands.hybrid_command(name="togglesnipe")
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def togglesnipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)
        if not guild:
            return

        snipe_enabled = guild[0].snipe_enabled

        if snipe_enabled:
            self.snipes.clear_guild(guild_id)

        await update_guild(guild_id, snipe_enabled=not snipe_enabled)

        embed = discord.Embed(
            title=None,
            color=COLORS["green"] if not snipe_enabled else COLORS["red"],
            description=f"✅ Successfully {'enabled' if not snipe_enabled else 'disabled'} snipe!",
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventHandler(bot))
    LOGGER.info("Cog Loaded: %s", EventHandler.__cog_name__)
