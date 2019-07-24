import discord
from discord.ext import commands
from data.stats import Stats
import json
import time

config = {}
with open("./config.json") as json_config:
    config = json.load(json_config)

client = commands.Bot(
    command_prefix = config["prefix"], 
    activity = discord.Game(config["activity"])
)
client.config = config
client.stats = Stats()

@client.event
async def on_connect():
    """Prepare bot modules and data"""
    for module in config["modules"]:
            client.load_extension("modules.{0}".format(module))
            print(">> Loaded {0} module".format(module))

    print("> Loaded {0} module(s)".format(len(config["modules"])))

# On Ready
@client.event
async def on_ready():
    """Confirm client readyness to console"""
    print("> Logged in as {0.user}".format(client))
    print("> Command prefix \'{0}\'".format(client.config["prefix"]))

    for guild in client.guilds:
        print(">> Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

    print("> Connected to {0} guild(s) -- {1} user(s)".format(len(client.guilds), len(client.users)))

# On Message
@client.event
async def on_message(message):
    """Process command if valid"""
    if (message.author == client.user): # Ignore messages sent by itself
        return

    # Handle command using modules
    await client.process_commands(message)
    client.stats.commands_processed += 1

# Connect & Login
client.run(config["token"], bot = True, reconnect = True)