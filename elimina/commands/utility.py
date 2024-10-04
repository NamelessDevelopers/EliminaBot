import asyncio
import re

from discord import Embed
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS


class Utility(commands.Cog):

    __cog_name__ = "Util"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.command(name="dctimer", aliases=["disconnect", "dc"])
    @commands.bot_has_guild_permissions(manage_channels=True, move_members=True)
    async def dctimer(
        self, ctx: commands.Context, time: str
    ) -> None:  # TODO: make a class named Time and transform using that instead
        if not ctx.author.voice:
            errorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ You're not connected to a voice channel!",
            )
            return await ctx.send(embed=errorEmbed)

        if time is None:
            errorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Please specify a duration after which I should disconnect you!",
            )
            return await ctx.send(embed=errorEmbed)

        if not (bool(re.search(r"\d", time))):
            errorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Invalid value for time!",
            )
            return await ctx.send(embed=errorEmbed)

        if time[-1].lower() == "s":
            time = int(time[: len(time) - 1])

        elif time[-1].lower() == "m":
            time = int(time[: len(time) - 1]) * 60

        elif time[-1].lower() == "h":
            time = int(time[: len(time) - 1]) * 60 * 60

        time = int(time)

        if time <= 0 or time > 10800:
            errorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Time must be between **1s** to **3h**.",
            )
            return await ctx.send(embed=errorEmbed)

        dcEmbed = Embed(
            title=None,
            color=COLORS["green"],
            description="✅ Timer for automatic disconnection set!",
        )
        await ctx.send(embed=dcEmbed)
        await asyncio.sleep(time)
        tempChannel = await ctx.guild.create_voice_channel("disconnect")
        await ctx.author.move_to(tempChannel, reason="disconnecting")
        await tempChannel.delete(reason="disconnected")
        await asyncio.sleep(30)  # Cross-check if the channel is deleted.
        await tempChannel.delete(reason="disconnected")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Utility(bot))
    LOGGER.info("Cog Loaded: ", Utility.__cog_name__)
