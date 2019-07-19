import discord
from discord.ext import commands
import json;

config = {}
with open("./config.json") as json_config:
    config = json.load(json_config)

# client = discord.Client()
bot = commands.Bot(command_prefix = config["prefix"])
bot.config = config;

# On Ready
@bot.event
async def on_ready():
    """Confirm bot readyness to console"""
    print("> Logged in as {0.user}".format(bot))
    print("> Command prefix \'{0}\'".format(bot.config["prefix"]))

    for module in config["modules"]:
        bot.load_extension("modules.{0}".format(module))
        print(">> Loaded {0} module".format(module))

    print("> Loaded {0} module(s)".format(len(config["modules"])))

    sumUsers = 0;

    for guild in bot.guilds:
        sumUsers += len(guild.members)
        print(">> Connected to guild \"{0}\" -- {1} users".format(guild.name, len(guild.members)))

    print("> Connected to {0} guild(s) -- {1} user(s)".format(len(bot.guilds), sumUsers))

    await bot.change_presence(activity = discord.Game(">_"))

# On Message
@bot.event
async def on_message(message):
    """Process command if valid"""
    if (message.author == bot.user): # Ignore messages sent by itself
        return

    # Handle command using modules
    await bot.process_commands(message)

# Connect & Login
bot.run(config["token"], bot = True)
