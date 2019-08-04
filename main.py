import discord
from discord.ext import tasks, commands
import asyncio
import logging
import json
import time
from collections import namedtuple

class AtlasClient(commands.AutoShardedBot):
    """Custom Atlas Client inheriting Bot"""

    ## SETUP ##
    def __init__(self):
        # Load Configuration
        self.config = self.read_config()
        
        # Init bot
        super().__init__(
            command_prefix = self.config["prefix"], 
            activity = discord.Game(self.config["activity"])
        )

        # Allow custom !help command
        self.remove_command("help")
        # Used for embed message color
        self.color = discord.Color.from_rgb(
            self.config["color"][0],
            self.config["color"][1],
            self.config["color"][2]
        )

        # Init bot stats
        botStats = namedtuple("botStats", "start_time commands_processed")
        botStats.start_time = time.time()
        botStats.commands_processed = 0
        self.botStats = botStats

        logging.basicConfig(level = logging.WARNING)

    # IO Config
    def write_config(self, data):
        """Write data to file with specified config"""
        with open("data/config.json", "w", encoding = "utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii = False, indent = 4)

    def read_config(self):
        """Read data from file to specified config"""
        try:
            with open("data/config.json") as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            print("Configuration file not found. Please create /data/config.json.")

    # IO Guild
    def write_guild(self, data, guild: discord.Guild):
        """Write guild and guild preferences to file"""
        with open("data/guilds/g{0}.json".format(guild.id), "w", encoding = "utf-8") as json_file:
            return json.dump(data, json_file, ensure_ascii = False, indent = 4)

    def read_guild(self, guild: discord.Guild):
        """Read guild and guild preferences from file"""
        try:
            with open("data/guilds/g{0}.json".format(guild.id), "w", encoding = "utf-8") as json_file:
                return json.load(json_file)
        except IOError:
            # Create default file if it does not exist
            guildData = {
                "id": guild.id,
                "name": guild.name
            }
            return self.write_guild(guildData, guild)

    # IO User
    def write_user(self, data, member: discord.User):
        """Write user and user preferences to file"""
        with open("data/users/u{0}.json".format(member.id), "w", encoding = "utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii = False, indent = 4)

    def read_user(self, member: discord.User):
        """Read user and user preferences from file"""
        try:
            with open("data/users/u{0}.json".format(member.id), "w", encoding = "utf-8") as json_file:
                return json.load(json_file)
        except IOError:
            # Create default file if it does not exist
            userData = {
                "id": member.id,
                "name": member.name,
            }
            self.write_user(userData, member)

    ## EVENTS ##
    # Fires when bot logs in
    async def on_connect(self):
        """Prepare bot modules and data"""
        for module in self.config["modules"]:
                self.load_extension("modules.{0}".format(module))
                print(">> Loaded {0} module".format(module))

        print("> Loaded {0} module(s)".format(len(self.config["modules"])))
        app = await self.application_info()
        await self.user.edit(username = app.name)
        print("> Username set as \"{0}\"".format(app.name))

    # Fires when bot is ready to receive commands
    async def on_ready(self):
        """Confirm client readyness to console"""
        print("> Logged in as {0.user}".format(client))
        print("> Command prefix \'{0}\'".format(client.config["prefix"]))

        # Setup guild files
        for guild in self.guilds:
            guildData = self.read_guild(guild)
            print(">> Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

        # Setup user files
        for user in self.users:
            userData = self.read_user(user)

        print("> Connected to {0} guild(s) -- {1} user(s)".format(len(client.guilds), len(client.users)))

    # Fires everytime a message is sent
    async def on_message(self, message):
        """Process command if valid"""
        if (message.author == client.user or 
            not message.content.startswith(self.config["prefix"])): # Ignore messages sent by itself
            return

        # Handle command using modules
        # await self.process_commands(message)
        ctx = await self.get_context(message, cls = commands.Context)
        if (ctx.valid): await self.invoke(ctx)

        self.botStats.commands_processed += 1

    async def on_command_error(self, ctx, error):
        """Handle error"""
        if(isinstance(error, commands.MissingPermissions)):
            await ctx.send("Cannot access command.")
        else:
            print(error)

## CONNECT & LOGIN ##
try:
    # client.run(client.config["token"], bot = True, reconnect = True)
    client = AtlasClient()
    client.loop.run_until_complete(client.start(
        client.config["token"], 
        bot = True, 
        reconnect = True)
    )
except KeyboardInterrupt:
    client.loop.run_until_complete(client.logout())
finally:
    client.loop.close()