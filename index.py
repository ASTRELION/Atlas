import discord
from discord.ext import commands
import json;

config = {}
with open("./config.json") as json_config:
    config = json.load(json_config)

#client = discord.Client()
bot = commands.Bot(command_prefix = config["prefix"])

# On Ready
@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    print("Command prefix {}".format(bot.command_prefix))

# On Message
@bot.event
async def on_message(message):
    if (message.author == bot.user):
        return

    if (message.content.startswith(">hello")):
        await message.channel.send("Hello!")

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send("Pong! *{}ms*".format(round(latency * 1000)))

# Connect
bot.run(config["token"], bot = True)
