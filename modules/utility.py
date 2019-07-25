import discord
from discord.ext import commands
import json
import datetime
import time
import typing

class Utility(commands.Cog):
    """General utility commands"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.command("ping")
    async def ping(self, ctx):
        latency = self.client.latency
        await ctx.send("Pong! *{}ms*".format(round(latency * 1000)))

    @commands.command("clear")
    async def clear(self, ctx):
        """Send a blank message to clear chat"""
        blank = ""
        for i in range(35):
            blank += "\n\u200B"

        await ctx.send(blank + "`Chat cleared by {0}`".format(ctx.author))

    @commands.command("botinfo")
    async def botinfo(self, ctx):
        """Display information about the bot"""
        app = await self.client.application_info()
        botMember = discord.utils.find(lambda m: m.id == self.client.user.id, ctx.guild.members)

        embed = discord.Embed(
            description = app.description,
            color = botMember.color
        )

        embed.set_author(
            name = "{0} Information".format(app.name),
            icon_url = botMember.avatar_url
        )

        embed.add_field(
            name = ":regional_indicator_a: Username",
            value = botMember,
            inline = True
        )
        
        embed.add_field(
            name = ":large_blue_circle: Status",
            value = botMember.status,
            inline = True
        )

        embed.add_field(
            name = ":video_game: Activity",
            value = botMember.activity,
            inline = True
        )

        uptime = time.time() - self.client.stats.start_time
        uptimeString = ""

        if (uptime < 60): # Seconds
            uptimeString = "{0} seconds".format(round(uptime, 2))
        elif (uptime < 60 * 60): # Minutes
            uptimeString = "{0} minutes".format(round(uptime / 60, 2))
        elif (uptime < 60 * 60 * 24): # Hours
            uptimeString = "{0} hours".format(round(uptime / 60 / 60, 2))
        else: # Days
            uptimeString = "{0} days".format(round(uptime / 60 / 60 / 24, 2))

        embed.add_field(
            name = ":clock3: Uptime",
            value = uptimeString,
            inline = True
        )

        created = self.client.user.created_at
        embed.add_field(
            name = ":birthday: Date Created",
            value = created.strftime("%d.%m.%Y at %H:%M"),
            inline = True
        )

        age = (datetime.datetime.now() - created).days
        embed.add_field(
            name = ":calendar_spiral: Age",
            value = "{0} days ({1} years)".format(age, round(age / 365, 2)),
            inline = True
        )

        embed.add_field(
            name = ":european_castle: Servers",
            value = len(self.client.guilds)
        )

        embed.add_field(
            name = ":busts_in_silhouette: Users",
            value = len(self.client.users)
        )

        embed.add_field(
            name = ":robot: Commands Processed",
            value = self.client.stats.commands_processed
        )

        await ctx.send(embed = embed)

    @commands.command("serverinfo")
    async def serverinfo(self, ctx, guildID: typing.Optional[int] = None):
        """Display server information"""
        if (guildID == None or guildID not in (g.id for g in self.client.guilds)): 
            guildID = ctx.guild.id
            # await ctx.send("Server ID not recognized, displaying this server instead.")
            
        guild = self.client.get_guild(guildID)            

        embed = discord.Embed(
            description = guild.description
        )

        embed.set_author(
            name = "{0} Information".format(guild.name),
            icon_url = guild.icon_url
        )

        embed.add_field(
            name = ":regional_indicator_a: Name",
            value = guild.name
        )

        embed.add_field(
            name = ":exclamation: Verification Level",
            value = guild.verification_level
        )

        embed.add_field(
            name = ":earth_americas: Region",
            value = guild.region
        )

        created = guild.created_at
        embed.add_field(
            name = ":birthday: Date Created",
            value = created.strftime("%d.%m.%Y at %H:%M")
        )

        age = (datetime.datetime.now() - created).days
        embed.add_field(
            name = ":calendar_spiral: Age",
            value = "{0} days ({1} years)".format(age, round(age / 365, 2)),
        )

        embed.add_field(
            name = ":microphone2: Broadcast Channel",
            value = guild.system_channel.name
        )

        embed.add_field(
            name = ":sleeping: AFK Channel",
            value = guild.afk_channel.name
        )

        embed.add_field(
            name = ":loudspeaker: Voice Channels",
            value = len(guild.voice_channels)
        )

        embed.add_field(
            name = ":speech_left: Text Channels",
            value = len(guild.text_channels)
        )

        embed.add_field(
            name = ":busts_in_silhouette: Total Users",
            value = guild.member_count
        )

        embed.add_field(
            name = ":gem: Nitro Boosts",
            value = len(guild.premium_subscribers)
        )

        embed.add_field(
            name = ":robot: Bot Count",
            value = len(list(b for b in guild.members if (b.bot)))
        )

        await ctx.send(embed = embed)

    @commands.command("userinfo")
    async def userinfo(self, ctx, user: typing.Optional[discord.Member] = None):
        """Get information about your user or given user ID"""
        if (user == None): 
            user = ctx.author
            # await ctx.send("User not recognized, displaying your information instead.")

        embed = discord.Embed()

        embed.set_author(
            name = "{0} Information".format(user),
            icon_url = user.avatar_url
        )

        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Utility(client))
