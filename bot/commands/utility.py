import discord
import asyncio
import re

from discord.ext import commands
from discord import Embed

from bot.utils.utils import COLORS, SUPER_USERS
from bot.utils.fileHandler import DATA


snipe = {
    "id" : None,
    "content" : None,
    "author" : None,
    "attachment" : None,
    "guild" : None,
    "channel" : None
}

edit_snipe = {
    "author" : None,
    "content" : None,
    "guild" : None,
    "channel" : None
}


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.author.bot:
            return
        
        global snipe

        snipe["id"] = message.id
        snipe["author"] = message.author
        snipe["content"] = message.content
        snipe["guild"] = message.guild
        snipe["channel"] = message.channel

        if message.attachments:
            snipe["attachment"] = message.attachments[0].proxy_url

        await asyncio.sleep(60)

        if message.id == snipe["id"]:
            snipe["id"] = None
            snipe["author"] = None
            snipe["content"] = None
            snipe["attachment"] = None
            snipe["guild"] = None
            snipe["channel"] = None
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        global edit_snipe

        if before.author.bot:
            return

        edit_snipe["author"] = before.author
        edit_snipe["content"] = before.content
        edit_snipe["guild"] = before.guild
        edit_snipe["channel"] = before.channel

        await asyncio.sleep(60)

        if before.id == after.id:
            edit_snipe["author"] = None
            edit_snipe["content"] = None
            edit_snipe["guild"] = None
            edit_snipe["channel"] = None

    @commands.command(name="snipe")
    async def snipe(self, ctx):
        global snipe

        has_snipe = False
        author_roles = ctx.author.roles
        for role in author_roles:
            if role.name.lower() == 'sniper':
                has_snipe = True

        is_superuser = str(ctx.author.id) in SUPER_USERS

        if not is_superuser and not ctx.author.guild_permissions.administrator and not has_snipe:
            errorEmbed = Embed(
                title=None,
                color = COLORS["red"],
                description = "❌ You either need a role called `sniper` or be an `Administrator` to snipe."
            )
            x = await ctx.send(embed=errorEmbed)
            return await x.delete(delay=4)

        if snipe["guild"] != ctx.guild or snipe["channel"] != ctx.channel or snipe["content"] == None:
            errorEmbed = Embed(
                title=None,
                color = COLORS["red"],
                description = "❌ There is nothing to snipe!"
            )
            x = await ctx.send(embed=errorEmbed)
            return await x.delete(delay=4)

        if snipe["attachment"] and not is_superuser and not ctx.author.guild_permissions.administrator and str(DATA[str(ctx.guild.id)][1]) == '0':
            errorEmbed = Embed(
                title=None,
                color = COLORS["red"],
                description = "❌ There is nothing to snipe!"
            )
            x = await ctx.send(embed=errorEmbed)
            return await x.delete(delay=4)

        embed = discord.Embed(description=str(snipe["content"]), colour=COLORS["accent"])
        embed.set_footer(text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        if snipe["attachment"] is not None:
            embed.set_image(url=snipe["attachment"])
        embed.set_author(name="{0.name}#{0.discriminator}".format(snipe["author"]), icon_url=snipe["author"].avatar_url)
        await ctx.send(embed=embed)
        snipe["attachment"] = None
    
    @commands.command(name="editsnipe")
    async def editsnipe(self, ctx):
        has_snipe = False
        author_roles = ctx.author.roles
        for role in author_roles:
            if role.name.lower() == 'sniper':
                has_snipe = True

        is_superuser = str(ctx.author.id) in SUPER_USERS

        if not is_superuser and not ctx.author.guild_permissions.administrator and not has_snipe:
            errorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ You either need a role called `sniper` or be an `Administrator` to snipe."
            )
            x = await ctx.send(embed=errorEmbed)
            return await x.delete(delay=4)

        if edit_snipe["guild"] != ctx.guild or edit_snipe["channel"] != ctx.channel or edit_snipe["content"] == None:
            errorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ There is nothing to snipe!"
            )
            x = await ctx.send(embed=errorEmbed)
            return await x.delete(delay=4)

        embed = discord.Embed(description=str(edit_snipe["content"]), colour=COLORS["accent"])
        embed.set_footer(text=f"sniped by {ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
        embed.set_author(name="{0.name}#{0.discriminator}".format(edit_snipe["author"]), icon_url=edit_snipe["author"].avatar_url)
        await ctx.send(embed=embed)
    
    @commands.command(name="dctimer", aliases=["disconnect", "dc"])
    @commands.bot_has_guild_permissions(manage_channels=True, move_members=True)
    async def dctimer(self, ctx, time):
        if not ctx.author.voice:
            errorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ You're not connected to a voice channel!"
            )
            return await ctx.send(embed=errorEmbed)

        if time is None:
            errorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ Please specify a duration after which I should disconnect you!"
            )
            return await ctx.send(embed=errorEmbed)

        if not(bool(re.search(r'\d', time))):
            errorEmbed = Embed(
                title = None,
                color = COLORS["red"],
                description = "❌ Invalid value for time!"
            )
            return await ctx.send(embed=errorEmbed)

        if time[-1].lower() == 's':
            time = int(time[:len(time)-1])

        elif time[-1].lower() == 'm':
            time = int(time[:len(time)-1]) * 60

        elif time[-1].lower() == 'h':
            time = int(time[:len(time)-1]) * 60 * 60

        time = int(time)

        if time <= 0 or time > 10800:
            errorEmbed = Embed(
                title=None,
                color = COLORS["red"],
                description = "❌ Time must be between **1s** to **3h**."
            )
            return await ctx.send(embed=errorEmbed)
        
        dcEmbed = Embed(
            title = None,
            color = COLORS["green"],
            description = "✅ Timer for automatic disconnection set!"
        )
        await ctx.send(embed=dcEmbed)
        await asyncio.sleep(time)
        tempChannel = await ctx.guild.create_voice_channel("disconnect")
        await ctx.author.move_to(tempChannel, reason="disconnecting")
        await tempChannel.delete(reason="disconnected")
        await asyncio.sleep(30) # Cross-check if the channel is deleted.
        await tempChannel.delete(reason="disconnected")

def setup(bot):
    bot.add_cog(Utility(bot))
    print("Utility loaded.")