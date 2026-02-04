import asyncio
import re

from discord import Embed
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS


class Utility(commands.Cog):

    __cog_name__: str = "Util"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.command(name="dctimer", aliases=["disconnect", "dc"])
    @commands.guild_only()
    @commands.bot_has_guild_permissions(manage_channels=True, move_members=True)
    async def dctimer(self, ctx: commands.Context, time: str) -> None:
        if not ctx.author.voice:
            embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ You're not connected to a voice channel!",
            )
            return await ctx.send(embed=embed)

        if time is None:
            embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Please specify a duration after which I should disconnect you!",
            )
            return await ctx.send(embed=embed)

        if not re.search(r"\d", time):
            embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Invalid value for time!",
            )
            return await ctx.send(embed=embed)

        suffix = time[-1].lower()
        if suffix == "s":
            seconds = int(time[:-1])
        elif suffix == "m":
            seconds = int(time[:-1]) * 60
        elif suffix == "h":
            seconds = int(time[:-1]) * 3600
        else:
            seconds = int(time)

        if seconds <= 0 or seconds > 10800:
            embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Time must be between **1s** to **3h**.",
            )
            return await ctx.send(embed=embed)

        embed = Embed(
            title=None,
            color=COLORS["green"],
            description="✅ Timer for automatic disconnection set!",
        )
        await ctx.send(embed=embed)

        await asyncio.sleep(seconds)

        try:
            # re-check if user is still in voice
            if not ctx.author.voice:
                return
            temp_channel = await ctx.guild.create_voice_channel("disconnect")
            await ctx.author.move_to(temp_channel, reason="dctimer: disconnecting")
            await temp_channel.delete(reason="dctimer: cleanup")
        except Exception:
            LOGGER.exception("dctimer disconnect failed for %s", ctx.author)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
    LOGGER.info("Cog Loaded: %s", Utility.__cog_name__)
