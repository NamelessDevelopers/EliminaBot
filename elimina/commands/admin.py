import discord
from discord import Embed
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS
from elimina.db.guild import get_guild, get_whitelists, update_guild
from elimina.exceptions.elimina_exceptions import TimeValueError


class Admin(commands.Cog):

    __cog_name__: str = "Admin"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.hybrid_command(name="toggle", aliases=["enable", "disable"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def toggle(self, ctx: commands.Context) -> None:
        channel_id = ctx.channel.id
        guild_id = ctx.guild.id

        whitelist = await get_whitelists()

        if guild_id in whitelist and channel_id in whitelist[guild_id]["channels"]:
            await update_guild(guild_id, disabled_channel=channel_id)
            deactivate_embed = Embed(
                title=None,
                color=COLORS["red"],
                description=f"✅ Successfully deactivated {ctx.channel.mention}!",
            )
            return await ctx.send(embed=deactivate_embed)
        await update_guild(guild_id, enabled_channel=channel_id)
        activate_embed = Embed(
            title=None,
            color=COLORS["green"],
            description=f"✅ Successfully activated {ctx.channel.mention}!",
        )
        await ctx.send(embed=activate_embed)

    @commands.hybrid_command(name="timer", aliases=["wait", "delay"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def timer(self, ctx: commands.Context, time: int) -> None:
        guild_id = ctx.guild.id
        if time <= 0 or time > 300:
            raise TimeValueError(time)

        await update_guild(guild_id, delete_delay=time)

        time_changed_embed = Embed(
            title=None,
            color=COLORS["green"],
            description=f"✅ Changed timer to **{time} seconds.**",
        )
        await ctx.send(embed=time_changed_embed)

    @commands.hybrid_command(name="imgsnipe", aliases=["imagesnipe", "image"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def imgsnipe(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id

        guild = await get_guild(guild_id)

        if not guild:
            return

        image_snipe = guild[0].image_snipe

        await update_guild(guild_id, image_snipe=not image_snipe)
        embed = Embed(
            title=None,
            color=COLORS["green"] if not image_snipe else COLORS["red"],
            description=f"✅ Successfully {'enabled' if not image_snipe else 'disabled'} image snipe!",
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="ignore", aliases=["unignore", "whitelist"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def ignore(self, ctx: commands.Context, bot: discord.User) -> None:
        guild_id = ctx.guild.id
        bot_id = bot.id
        if not bot.bot:
            error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ The mentioned user is not a bot.",
            )
            return await ctx.send(embed=error_embed)

        if bot_id == self.bot_id:
            error_embed = Embed(
                title=None, color=COLORS["red"], description="❌ You can't ignore me."
            )
            return await ctx.send(embed=error_embed)

        whitelist = await get_whitelists()

        if guild_id in whitelist and bot_id in whitelist[guild_id]["bots"]:
            await update_guild(guild_id, unignored_bot=bot_id)
            unignore_embed = Embed(
                title=None,
                color=COLORS["red"],
                description=f"✅ Successfully un-ignored {bot.mention}.",
            )
            await ctx.send(embed=unignore_embed)

        else:
            await update_guild(guild_id, ignored_bot=bot_id)

            ignore_embed = Embed(
                title=None,
                color=COLORS["green"],
                description=f"✅ Successfully ignored {bot.mention}.",
            )
            await ctx.send(embed=ignore_embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
    LOGGER.info("Cog Loaded: %s", Admin.__cog_name__)
