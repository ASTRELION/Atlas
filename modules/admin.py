import discord
from discord.ext import commands
import json

class Admin(commands.Cog):
    """Administrative commands to be used by Bot and Server owners"""

    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.command("setactivity")
    @commands.is_owner()
    async def setactivity(self, ctx, *, activity):
        """Set the bot playing status"""
        self.config["activity"] = activity

        with open('config.json', 'w', encoding='utf-8') as json_config:
            json.dump(self.config, json_config, ensure_ascii = False, indent = 4)

        await self.client.change_presence(activity = discord.Game(self.config["activity"]))

    @commands.command("reload")
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        """Reload a module"""
        module = str.lower(module)
        self.client.reload_extension("modules.{0}".format(module))
        await ctx.send("{0} module reloaded.".format(module))

def setup(client):
    client.add_cog(Admin(client))