import discord
from discord.ext import commands
import json
import datetime
import time
import typing
import re
import os
from threading import Thread
import aiohttp

def setup(client):
    client.add_cog(DnD(client))

class DnD(commands.Cog, name = "DnD"):
    """Dungeons and Dragons specific commands (5e)"""

    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.dndAPI = "http://www.dnd5eapi.co/api/"
        self.resources = {
            "ability-scores",
            "classes",
            "conditions",
            "damage-types",
            "equipment-categories",
            "equipment",
            "features",
            "languages",
            # "levels",
            "magic-schools",
            "monsters",
            "proficiencies",
            "races",
            "skills",
            "spellcasting",
            "spells",
            "startingequipment",
            "subclasses",
            "subraces",
            "traits",
            "weapon-properties"
        }

    def getAlphaNum(self, string: str):
        """Return string as alpha-numeric only"""
        return re.sub("[^0-9a-zA-Z]+", "", string)

    def getResource(self, resource: str):
        """Returns given resource from the DnD API"""
        # req = requests.get(self.dndAPI + resource.lower()).json()
        # return req["results"]
        with open(self.client.DND_LOC + "{0}.json".format(self.getAlphaNum(resource).lower())) as json_file:
            return json.load(json_file)

    def findByName(self, resource: str, name: str):
        """Return list of resources matching given name"""
        # s = re.sub('[^0-9a-zA-Z]+', '*', s)
        name = self.getAlphaNum(name).lower()
        resource = self.getAlphaNum(resource).lower()
        results = []

        for i in self.getResource(resource):
            item = None
            try:
                item = self.getAlphaNum(i["name"]).lower()
            except KeyError:
                item = self.getAlphaNum(i["class"]).lower()

            if (name in item):
                # req = requests.get(i["url"]).json()
                with open(self.client.DND_LOC + "{0}/{1}.json".format(resource, item)) as json_file:
                    req = json.load(json_file)
                    results.append(req)

        return results

    def getResourceContent(self, resource: str):
        """Return list of all content in a resource"""
        resource = self.getAlphaNum(resource).lower()
        result = []
        for file in os.listdir(self.client.DND_LOC + resource):
            with open(self.client.DND_LOC + "{}/{}".format(resource, file)) as json_file:
                req = json.load(json_file)
                result.append(req)

        return result

    async def update_database(self):
        """Update local DnD data"""
        self.client.logger.warning("Starting DnD database update...")
        for r in self.resources:
            # Create resource .json
            # Fetch online resource
            res = None
            async with aiohttp.ClientSession() as session:
                async with session.get(self.dndAPI + r) as ses:
                    if ses.status == 200:
                        res = await ses.json()
                        res = res["results"]

            rName = self.getAlphaNum(r).lower()
            with open(self.client.DND_LOC + "{0}.json".format(rName), "w", encoding = "utf-8") as json_file:
                json.dump(res, json_file, ensure_ascii = False, indent = 4)

            # Populate resource folder with data
            os.makedirs(self.client.DND_LOC + "{0}/".format(rName), exist_ok = True)
            for i in res:
                item = None
                async with aiohttp.ClientSession() as session:
                    async with session.get(i["url"]) as ses:
                        if ses.status == 200:
                            item = await ses.json()
                try:
                    iName = self.getAlphaNum(i["name"]).lower()
                    with open(self.client.DND_LOC + "{0}/{1}.json".format(rName, iName), "w", encoding = "utf-8") as json_file:
                        json.dump(item, json_file, ensure_ascii = False, indent = 4)
                except KeyError:
                    iName = self.getAlphaNum(i["class"]).lower()
                    with open(self.client.DND_LOC + "{0}/{1}.json".format(rName, iName), "w", encoding = "utf-8") as json_file:
                        json.dump(item, json_file, ensure_ascii = False, indent = 4)
        
        self.client.logger.warning("Dnd database update complete.")

    @commands.command("dupdate")
    async def dupdate(self, ctx):
        """Update local DnD data"""
        await ctx.send("Update in progress. Please allow a few minutes for the database to download.")
        await self.update_database()

    @commands.command("dsearch")
    async def dsearch(self, ctx, *, keyword: str):
        """Search the entire DnD API for given keyword"""
        embed = discord.Embed(
            title = "DnD Search for \"{0}\"".format(keyword),
            color = self.client.color
        )

        for r in self.resources:
            # resource = self.getResource(r)
            data = self.findByName(r, keyword)

            if (len(data) > 0):
                results = "\u200B"

                for d in data:
                    try:
                        results += "{0}\n".format(d["name"])
                    except KeyError:
                        results += "{0}\n".format(d["class"])

                if (len(results) > 1000):
                    splitResults = results.split("\n")
                    embed.add_field(
                        name = r,
                        value = "\n".join(splitResults[:int(len(splitResults) / 2)]),
                        inline = False
                    )

                    embed.add_field(
                        name = r + " 2",
                        value = "\n".join(splitResults[int(len(splitResults) / 2):]),
                        inline = False
                    )
                else:
                    embed.add_field(
                        name = r,
                        value = results,
                        inline = False
                    )

        await ctx.send(embed = embed)

    @commands.command("dspell")
    async def dspell(self, ctx, *, spell: str):
        """Search for a DnD (5e) spell with given name"""
        # spells = self.getResource("spells")
        spellData = self.findByName("spells", spell)

        for s in spellData:
            embed = discord.Embed(
                title = "Spell **{0}**".format(s["name"]),
                description = "".join(s["desc"]),
                color = self.client.color
            )

            # Level (0 = cantrip)
            embed.add_field(
                name = "Level",
                value = s["level"]
            )

            # Components
            embed.add_field(
                name = "Components",
                value = " ".join(s["components"])
            )

            # Ritual
            embed.add_field(
                name = "Ritual?",
                value = s["ritual"]
            )

            # Range
            embed.add_field(
                name = "Range",
                value = s["range"]
            )

            # Casting Time
            embed.add_field(
                name = "Casting Time",
                value = s["casting_time"]
            )

            # Duration
            embed.add_field(
                name = "Duration",
                value = s["duration"]
            )

            # School
            embed.add_field(
                name = "School",
                value = s["school"]["name"]
            )

            # Classes
            embed.add_field(
                name = "Classes",
                value = "\u200B" + ", ".join(x["name"] for x in s["classes"])
            )

            # Sub-classes
            embed.add_field(
                name = "Sub-Classes",
                value = "\u200B" + ", ".join(x["name"] for x in s["subclasses"])
            )

            # Player Handbook Page
            embed.set_footer(
                text = "PHB Page #{0}".format(
                    next(int(s) for s in s["page"].split() if s.isdigit()))
            )

            await ctx.send(embed = embed)

    @commands.command("dcreate")
    async def dchar(self, ctx):
        """Create a new DnD character"""
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        charName = None
        charRace = None
        charClass = None

        await ctx.send("{0}, you started creating a new Dungeons & Dragons character.".format(ctx.author))

        # Character name
        await ctx.send(">Choose a __character name__.")
        msg = await self.client.wait_for("message", check = check, timeout = 60)
        charName = msg.content
        await ctx.send("*A character named **{0}** was born.*".format(charName))

        # Race
        races = list(x["name"] for x in self.getResourceContent("races"))

        while (charRace is None):
            await ctx.send(
                ">Choose a __race__.\n" +
                ">Choose __one__:\n" +
                ">>" + ", ".join(races)
            )
            msg = await self.client.wait_for("message", check = check, timeout = 60)

            for i in races:
                if (self.getAlphaNum(msg.content).lower() in self.getAlphaNum(i).lower()):
                    charRace = i

        await ctx.send("*A **{0}** was born, with the name of **{1}***.".format(charRace, charName))

        ## Sub-race
        if (self.getAlphaNum(charRace).lower() in ["elf", "dwarf", "halfling"]):
            races = list(x["name"] for x in self.getResourceContent("subraces") if charRace in x["name"])
            charRace = None

            while (charRace is None):
                await ctx.send(
                    ">Choose a __sub-race__.\n" +
                    ">Choose __one__:\n" +
                    ">>" + ", ".join(races)
                )
                msg = await self.client.wait_for("message", check = check, timeout = 60)

                for i in races:
                    if (self.getAlphaNum(msg.content).lower() in self.getAlphaNum(i).lower()):
                        charRace = i

            await ctx.send("*A **{0}** was born, with the name of **{1}***.".format(charRace, charName))

        # Class
        classes = list(x["name"] for x in self.getResourceContent("classes"))

        while (charClass is None):
            await ctx.send(
                ">Choose a __class__.\n" +
                ">Choose __one__:\n" +
                ">>" + ", ".join(classes)
            )
            msg = await self.client.wait_for("message", check = check, timeout = 60)

            for i in classes:
                if (self.getAlphaNum(msg.content).lower() in self.getAlphaNum(i).lower()):
                    charClass = i

        await ctx.send("*A **{}** **{}** was born and given the name of **{}**.*".format(charRace, charClass, charName))

        # 

        await ctx.send("Congratulations {0}, your character is complete.".format(ctx.author))