import discord
from discord.ext import commands
import json
import typing

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
    async def reload(self, ctx, *, extension: typing.Optional[str] = None):
        """Reload an extension or all extensions"""
        if (extension is None): # Reload all extensions
            for ext in self.config["extensions"]:
                self.client.reload_extension(ext)
            await ctx.send("All extensions reloaded.")
        else: # Reload single extension
            extension = str.lower(extension)
            self.client.reload_extension(extension)
            await ctx.send("{0} extension reloaded.".format(extension))

    @commands.command("load")
    @commands.is_owner()
    async def load(self, ctx, *, extension: str):
        """Load a new extension"""
        extension = str.lower(extension)
        self.client.load_extension(extension)
        await ctx.send("{0} extension loaded.".format(extension))

    @commands.command("users")
    @commands.guild_only()
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