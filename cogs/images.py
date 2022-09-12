from ast import alias
from discord.ext import commands
from discord import embeds
from random import choice, randint
from bot import BenjaminBowtieBot
from oauth2 import OAuth2

import datetime
import os
import requests

class Images(commands.Cog):
    def __init__(self, bot: BenjaminBowtieBot):
        self._bot = bot

        # DA Authorization
        # https://www.deviantart.com/developers/authentication
        DA_AUTH_URL = "https://www.deviantart.com/oauth2/authorize"
        DA_TOKEN_URL = "https://www.deviantart.com/oauth2/token"

        # Remove the initial token, refresh_token, and code if you're running
        # this bot on a system where you can open the webbrowser for auth.
        self._DA_OAUTH = OAuth2(
            DA_AUTH_URL, 
            DA_TOKEN_URL, 
            os.getenv("DA_CLIENT_ID"), 
            os.getenv("DA_CLIENT_SECRET"),
            os.getenv("DA_OAUTH_TOKEN"),
            os.getenv("DA_OAUTH_REFRESH_TOKEN"),
            os.getenv("DA_OAUTH_CODE"))
        self._DA_OAUTH.auth("gallery", "browse")

    @commands.command(name="xkcd", help="Gets the latest XKCD or a specific comic if a number is given.")
    async def xkcd_handler(self, context: commands.Context, arg=None):
        response = None
        if arg is None:
            response = requests.get("https://xkcd.com/info.0.json")
        elif not arg.isdecimal():
            await context.send("Usage: b!xkcd {optional comic number}")
            return
        else:
            comic_num = int(arg)
            response = requests.get(f"https://xkcd.com/{comic_num}/info.0.json")

        if not response.ok:
            await context.send(f"Error: The XKCD API responded with {response.status_code}!")
            return

        data = response.json()
        date = datetime.datetime(int(data["year"]), int(data["month"]), int(data["day"]))

        embed = embeds.Embed(
            title=f"XKCD #{data['num']}: {data['title']}",
            description=f"Alt Text: {data['alt']}",
            timestamp=date
        )
        embed.set_image(url=data["img"])
        await context.send(embed=embed)

    @commands.command(name="fractal", help="Gets a random fractal image from a select group of fractal artists.")
    async def fractal_handler(self, context: commands.Context):
        artist = choice(["ThoughtWeaver", "tatasz", "ChaosFissure", "bezo97", "senzune", "c-91", "technochroma"])
        params = {
            "username": artist,
            "with_session": False,
            "mature_content": False,
            "limit": 20,
            # This is a naive way of randomizing, based on the fact that all the above artists have 200+ deviations
            "offset": 20 * randint(0, 10)
        }
        response = self._DA_OAUTH.get("https://www.deviantart.com/api/v1/oauth2/gallery/all", params)
        if not response.ok:
            await context.send(f"Error: The DA API responded with {response.status_code}!")
            return

        data = response.json()
        filtered = list(filter(lambda x: x["category_path"] == "visual_art" or "fractal" in x["category_path"], data["results"]))
        result = choice(filtered)

        embed = embeds.Embed(
            title=result["title"],
            timestamp=datetime.datetime.fromtimestamp(int(result["published_time"]))
        )
        embed.set_author(
            name=result["author"]["username"],
            icon_url=result["author"]["usericon"]
        )
        embed.set_image(url=result["content"]["src"])
        await context.send(embed=embed)


async def setup(bot: BenjaminBowtieBot):
    await bot.add_cog(Images(bot))
