import discord
from discord.ext import commands
from data.stats import Stats
import json
import time

class AtlasClient(commands.Bot):
    """Custom Atlas Client inheriting Bot"""

    def __init__(self):
        config = {}
        with open("./config.json") as json_config:
            config = json.load(json_config)

        super().__init__(
            command_prefix = config["prefix"], 
            activity = discord.Game(config["activity"])
        )

        self.config = config
        self.stats = Stats()
        self.remove_command("help")

    async def on_connect(self):
        """Prepare bot modules and data"""
        for module in self.config["modules"]:
                self.load_extension("modules.{0}".format(module))
                print(">> Loaded {0} module".format(module))

        print("> Loaded {0} module(s)".format(len(self.config["modules"])))

    async def on_ready(self):
        """Confirm client readyness to console"""
        print("> Logged in as {0.user}".format(client))
        print("> Command prefix \'{0}\'".format(client.config["prefix"]))

        for guild in client.guilds:
            print(">> Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

        print("> Connected to {0} guild(s) -- {1} user(s)".format(len(client.guilds), len(client.users)))

    async def on_message(self, message):
        """Process command if valid"""
        if (message.author == client.user): # Ignore messages sent by itself
            return

        # Handle command using modules
        await self.process_commands(message)
        self.stats.commands_processed += 1

# Connect & Login
client = AtlasClient()
client.run(client.config["token"], bot = True, reconnect = True)