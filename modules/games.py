import discord
from discord.ext import commands
import json
import datetime
import time
import typing
import random

class Games(commands.Cog):
    """General utility commands"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.command("roll", aliases = ["r"])
    async def roll(self, ctx, times: typing.Optional[int] = 1, sides: typing.Optional[int] = 6):
        """Roll a dice specified times with specified sides"""
        if (times * sides > 1000):
            await ctx.send("*ERROR: `Number of rolls x dice sides` should be less than 1000*")
            return

        rolls = []
        rollSum = 0
        rollProduct = 1

        for i in range(times):
            roll = random.randint(1, sides)
            rolls.append(roll)
            rollSum += roll
            rollProduct *= roll
        
        result = "{0}\n`Rolling {1}d{2}:` :game_die: ".format(
            ctx.author.mention, 
            times, 
            sides)
        result += "\n**{0}**\n".format(", ".join(str(r) for r in rolls))
        result += "`Sum: {0}`\n`Product: {1}`\n`Average: {2}`\n`w/ Advantage: {3}`\n`w/ Disadvantage: {4}`".format(
            rollSum,
            rollProduct,
            round(rollSum / len(rolls), 2),
            max(rolls),
            min(rolls))
        await ctx.send(result)        

def setup(client):
    client.add_cog(Games(client))