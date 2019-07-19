import discord
from discord.ext import commands
import json

class Utility(commands.Cog):
    """General utility commands"""

    def __init__(self, bot):
        self.bot = bot
        self.config = bot.config

    @commands.command("ping")
    async def ping(self, ctx):
        latency = self.bot.latency
        await ctx.send("Pong! *{}ms*".format(round(latency * 1000)))

def setup(bot):
    bot.add_cog(Utility(bot))
