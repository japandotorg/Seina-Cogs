"""
MIT License

Copyright (c) 2022-present japandotorg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
from bs4 import BeautifulSoup # type: ignore
from fake_useragent import UserAgent # type: ignore

import discord
import requests
from redbot.core import commands  # type: ignore
from redbot.core.bot import Red  # type: ignore

USER_AGENT = UserAgent()
HEADERS = {
    "User-Agent": USER_AGENT.random
}

FREE_GAMES = 'https://www.epicgames.com/store/ru/browse?sortBy=releaseDate&sortDir=DESC&priceTier=tierFree&count=1000'


class EpicGames(commands.Cog):
    """
    A simple cog to get data from the free games promotion api.
    """

    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"

    async def red_delete_data_for_user(self, **kwargs):
        return

    def __init__(self, bot: Red):
        self.bot: Red = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**" f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    @commands.guild_only()
    @commands.command(name="epicgames", aliases=["freegames", "egs", "freegame"])
    async def _epic_games(self, ctx: commands.Context):
        """
        Finds free game info from epic games promotional api.
        """
        HEADERS["User-Agent"] = USER_AGENT.random
        
        response = requests.get(FREE_GAMES, headers=HEADERS)
        
        soup = BeautifulSoup(response.content, "html.parser")
        items = soup.find_all("li", class_="css-lrwy1y")
        
        games = []
        
        for _item in items:
            if not _item.find("div", class_="css-1h2ruwl").get_text(strip=True) in games:
                games.append(_item.find("div", class_="css-1h2ruwl").get_text(strip=True))
                
        games = "\n".join(games)
        
        embed: discord.Embed = discord.Embed(
            title="Free Epic Games",
            description=games,
            color=await ctx.embed_color()
        )
        
        await ctx.send(embed=embed)
