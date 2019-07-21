import discord
from discord.ext import commands
import json
import datetime
import time

class Utility(commands.Cog):
    """General utility commands"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.command("ping")
    async def ping(self, ctx):
        latency = self.client.latency
        await ctx.send("Pong! *{}ms*".format(round(latency * 1000)))

    @commands.command("botinfo")
    async def botinfo(self, ctx):
        app = await self.client.application_info()
        botMember = discord.utils.find(lambda m: m.id == self.client.user.id, ctx.guild.members)

        embed = discord.Embed(
            title = "**{0}** Information".format(app.name), 
            description = app.description
        )

        embed.add_field(
            name = ":regional_indicator_a: Username",
            value = self.client.user,
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
            uptimeString = "{0} hours".format(round(uptime / 60 / 60), 2)
        else: # Days
            uptimeString = "{0} days".format(round(uptime / 60 / 60 / 24), 2)

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
    async def serverinfo(self, ctx):
        embed = discord.Embed(
            title = "**{0}** Information".format(ctx.guild.name)
        )

        await ctx.send(embed = embed)

    @commands.command("userinfo")
    async def userinfo(self, ctx):
        embed = discord.Embed(
            title = "**{0}** Information".format(ctx.author.name)
        )

        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Utility(client))
