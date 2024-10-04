import discord
from discord import Embed
from discord.ext import commands

from elimina import LOGGER
from elimina.constants import COLORS
from elimina.utils.fileHandler import (
    BOT,
    DATA,
    SERVICESHEET,
    SHEETID,
    bot_update,
    data_update,
)


class Admin(commands.Cog):

    __cog_name__ = "Admin"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="toggle", aliases=["enable", "disable"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def toggle(self, ctx: commands.Context) -> None:
        channelID = ctx.channel.id
        whiteListed = False

        if str(ctx.guild.id) in str(DATA):
            if str(channelID) in DATA[str(ctx.guild.id)]:
                whiteListed = True

        if whiteListed:
            DATA[str(ctx.guild.id)].remove(str(channelID))
            deactivateEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="✅ Successfully deactivated {0.mention}!".format(
                    ctx.channel
                ),
            )
            await ctx.send(embed=deactivateEmbed)
        else:
            DATA[str(ctx.guild.id)].append(str(channelID))
            activateEmbed = Embed(
                title=None,
                color=COLORS["green"],
                description="✅ Successfully activated {0.mention}!".format(
                    ctx.channel
                ),
            )
            await ctx.send(embed=activateEmbed)

        data_update(ctx.guild.id)

    @commands.command(name="timer", aliases=["wait", "delay"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def timer(self, ctx: commands.Context, time: int) -> None:
        time = int(time)
        if time <= 0 or time > 300:
            raise ValueError

        DATA.get(str(ctx.guild.id))[0] = time

        data_update(ctx.guild.id)
        timerChangedEmbed = Embed(
            title=None,
            color=COLORS["green"],
            description=f"✅ Changed timer to **{DATA[str(ctx.message.author.guild.id)][0]} seconds.**",
        )
        await ctx.send(embed=timerChangedEmbed)

    @commands.command(name="imgsnipe", aliases=["imagesnipe", "image"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def imgsnipe(self, ctx: commands.Context) -> None:
        image_snipe = True

        if str(ctx.guild.id) in str(DATA):
            if DATA.get(str(ctx.guild.id))[1] == "0":
                image_snipe = False

        if not image_snipe:
            DATA.get(str(ctx.guild.id))[1] = "1"
            enableEmbed = Embed(
                title=None,
                color=COLORS["green"],
                description="✅ Successfully enabled image snipe!",
            )
            await ctx.send(embed=enableEmbed)

        else:
            DATA.get(str(ctx.guild.id))[1] = "1"
            disableEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="✅ Successfully disabled image snipe!",
            )
            await ctx.send(embed=disableEmbed)

        data_update(ctx.guild.id)

    @commands.command(name="ignore", aliases=["unignore", "whitelist"])
    @commands.has_permissions(administrator=True)
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.guild)
    async def ignore(self, ctx: commands.Context, bot: discord.User) -> None:
        global SHEETID, SERVICESHEET

        if not bot.bot:
            errorEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="❌ The mentioned user is not a bot.",
            )
            return await ctx.send(embed=errorEmbed)

        if bot.id == 777575449957498890:
            errorEmbed = Embed(
                title=None, color=COLORS["red"], description="❌ You can't ignore me."
            )
            await ctx.send(embed=errorEmbed)

        userID = bot.id
        whiteListed = False

        if str(ctx.guild.id) in str(BOT):
            if str(userID) in BOT[str(ctx.guild.id)]:
                whiteListed = True

        if whiteListed:
            BOT[str(ctx.guild.id)].remove(str(userID))
            unignoredEmbed = Embed(
                title=None,
                color=COLORS["red"],
                description="✅ Successfully un-ignored {0.mention}.".format(bot),
            )
            await ctx.send(embed=unignoredEmbed)

        else:
            BOT[str(ctx.guild.id)].append(str(userID))
            BOT[str(ctx.guild.id)].append(str(userID))

            ignoredEmbed = Embed(
                title=None,
                color=COLORS["green"],
                description="✅ Successfully ignored {0.mention}.".format(bot),
            )
            await ctx.send(embed=ignoredEmbed)

        bot_update(ctx.guild.id)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Admin(bot))
    LOGGER.info("Cog Loaded: ", Admin.__cog_name__)
