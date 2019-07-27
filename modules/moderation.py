import discord
from discord.ext import commands
import json
import datetime
import time
import typing

class Moderation(commands.Cog):
    """Server moderation commands"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.command("kick")
    async def kick(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Kick given user from the server"""
        guild = ctx.guild
        await guild.kick(user, reason = reason)

    @commands.command("ban")
    async def ban(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Ban given user from the server"""
        guild = ctx.guild
        await guild.ban(user, reason = reason)

    @commands.command("unban")
    async def unban(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Unban given user from the server"""
        guild = ctx.guild
        await guild.unban(user, reason = reason)

    @commands.command("softban")
    async def softban(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Ban and immediately unban given user from the server"""
        guild = ctx.guild
        await guild.ban(user, reason = "SOFTBAN: {0}".format(reason))
        await guild.unban(user, reason = "SOFTBAN: {0}".format(reason))

    @commands.command("banlist")
    async def banlist(self, ctx):
        """List all currently active bans in this server"""
        bans = await ctx.guild.bans()
        banString = ""
        for ban in bans:
            banString += "{0} for \"{1}\"".format(ban.user.name, ban.reason)

        embed = discord.Embed(
            title = "Banned Users",
            description = banString or "None"
        )

        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Moderation(client))
