import discord
from discord import Embed
from discord.ext import commands

from elimina import LOGGER, config
from elimina.constants import COLORS, SUPER_USERS
from elimina.db.guild import get_guild, get_whitelists


class Info(commands.Cog):

    __cog_name__ = "Info"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot_id = bot.user.id

    @commands.hybrid_command(name="help")
    async def _help(self, ctx: commands.Context) -> None:
        help_embed = Embed(title="**Commands**", colour=COLORS["accent"])

        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}info` :",
            value="  *To get information about how Elimina is setup in this server.*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}toggle` :  __(Admin only)__",
            value="  *Type in channel to activate or deactivate the bot in the respective channel.*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}ignore <bot>` : __(Admin only)__",
            value="*Add or Remove the bot(s) from server's Elimina whitelist*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}timer <time in seconds>` :  __(Admin Only)__",
            value="  *Change default timer after which the bot messages are deleted. Default: 15 seconds*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}purge` <number of messages>[optional]:",
            value="  *Type in channel to manually clear recent(or if specified, n number of) messages sent by bots*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}snipe` :",
            value="*To show the last text message or image deleted by a user within a minute on the same channel. _Does not snipe bots._*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}imgsnipe` : __(Admin only)__",
            value="*To enable/disable sniping of images using the `snipe` command.*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}invite` :",
            value="  *To provide an invite link for a Discord server.*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}editsnipe` :",
            value="*To show the last message edited by a user within a minute on the same channel.*",
        )
        help_embed.add_field(
            name=f"`{config.BOT_PREFIX}dctimer <time>` :",
            value="*To automatically disconnect you from the voice channel after the specified time delay.*",
        )
        help_embed.add_field(name="\u200B", value="\u200B")
        help_embed.add_field(
            name="Support Server",
            value=f"*{config.SUPPORT_SERVER_INVITE}*",
            inline=False,
        )
        help_embed.add_field(
            name="_Messages from Elimina are deleted after 1 minute in toggled on channels_",
            value=f"*For help contact: {config.SUPPORT_EMAIL}*",
            inline=False,
        )
        help_embed.set_author(
            name="Elimina Bot",
            url=config.GITHUB_URL,
            icon_url=self.bot.user.avatar_url,
        )
        help_embed.set_footer(text="Requested by: " + ctx.message.author.name)
        await ctx.send(embed=help_embed)

    @commands.hybrid_command(name="info", aliases=["about", "information"])
    async def info(self, ctx: commands.Context) -> None:
        info_embed = discord.Embed(
            title="Server Setup Information",
            description="Elimina is a bot that can delete messages sent from bot users"
            + " after X number of seconds in toggled on channels. Messages can be deleted"
            + " after 1 second to after 300 seconds (5 minutes)! Elimina also provides a"
            + " snipe feature showing the most recently deleted text or image message.\nUse"
            + f"`{config.BOT_PREFIX}help` for more information",
            colour=COLORS["accent"],
        )

        whitelists = await get_whitelists()

        guild_id = ctx.guild.id
        guild = await get_guild(guild_id)
        if not guild:
            return
        guild = guild[0]

        mention_str = "  ".join(
            [
                ctx.guild.get_channel(int(channel_id)).mention
                for channel_id in list(whitelists[guild_id]["channels"])
            ]
        )

        info_embed.set_author(
            name="Elimina Bot",
            url=config.GITHUB_URL,
            icon_url=self.bot.user.avatar_url,
        )

        bot_str = " ".join(
            [f"<@{bot_id}>" for bot_id in list(whitelists[guild_id]["bots"])]
        )

        if not len(mention_str):
            info_embed.add_field(
                name="Following channels are toggled on: ",
                value="No Channels toggled on use ~toggle",
                inline=False,
            )
        else:
            info_embed.add_field(
                name="Following channels are toggled on: ",
                value=mention_str,
                inline=False,
            )

        if not len(bot_str):
            info_embed.add_field(
                name="Following bots are ignored: ",
                value="No bots are ignored ~ignore <@bot>",
                inline=False,
            )
        else:
            info_embed.add_field(
                name="Following bots are ignored: ", value=bot_str, inline=False
            )

        info_embed.add_field(
            name="Sniping",
            value="enabled" if guild.snipe_enabled else "disabled",
            inline=True,
        )

        info_embed.add_field(
            name="Image Snipe: ",
            value="enabled" if guild.image_snipe else "disabled",
            inline=True,
        )

        info_embed.add_field(
            name="Timer set at:",
            value=f"__{guild.delete_delay} seconds__",
            inline=True,
        )

        info_embed.add_field(
            name="Support Server",
            value=f"*{config.SUPPORT_SERVER_INVITE}*",
            inline=False,
        )
        info_embed.set_footer(
            text="Requested by: "
            + ctx.message.author.name
            + "\nAuthors: "
            + " ".join(author for author in SUPER_USERS.values())
        )
        await ctx.send(embed=info_embed)

    @commands.hybrid_command(name="invite")
    async def invite(self, ctx: commands.Context) -> None:
        embed_invite = discord.Embed(
            title="Click here to invite me",
            colour=COLORS["accent"],
            url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot_id}&permissions=17918992&scope=bot",
        )
        embed_invite.add_field(
            name="Support Server",
            value=f"*{config.SUPPORT_SERVER_INVITE}*",
            inline=False,
        )
        embed_invite.set_footer(text=f"\nFor help contact {config.SUPPORT_EMAIL}")
        await ctx.send(embed=embed_invite)

    @commands.hybrid_command(name="vote")
    async def vote(self, ctx: commands.Context) -> None:
        vote_embed = discord.Embed(
            title="Click here to vote for me",
            color=COLORS["accent"],
            url=f"https://top.gg/bot/{config.TOP_GG_ID}/vote",
        )
        vote_embed.add_field(
            name="Support Server",
            value=f"*{config.SUPPORT_SERVER_INVITE}*",
            inline=False,
        )
        vote_embed.set_footer(text=f"\nFor help contact {config.SUPPORT_EMAIL}")
        return await ctx.send(embed=vote_embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Info(bot))
    LOGGER.info("Cog Loaded: ", Info.__cog_name__)
