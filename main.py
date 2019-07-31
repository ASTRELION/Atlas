import discord
from discord.ext import tasks, commands
import asyncio
import logging
import json
import time
from collections import namedtuple

class AtlasClient(commands.Bot):
    """Custom Atlas Client inheriting Bot"""

    def __init__(self):
        # Load Configuration
        self.config = {}
        with open("./config.json") as json_config:
            self.config = json.load(json_config)
        
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

    # Fires when bot logs in
    async def on_connect(self):
        """Prepare bot modules and data"""
        for module in self.config["modules"]:
                self.load_extension("modules.{0}".format(module))
                print(">> Loaded {0} module".format(module))

        print("> Loaded {0} module(s)".format(len(self.config["modules"])))

    # Fires when bot is ready to receive commands
    async def on_ready(self):
        """Confirm client readyness to console"""
        print("> Logged in as {0.user}".format(client))
        print("> Command prefix \'{0}\'".format(client.config["prefix"]))

        for guild in client.guilds:
            print(">> Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

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

    async def on_command_error(self, ctx, exception):
        """Handle error"""
        print(exception)

# Connect & Login
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