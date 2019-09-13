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
        self.client.logger.info("Connected")
        app = await self.client.application_info()
        await self.client.user.edit(username = app.name)
        self.client.logger.info("Username set to \"{0}\"".format(app.name))

    # Fires when bot is ready to receive commands
    @commands.Cog.listener()
    async def on_ready(self):
        """Confirm client readyness to console"""
        self.client.logger.info("Logged in as {0.user}".format(self.client))
        self.client.logger.info("Command prefix \"{0}\"".format(self.client.config["prefix"]))

        # Setup guild files
        for guild in self.client.guilds:
            guildData = self.client.read_guild(guild)
            self.client.write_guild(guildData, guild)
            self.client.logger.info("Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

        # Setup user files
        for user in self.client.users:
            userData = self.client.read_user(user)
            self.client.write_user(userData, user)

        self.client.logger.info("Connected to {0} guild(s) -- {1} user(s)".format(len(self.client.guilds), len(self.client.users)))

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
        self.client.logger.error("{0} tried to use \"{1}\" in server \"{2}\"".format(ctx.author, ctx.message.content, ""))
        if(isinstance(error, commands.MissingPermissions)):
            await ctx.send("ERROR: You are missing the following permission(s): {0}".format(",".join(error.missing_perms)))
        elif(isinstance(error, commands.CommandOnCooldown)):
            await ctx.send("ERROR: You must wait {0} seconds before using that command again.".format(int(error.retry_after)))
        elif(isinstance(error, commands.ExtensionError)):
            await ctx.send("ERROR: Extension was not found or could not be loaded.")
        else:
            self.client.logger.info(error)

def setup(client):
    client.add_cog(Events(client))