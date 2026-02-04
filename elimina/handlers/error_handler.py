from typing import Any

from discord import Embed
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS
from elimina.exceptions.elimina_exceptions import TimeValueError


class ErrorHandler(commands.Cog):
    """
    The ErrorHandler Class.

    Class to handle various errors from `discord.ext.commands` and custom errors.
    """

    __cog_name__: str = "Error Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Any) -> None:
        if isinstance(error, commands.NoPrivateMessage):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = ", ".join(error.missing_permissions)
            perm_error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description=f"❌ I'm missing permissions: `{missing}`",
            )
            return await ctx.send(embed=perm_error_embed)

        if isinstance(error, commands.MissingPermissions):
            missing = ", ".join(error.missing_permissions)
            perm_error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description=f"❌ You need: `{missing}` to use this command.",
            )
            return await ctx.send(embed=perm_error_embed)

        if isinstance(error, commands.CommandOnCooldown):
            cooldown_error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description=f"❌ That command is on cooldown for {error.retry_after:.1f} seconds.",
            )
            return await ctx.send(embed=cooldown_error_embed)

        if isinstance(error, commands.UserNotFound):
            user_error_embed = Embed(
                title=None, color=COLORS["red"], description="❌ User not found."
            )
            return await ctx.send(embed=user_error_embed)

        if isinstance(error, TimeValueError):
            timer_error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description=f"❌ Invalid value for time ({error.time}). Must be between 1 and 300",
            )
            return await ctx.send(embed=timer_error_embed)

        else:
            LOGGER.exception(error)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
    LOGGER.info("Cog Loaded: %s", ErrorHandler.__cog_name__)
