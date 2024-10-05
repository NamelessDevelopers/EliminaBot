from discord import Embed, HTTPException
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS, SUPER_USERS


class Mod(commands.Cog):

    __cog_name__: str = "Mod"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="purge", aliases=["prune", "clean", "clear"])
    async def purge(self, ctx: commands.Context, count: int = 300) -> None:

        has_moderation = False
        for role in ctx.author.roles:
            if role.name.lower() == "moderation":
                has_moderation = True
        manage_messages = ctx.author.guild_permissions.manage_messages
        super_user = ctx.author.id in SUPER_USERS

        if not (super_user or manage_messages or has_moderation):
            return

        try:
            msgs = await ctx.channel.purge(
                limit=count + 1,
                before=ctx.message,
                check=lambda m: m.author.bot and not m.pinned,
            )

        except HTTPException:
            error_embed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ Unable to delete messages older than 14 days.",
            )
            await ctx.send(embed=error_embed)

        msg = None

        if not len(msgs):
            purge_embed = Embed(
                title=None, color=COLORS["red"], description="❌ No messages to delete."
            )
            msg = await ctx.send(embed=purge_embed)

        else:
            purge_embed = Embed(
                title=None,
                color=COLORS["green"],
                description=f"✅ Successfully deleted {len(msgs)} messages sent by bots.",
            )
            msg = await ctx.send(embed=purge_embed)

        await ctx.message.delete()
        await msg.delete(delay=4)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mod(bot))
    LOGGER.info(f"Cog Loaded: {Mod.__cog_name__}")
