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
        self.client.write_config(self.config)
        await self.client.change_presence(activity = discord.Game(self.config["activity"]))

    @commands.command("reload")
    @commands.is_owner()
    async def reload(self, ctx, *, module: str):
        """Reload a module"""
        module = str.lower(module)
        self.client.reload_extension("modules.{0}".format(module))
        await ctx.send("{0} module reloaded.".format(module))

    @commands.command("users")
    @commands.has_permissions(administrator = True)
    async def users(self, ctx):
        """List all users in the guild file associated with this server"""
        data = self.client.read_guild(ctx.guild)

        userList = ""
        for id in data["users"]:
            userList += "{0}\n".format(str(self.client.get_user(id)))

        await ctx.send(userList)

def setup(client):
    client.add_cog(Admin(client))