import discord
from discord.ext import commands
import json
import datetime
import time
import typing
import random

class Channels(commands.Cog):
    """General utility commands"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.command("setcategory")
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def setcategory(self, ctx, *, category: discord.CategoryChannel):
        """Set a category as the place to place newly created private channels"""
        guildData = self.client.read_guild(ctx.guild)
        guildData["private_category"] = category.id
        self.client.write_guild(guildData, ctx.guild)

    @commands.group("voice")
    @commands.guild_only()
    async def voice(self, ctx):
        """Base command for managing private voice channels"""
        if (ctx.invoked_subcommand is None):
            await ctx.send("Please use command with a subcommand.")

    @voice.command("list")
    @commands.guild_only()
    async def voice_list(self, ctx):
        """List all currently active private voice channels"""
        guildData = self.client.read_guild(ctx.guild)

        channelString = ""
        for id in guildData["private_voice"]:
            user = ctx.guild.get_member(int(id))
            channel = ctx.guild.get_channel(guildData["private_voice"][id])
            channelString += "{0} owned by {1}\n".format(channel, user)

        await ctx.send(channelString)

    @voice.command("create")
    @commands.guild_only()
    async def voice_create(self, ctx, channelName: typing.Optional[str] = None):
        """Create a new private voice channel"""
        guildData = self.client.read_guild(ctx.guild)
        if (str(ctx.author.id) in guildData["private_voice"]):
            await ctx.send("You already have a channel with ID {0}.".format(guildData["private_voice"][str(ctx.author.id)]))
            return

        # Set channel name
        if (channelName is None): channelName = "{0}'s Channel".format(ctx.author.display_name)

        # Voice channel permissions
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(connect = False),
            ctx.author: discord.PermissionOverwrite(connect = True),
            ctx.guild.me: discord.PermissionOverwrite(manage_channels = True, connect = True)
        }

        # Create channel
        privateCategory = ctx.guild.get_channel(guildData["private_category"])
        userChannel = await ctx.guild.create_voice_channel(
            channelName, 
            category = privateCategory, 
            overwrites = overwrites)
        guildData["private_voice"][ctx.author.id] = userChannel.id

        self.client.write_guild(guildData, ctx.guild)

    @voice.command("destroy")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels = True)
    async def voice_destroy(self, ctx):
        """Permanently delete your private channel, if it exists"""
        guildData = self.client.read_guild(ctx.guild)
        if (str(ctx.author.id) not in guildData["private_voice"]):
            await ctx.send("You do not own a private voice channel.")
            return

        # Remove channel
        channel = ctx.guild.get_channel(guildData["private_voice"][str(ctx.author.id)])
        await channel.delete()
        guildData["private_voice"].pop(str(ctx.author.id), None)
        self.client.write_guild(guildData, ctx.guild)

    @voice.command("add")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels = True)
    async def voice_add(self, ctx, user: discord.Member):
        """Add specified user to your private channel"""

    @voice.command("del")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels = True)
    async def voice_del(self, ctx, user: typing.Optional[discord.Member] = None):
        """Remove a user from your voice channel, or all users if none is specified"""


def setup(client):
    client.add_cog(Channels(client))