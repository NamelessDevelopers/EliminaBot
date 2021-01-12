import discord

from discord.ext import commands
from discord import Embed

from bot.utils.utils import COLORS
from bot.utils.fileHandler import DATA, BOT


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def _help(self, ctx):
        embedHelp = Embed(
            title = "**Commands**",
            colour = COLORS["accent"]
        )

        embedHelp.add_field(name="`~info` :", value="  *To get information about how Elimina is setup in this server.*")
        embedHelp.add_field(name="`~toggle` :  __(Admin only)__", value="  *Type in channel to activate or deactivate the bot in the respective channel.*")
        embedHelp.add_field(name="`~ignore <bot>` : __(Admin only)__", value="*Add or Remove the bot(s) from server's Elimina whitelist*")
        embedHelp.add_field(name="`~timer <time in seconds>` :  __(Admin Only)__", value="  *Change default timer after which the bot messages are deleted. Default: 15 seconds*")
        embedHelp.add_field(name="`~purge` <number of messages>[optional]:", value="  *Type in channel to manually clear recent(or if specified, n number of) messages sent by bots*")
        embedHelp.add_field(name="`~snipe` :", value="*To show the last text message or image deleted by a user within a minute on the same channel. _Does not snipe bots._*")
        embedHelp.add_field(name="`~imgsnipe` : __(Admin only)__", value="*To enable/disable sniping of images using the `snipe` command.*")
        embedHelp.add_field(name="`~invite` :", value="  *To provide an invite link for a Discord server.*")
        embedHelp.add_field(name="`~editsnipe` :", value="*To show the last message edited by a user within a minute on the same channel.*")
        embedHelp.add_field(name="`~dctimer <time>` :", value="*To automatically disconnect you from the voice channel after the specified time delay.*")
        embedHelp.add_field(name='\u200B', value='\u200B')
        embedHelp.add_field(name="Support Server",value='*https://discord.gg/mXPGpTMsqS*', inline=False)
        embedHelp.add_field(name="_Messages from Elimina are deleted after 1 minute in toggled on channels_",value='*For help contact: eliminabot@gmail.com*', inline=False)
        embedHelp.set_author(name='Elimina Bot', url="https://github.com/NamelessDevelopers/EliminaBot" , icon_url=self.bot.user.avatar_url)
        embedHelp.set_footer(
            text="Requested by: " + ctx.message.author.name)
        await ctx.send(embed=embedHelp)
    
    @commands.command(name="info", aliases=["about", "information"])
    async def info(self, ctx):
        embedInfo = discord.Embed(
            title="Server Setup Information",
            description="Elimina is a bot that can delete messages"
            ' sent from bot users after X number of seconds in toggled on channels. '
            'Messages can be deleted after 1 second to after 300 seconds (5 minutes)! Elimina '
            ' also provides a snipe feature showing the most recently deleted text or image message.\nUse `~help` for more information',
            colour=COLORS["accent"]
        )

        val = str(ctx.guild.id)
        mentionStr = ''
        for elem in DATA[val]:
            try:
                int(elem)
            except:
                continue
            if elem != '' and elem != "\n" and int(elem) > 300:
                try:
                    mentionStr += ctx.guild.get_channel(int(elem)).mention + " "
                except:
                    continue


        embedInfo.set_author(name='Elimina Bot', url="https://github.com/NamelessDevelopers/EliminaBot" , icon_url=self.bot.user.avatar_url)

        botStr = ''
        for e in BOT[val]:
            try:
                int(e)
            except:
                continue
            if e != '' and e != "\n" and int(e) > 300:
                try:
                    mem = await ctx.guild.fetch_member(int(e))
                    botStr += mem.mention + " "
                except:
                    continue

        if mentionStr == '':
            embedInfo.add_field(name="Following channels are toggled on: ", value="No Channels toggled on use ~toggle", inline=False)
        else:
            embedInfo.add_field(name="Following channels are toggled on: ", value=mentionStr, inline=False)

        if botStr == '':
            embedInfo.add_field(name="Following bots are ignored: ", value="No bots are ignored ~ignore <@bot>", inline=False)
        else:
            embedInfo.add_field(name="Following bots are ignored: ", value=botStr, inline=False)

        if str(DATA[val][1]) == '0':
            embedInfo.add_field(name="Image Snipe: ", value="disabled", inline=True)
        else:
            embedInfo.add_field(name="Image Snipe:  ", value="enabled", inline=True)

        embedInfo.add_field(name="Timer set at: __" + str(DATA[val][0]) + " seconds__", value="\u200b", inline=True)

        embedInfo.add_field(name="Support Server",value='*https://discord.gg/mXPGpTMsqS*', inline=False)
        embedInfo.set_footer(text="Requested by: " + ctx.message.author.name + "\nAuthors: AyamDobhal#1672, moizmoizmoizmoiz#5923, sona#5766")
        await ctx.send(embed=embedInfo)
    
    @commands.command(name="invite")
    async def invite(self, ctx):
        embed_invite = discord.Embed(
            title="Click here to invite me",
            colour=COLORS["accent"],
            url='https://discord.com/api/oauth2/authorize?client_id=777575449957498890&permissions=17918992&scope=bot'
        )
        embed_invite.add_field(name="Support Server",value='*https://discord.gg/mXPGpTMsqS*', inline=False)
        embed_invite.set_footer(text="\nFor help contact eliminabot@gmail.com")
        await ctx.send(embed=embed_invite)
    
    @commands.command(name="vote")
    async def vote(self, ctx):
        voteEmbed = discord.Embed(
            title = "Click here to vote for me",
            color = COLORS["accent"],
            url = "https://top.gg/bot/777575449957498890/vote"
        )
        voteEmbed.add_field(name="Support Server",value='*https://discord.gg/mXPGpTMsqS*', inline=False)
        voteEmbed.set_footer(text="\nFor help contact eliminabot@gmail.com")
        return await ctx.send(embed=voteEmbed)

def setup(bot):
    bot.add_cog(Info(bot))
    print("Info loaded.")