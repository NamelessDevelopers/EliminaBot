import discord

from discord.ext import commands
from discord import Embed

from bot.utils.utils import COLORS


class Errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            permErrorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ Looks like I'm missing `manage channels` and `move members` permissions."
            )
            return await ctx.send(embed=permErrorEmbed)

        if isinstance(error, commands.CommandOnCooldown):
            command = self.bot.get_command(ctx.command.name)
            cooldownEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ That command is on cooldown for {} seconds."
                        .format(int(command.get_cooldown_retry_after(ctx)))
            )
            return await ctx.send(embed=cooldownEmbed)
        
        if isinstance(error, commands.UserNotFound):
            userErrorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ User not found."
            )
            return await ctx.send(embed=userErrorEmbed)

        if ctx.command.name == "timer":
            timerErrorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ Invalid value for time. Must be between 1 and 300"
            )
            return await ctx.send(embed=timerErrorEmbed)

        else:
            print(error)

def setup(bot):
    bot.add_cog(Errors(bot))
    print("Errors loaded.")