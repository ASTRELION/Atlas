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

        extensions = {
            "events",
            "modules.admin",
            "modules.moderation",
            "modules.utility"
        }

        for ext in extensions:
            self.load_extension(ext)
            print(">> Loaded {0} extension".format(ext))

        print("> Loaded {0} extensions(s)".format(len(extensions)))

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
        # Refresh meta data
        data["id"] = guild.id
        data["name"] = guild.name
        data["user_count"] = guild.member_count
        data["text_channels"] = len(guild.text_channels)
        data["voice_channels"] = len(guild.voice_channels)
        data["users"] = list(u.id for u in guild.members)
        # Write
        with open("data/guilds/g{0}.json".format(guild.id), "w", encoding = "utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii = False, indent = 4)

    def read_guild(self, guild: discord.Guild):
        """Read guild and guild preferences from file"""
        try:
            with open("data/guilds/g{0}.json".format(guild.id)) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            # Create default file if it does not exist
            guildData = {}
            self.write_guild(guildData, guild)
            return self.read_guild(guild)

    # IO User
    def write_user(self, data, user: discord.User):
        """Write user and user preferences to file"""
        # Refresh meta data
        data["id"] = user.id
        data["name"] = str(user)
        # Write
        with open("data/users/u{0}.json".format(user.id), "w", encoding = "utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii = False, indent = 4)

    def read_user(self, user: discord.User):
        """Read user and user preferences from file"""
        try:
            with open("data/users/u{0}.json".format(user.id)) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            # Create default file if it does not exist
            userData = {}
            self.write_user(userData, user)
            return self.read_user(user)

    async def on_message(self, message): pass

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