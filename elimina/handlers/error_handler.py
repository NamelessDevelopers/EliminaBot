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

    __cog_name__ = "Error Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Any) -> None:
        if isinstance(error, commands.BotMissingPermissions):
            perm_error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Looks like I'm missing `manage channels` and/or `move members` permissions.",
            )
            return await ctx.send(embed=perm_error_embed)

        if isinstance(error, commands.CommandOnCooldown):
            command = self.bot.get_command(ctx.command.name)
            cooldown_error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ That command is on cooldown for {} seconds.".format(
                    int(command.get_cooldown_retry_after(ctx))
                ),
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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
    LOGGER.info("Cog Loaded: ", ErrorHandler.__cog_name__)
