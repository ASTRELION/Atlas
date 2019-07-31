import discord
from discord.ext import commands
import json
import datetime
import time
import typing

class Moderation(commands.Cog, name = "Moderation"):
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
    async def ban(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Ban given user from the server"""
        guild = ctx.guild
        await guild.ban(user, reason = reason)

    @commands.command("unban")
    async def unban(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Unban given user from the server"""
        guild = ctx.guild
        await guild.unban(user, reason = reason)

    @commands.command("softban")
    async def softban(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Ban and immediately unban given user from the server"""
        guild = ctx.guild
        await guild.ban(user, reason = "SOFTBAN: {0}".format(reason))
        await guild.unban(user, reason = "SOFTBAN: {0}".format(reason))

    @commands.group("mute")
    async def mute(self, ctx):
        if (ctx.invoked_subcommand is None): # No subcommand implementation
            await ctx.send("Please use !mute voice or !mute text")
        
    @mute.command("voice") #mute voice
    async def mutevoice(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Prevent given user from speaking in voice channels"""
        await user.edit(mute = True, reason = reason)

    @mute.command("text") #mute text
    async def mutetext(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Prevent given user from typing in text channels"""
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(user, send_messages = False, reason = reason)

    @commands.command("unmute")
    async def unmute(self, ctx, user: discord.Member):
        """Unmute given user and restore speaking and typing capabilities"""
        try:
            await user.edit(mute = False, reason = "Unmuted {0}".format(user))
        except:
            pass

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(user, send_messages = None, reason = "Unmuted {0}".format(user))

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

    @commands.command("clear")
    async def clear(self, ctx):
        """Send a blank message to clear chat"""
        blank = "\n\u200B" * 50
        await ctx.send(blank + "`Chat cleared by {0}`".format(ctx.author))

    @commands.command("purge")
    @commands.bot_has_permissions(manage_channels = True)
    @commands.has_permissions(manage_channels = True)
    async def purge(self, ctx, *, reason: typing.Optional[str] = None):
        """Delete this channel and clone it anew"""
        await ctx.channel.clone(name = None, reason = reason)
        await ctx.channel.delete(reason = reason)

def setup(client):
    client.add_cog(Moderation(client))
