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
    @commands.guild_only()
    @commands.bot_has_permissions(kick_members = True)
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Kick given user from the server"""
        guild = ctx.guild
        await guild.kick(user, reason = reason)

    @commands.command("ban")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Ban given user from the server"""
        guild = ctx.guild
        await guild.ban(user, reason = reason)

    @commands.command("unban")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, user: discord.User, *, reason: typing.Optional[str] = None):
        """Unban given user from the server"""
        guild = ctx.guild
        await guild.unban(user, reason = reason)

    @commands.command("softban")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def softban(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Ban and immediately unban given user from the server"""
        guild = ctx.guild
        await guild.ban(user, reason = "SOFTBAN: {0}".format(reason))
        await guild.unban(user, reason = "SOFTBAN: {0}".format(reason))

    @commands.group("mute")
    @commands.guild_only()
    @commands.bot_has_permissions(mute_members = True)
    @commands.has_permissions(mute_members = True)
    async def mute(self, ctx):
        if (ctx.invoked_subcommand is None): # No subcommand implementation
            await ctx.send("Please use !mute voice or !mute text")
        
    @mute.command("voice") #mute voice
    @commands.guild_only()
    @commands.bot_has_permissions(mute_members = True)
    @commands.has_permissions(mute_members = True)
    async def mute_voice(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Prevent given user from speaking in voice channels"""
        await user.edit(mute = True, reason = reason)

    @mute.command("text") #mute text
    @commands.guild_only()
    @commands.bot_has_permissions(mute_members = True)
    @commands.has_permissions(mute_members = True)
    async def mute_text(self, ctx, user: discord.Member, *, reason: typing.Optional[str] = None):
        """Prevent given user from typing in text channels"""
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(user, send_messages = False, reason = reason)

    @commands.command("unmute")
    @commands.guild_only()
    @commands.bot_has_permissions(mute_members = True)
    @commands.has_permissions(mute_members = True)
    async def unmute(self, ctx, user: discord.Member):
        """Unmute given user and restore speaking and typing capabilities"""
        try:
            await user.edit(mute = False, reason = "Unmuted {0}".format(user))
        except:
            pass

        for channel in ctx.guild.text_channels:
            await channel.set_permissions(user, send_messages = None, reason = "Unmuted {0}".format(user))

    @commands.command("banlist")
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
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
    @commands.bot_has_permissions(manage_messages = True)
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx):
        """Send a blank message to clear chat"""
        blank = "\n\u200B" * 50
        await ctx.send(blank + "`Chat cleared by {0}`".format(ctx.author))

    @commands.command("announce")
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(manage_messages = True)
    async def announce(self, ctx, *, message: str):
        """Announce a message to this channel via @everyone and an embed message"""
        embed = discord.Embed(
            title = "Announcement",
            description = message
        )

        await ctx.send(ctx.guild, embed = embed)

    @commands.command("purge")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_channels = True)
    @commands.has_permissions(manage_channels = True)
    async def purge(self, ctx, *, reason: typing.Optional[str] = None):
        """Delete this channel and clone it anew"""
        await ctx.channel.clone(name = None, reason = reason)
        await ctx.channel.delete(reason = reason)

    @commands.group("helpop")
    @commands.guild_only()
    async def helpop(self, ctx):
        """Send a dm to all registered op users"""
        if (ctx.invoked_subcommand is None):
            await ctx.send("Please use in conjunction with a subcommand.")

    @helpop.command("msg")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(send_messages = True)
    @commands.cooldown(1, 5 * 60, commands.BucketType.user)
    async def helpop_msg(self, ctx, *, message):
        guildData = self.client.read_guild(ctx.guild)
        for id in guildData["helpop_users"]:
            op = ctx.guild.get_member(id)
            dmChannel = op.dm_channel or await op.create_dm()
            await dmChannel.send("**{0} ({1}) via helpop:**\n{2}".format(
                ctx.author, 
                ctx.guild.name,
                message))

    @helpop.command("add")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(administrator = True)
    async def helpop_add(self, ctx, user: discord.Member):
        """Add user to list of helpop enabled users"""
        guildData = self.client.read_guild(ctx.guild)

        if (user.id not in guildData["helpop_users"]): # Add to set
            guildData["helpop_users"].append(user.id)
        
        self.client.write_guild(guildData, ctx.guild)

    @helpop.command("del")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(administrator = True)
    async def helpop_del(self, ctx, user: discord.Member):
        """Remove user from list of helpop enabled users"""
        guildData = self.client.read_guild(ctx.guild)

        if (user.id in guildData["helpop_users"]):
            guildData["helpop_users"].remove(user.id)
            print(guildData["helpop_users"])
        else:
            await ctx.send("Specified user is not an op.")

        self.client.write_guild(guildData, ctx.guild)

def setup(client):
    client.add_cog(Moderation(client))
