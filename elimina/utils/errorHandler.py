from typing import Any

from discord import Embed
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS


class Errors(commands.Cog):

    __cog_name__ = "Error Handler"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Any) -> None:
        # TODO: use match expression instead
        if isinstance(error, commands.BotMissingPermissions):
            permErrorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Looks like I'm missing `manage channels` and/or `move members` permissions.",
            )
            return await ctx.send(embed=permErrorEmbed)

        if isinstance(error, commands.CommandOnCooldown):
            command = self.bot.get_command(ctx.command.name)
            cooldownEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ That command is on cooldown for {} seconds.".format(
                    int(command.get_cooldown_retry_after(ctx))
                ),
            )
            return await ctx.send(embed=cooldownEmbed)

        if isinstance(error, commands.UserNotFound):
            userErrorEmbed = Embed(
                title=None, color=COLORS["red"], description="❌ User not found."
            )
            return await ctx.send(embed=userErrorEmbed)

        if ctx.command.name == "timer":
            timerErrorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Invalid value for time. Must be between 1 and 300",
            )
            return await ctx.send(embed=timerErrorEmbed)

        else:
            LOGGER.exception(error)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Errors(bot))
    LOGGER.info("Cog Loaded: ", Errors.__cog_name__)
