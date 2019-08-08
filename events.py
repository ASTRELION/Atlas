import discord
from discord.ext import commands
import json
import datetime
import time
import typing

class Events(commands.Cog):
    """Event handlers"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    # Fires when bot logs in
    @commands.Cog.listener()
    async def on_connect(self):
        """Prepare bot modules and data"""
        app = await self.client.application_info()
        await self.client.user.edit(username = app.name)
        print("> Username set as \"{0}\"".format(app.name))

    # Fires when bot is ready to receive commands
    @commands.Cog.listener()
    async def on_ready(self):
        """Confirm client readyness to console"""
        print("> Logged in as {0.user}".format(self.client))
        print("> Command prefix \'{0}\'".format(self.client.config["prefix"]))

        # Setup guild files
        for guild in self.client.guilds:
            guildData = self.client.read_guild(guild)
            self.client.write_guild(guildData, guild)
            print(">> Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

        # Setup user files
        for user in self.client.users:
            userData = self.client.read_user(user)
            self.client.write_user(userData, user)

        print("> Connected to {0} guild(s) -- {1} user(s)".format(len(self.client.guilds), len(self.client.users)))

    # Fires everytime a message is sent
    @commands.Cog.listener()
    async def on_message(self, message):
        """Process command if valid"""
        # Validate message as command
        if (message.author == self.client.user or 
                not message.content.startswith(self.config["prefix"])):
            return

        # Handle command using modules
        # await self.process_commands(message)
        ctx = await self.client.get_context(message, cls = commands.Context)
        if (ctx.valid): # TODO: Implement command-enabled by guild check
            await self.client.invoke(ctx)

    # Fires after a successful command
    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.client.botStats.commands_processed += 1

    # Fires everytime an error occurs
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle error"""
        print("{0} tried to use \"{1}\" in server \"{2}\"".format(ctx.author, ctx.message.content, "a"))
        if(isinstance(error, commands.MissingPermissions)):
            await ctx.send("You are missing the following permission(s): {0}".format(",".join(error.missing_perms)))
        elif(isinstance(error, commands.CommandOnCooldown)):
            await ctx.send("You must wait {0} seconds before using that command again.".format(int(error.retry_after)))
        else:
            print(error)

def setup(client):
    client.add_cog(Events(client))