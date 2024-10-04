from discord import Embed, HTTPException
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS, SUPER_USERS


class Mod(commands.Cog):

    __cog_name__ = "Mod"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="purge", aliases=["prune", "clean", "clear"])
    async def purge(self, ctx: commands.Context, count: int = 300) -> None:

        has_moderation = False
        for role in ctx.author.roles:
            if role.name.lower() == "moderation":
                has_moderation = True
        manage_messages = ctx.author.guild_permissions.manage_messages
        super_user = str(ctx.author.id) in SUPER_USERS.values()

        if not (super_user or manage_messages or has_moderation):
            return

        try:
            msgs = await ctx.channel.purge(
                limit=count + 1,
                before=ctx.message,
                check=lambda m: m.author.bot and not m.pinned,
            )

        except HTTPException:
            errorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Unable to delete messages older than 14 days.",
            )
            await ctx.send(embed=errorEmbed)

        if not len(msgs):
            purgeEmbed = Embed(
                title=None, color=COLORS["red"], description="❌ No messages to delete."
            )
            x = await ctx.send(embed=purgeEmbed)

        else:
            purgeEmbed = Embed(
                title=None,
                color=COLORS["green"],
                description="✅ Successfully deleted {} messages sent by bots.".format(
                    len(msgs)
                ),
            )
            x = await ctx.send(embed=purgeEmbed)

        await ctx.message.delete()
        await x.delete(delay=4)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Mod(bot))
    LOGGER.info("Cog Loaded: ", Mod.__cog_name__)
