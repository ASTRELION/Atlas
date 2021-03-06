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

    def filter_cogs(self, cogs):
        for cog in cogs.values():
            if (len(cog.get_commands()) > 0): yield cog

    def help_builder(self, page, userID):
        """Generates embed for the help command"""
        page -= 1 # Adjust for indexing
        cogs = list(self.filter_cogs(self.client.cogs))
        if (page >= len(cogs)): page = 0
        names = list(x.qualified_name for x in cogs)
        cog = cogs[page]
        
        cmds = ""
        embed = discord.Embed(
            title = "**{0} Commands** | {1} Help - {2}".format(cog.qualified_name, self.client.user.name, userID),
            color = self.client.color
        )
        
        for cmd in cog.get_commands():
            if (not isinstance(cmd, commands.core.Group)): # Commands without groups
                cmds += "**{0}{1} {2}** -- {3}\n".format(
                    self.config["prefix"],
                    cmd.qualified_name,
                    cmd.signature,
                    cmd.help
                )
            else: # Commands in group
                subcommands = ""
                for subcmd in cmd.commands:
                    subcommands += "**{0}{1} {2}** -- {3}\n".format(
                        self.config["prefix"],
                        subcmd.qualified_name,
                        subcmd.signature,
                        subcmd.help
                    )

                embed.add_field(
                    name = "{0} Commands".format(cmd.name.title()),
                    value = subcommands
                )

        footer = " ".join("{0}-{1}".format(page + 1, name) for page, name in enumerate(names))
        embed.set_footer(text = footer)
        embed.description = cmds
        return embed

    @commands.command("help")
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(send_messages = True)
    async def help(self, ctx, page: typing.Optional[int] = 1):
        """Display commands ordered by module"""
        helpMessage = await ctx.send(embed = self.help_builder(page, ctx.author.id))
        
        # Messily add page reaction buttons
        for i in range(len(list(self.filter_cogs(self.client.cogs)))):
            charBytes = b"\u003%d\u20E3" % (i + 1)
            emoteString = charBytes.decode("unicode_escape")
            await helpMessage.add_reaction(emoteString)

    # Fires everytime a reaction is added to a message
    # Used to page through help command
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Change help page"""
        if (user != self.client.user and 
                len(reaction.message.embeds) > 0 and 
                "Atlas Help" in reaction.message.embeds[0].title and 
                str(user.id) in reaction.message.embeds[0].title):
            try:
                pageNum = int(str(str.encode(reaction.emoji))[2])
                embed = self.help_builder(pageNum, user.id)
                await reaction.message.edit(embed = embed)
                await reaction.remove(user)
            except:
                pass
            
    @commands.command("ping")
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(send_messages = True)
    async def ping(self, ctx):
        """Ping the bot"""
        latency = self.client.latency
        await ctx.send("Pong! *{}ms*".format(round(latency * 1000)))

    @commands.command("botinfo")
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(send_messages = True)
    async def botinfo(self, ctx):
        """Display information about the bot"""
        app = await self.client.application_info()
        botMember = self.client.user

        embed = discord.Embed(
            description = app.description,
            color = self.client.color
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
            value = "Online",
            inline = True
        )

        embed.add_field(
            name = ":video_game: Activity",
            value = self.client.activity,
            inline = True
        )

        uptime = time.time() - self.client.botStats.start_time
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
            value = self.client.botStats.commands_processed
        )

        await ctx.send(embed = embed)

    @commands.command("serverinfo")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(administrator = True)
    async def serverinfo(self, ctx, guildID: typing.Optional[int] = None):
        """Display server information"""
        if (guildID is None or guildID not in (g.id for g in self.client.guilds)): 
            guildID = ctx.guild.id
            # await ctx.send("Server ID not recognized, displaying this server instead.")
            
        guild = self.client.get_guild(guildID)            

        embed = discord.Embed(
            description = guild.description,
            color = self.client.color
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
            value = "None" if guild.system_channel is None else guild.system_channel.name
        )

        embed.add_field(
            name = ":sleeping: AFK Channel",
            value = "None" if guild.afk_channel is None else guild.afk_channel.name
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
    @commands.bot_has_permissions(send_messages = True)
    @commands.has_permissions(send_messages = True)
    async def userinfo(self, ctx, user: typing.Optional[discord.Member] = None):
        """Get information about your user or given user ID"""
        if (user == None): 
            user = ctx.author
            # await ctx.send("User not recognized, displaying your information instead.")

        embed = discord.Embed(
            color = user.color
        )
        
        embed.set_author(
            name = "{0} Information".format(user),
            icon_url = user.avatar_url
        )

        embed.add_field(
            name = ":regional_indicator_a: Full Username",
            value = user
        )

        embed.add_field(
                name = ":desktop: Display Name",
                value = user.display_name
            )
            
        embed.add_field(
            name = ":large_blue_circle: Status",
            value = None if ctx.guild is None else user.status
        )

        embed.add_field(
            name = ":video_game: Activity",
            value = None if ctx.guild is None or user.activity is None else user.activity.name
        )

        created = user.created_at
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
            name = ":medal: Highest Role",
            value = "None" if ctx.guild is None else user.top_role.name
        )

        embed.add_field(
            name = ":robot: Bot?",
            value = "No" if user.bot is False else "Yes"
        )

        embed.add_field(
            name = ":gem: Nitro Boosting?",
            value = "No" if ctx.guild is None or user.premium_since is None else "Yes"
        )

        await ctx.send(embed = embed)

    @commands.command("invite")
    @commands.bot_has_permissions(create_instant_invite = True)
    @commands.has_permissions(create_instant_invite = True)
    async def invite(self, ctx):
        """Generate an invite to this server"""
        invites = await ctx.guild.invites()
        channel = ctx.channel

        botInvites = list(x for x in invites if x.inviter.id == self.client.user.id and x.channel.id == channel.id)

        invite = None
        if (len(botInvites) == 0): # Create new invite in this channel
            await ctx.send("No previous invite found, creating a new one.")
            invite = await channel.create_invite(reason = "Bot created invite using !invite")
        else:
            await ctx.send("Previous invite found, retrieving that one.")
            invite = botInvites[0]

        await ctx.send(invite)

def setup(client):
    client.add_cog(Utility(client))
