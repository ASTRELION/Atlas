import discord
from discord.ext import commands
import json
import datetime
import time
import typing
import requests
import re
import os
from threading import Thread

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

    def update_database(self):
        """Update local DnD data"""
        self.client.logger.warning("Starting DnD database update...")
        for r in self.resources:
            # Create resource .json
            rName = self.getAlphaNum(r).lower()
            with open(self.client.DND_LOC + "{0}.json".format(rName), "w", encoding = "utf-8") as json_file:
                json.dump(self.getResource(r), json_file, ensure_ascii = False, indent = 4)

            # Populate resource folder with data
            os.makedirs(self.client.DND_LOC + "{0}/".format(rName), exist_ok = True)
            for i in self.getResource(r):
                try:
                    iName = self.getAlphaNum(i["name"]).lower()
                    with open(self.client.DND_LOC + "{0}/{1}.json".format(rName, iName), "w", encoding = "utf-8") as json_file:
                        json.dump(requests.get(i["url"]).json(), json_file, ensure_ascii = False, indent = 4)
                except KeyError:
                    iName = self.getAlphaNum(i["class"]).lower()
                    with open(self.client.DND_LOC + "{0}/{1}.json".format(rName, iName), "w", encoding = "utf-8") as json_file:
                        json.dump(requests.get(i["url"]).json(), json_file, ensure_ascii = False, indent = 4)
        
        self.client.logger.warning("Dnd database update complete.")

    @commands.command("dupdate")
    async def dupdate(self, ctx):
        """Update local DnD data"""
        thread = Thread(target = self.update_database)
        thread.start()
        # thread.join()
        await ctx.send("Update in progress. Please allow a few minutes for the database to download.")

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