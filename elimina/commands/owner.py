from discord.ext import commands

from elimina import LOGGER


class Owner(commands.Cog):

    __cog_name_: str = "Owner"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.command(name="sync_tree")
    @commands.is_owner()
    @commands.cooldown(rate=1, per=3600, type=commands.BucketType.default)
    async def sync_tree(self, ctx: commands.Context) -> None:
        msg = await ctx.reply("Syncing CommandTree...")
        app_commands = await self.bot.tree.sync()
        await msg.edit(f"Synced {len(app_commands)} commands with the CommandTree...")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Owner(bot))
    LOGGER.info(f"Cog Loaded: {Owner.__cog_name_}")
