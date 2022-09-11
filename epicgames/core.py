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
from typing import List
from datetime import datetime

import discord
from redbot.core.bot import Red # type: ignore
from redbot.core import commands # type: ignore

FREE_GAMES = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
PARAMS = { "allowCountries": "US", "country": "US", "locale": "en_US" }

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
            f"Cog Version: **{self.__version__}**"
            f"Author: **{self.__author__}**"
        ]
        return "\n".join(text)
    
    def _get_image(images: List[dict]):
        result = None
        for _item in images:
            if _item["type"] == "DieselStoreFrontTall":
                result = _item["url"]
                break
        return result
    
    def _get_game_list(self):
        response = requests.get(FREE_GAMES, params=PARAMS).json()
        games = {
            "current": {},
            "upcoming": {}
        }
        
        image_to_display = None
        
        for resp in response["data"]["Catalog"]["searchStore"]["elements"]:
            if not resp["promotions"]:
                continue
            
            is_available_now = bool(resp["promotions"]["promotionalOffers"])
            promo_key = "promotionalOffers" if is_available_now else "upcomingPromotionalOffers"
            promo_type = "current" if is_available_now else "upcoming"
            date_key = "endDate" if is_available_now else "startDate"
            promo_title = resp["title"]
            promo_time = datetime.strptime(
                resp["promotions"][promo_key][0]["promotionalOffers"][0][date_key], "%Y-%m-%dT%H:%M:%S.%fZ"
            ).strftime("%m/%d")
            
            if promo_time not in games[promo_type]:
                games[promo_type][promo_time] = []
                
            games[promo_type][promo_time].append(promo_title)
            
            if is_available_now and image_to_display is None:
                image_to_display = self._get_image(resp["KeyImages"])
                
        return games, image_to_display
    
    @commands.guild_only()
    @commands.command(name="epicgames", aliases=["freegames", "egs", "freegame"])
    async def _epic_games(self, ctx: commands.Context):
        """
        Finds free game info from epic games promotional api.
        """
        embed: discord.Embed = discord.Embed(
            title="Free Epic Games!",
            color=await ctx.embed_color()
        )
        
        game_list, image_to_display = self._get_game_list()
        
        embed.set_image(url=image_to_display)
        
        for day, games in game_list["current"].items():
            embed.add_field(
                name="Free until {}".format(day),
                value="\n".join(games),
                inline=False,
            )
            
        for day, games in game_list["upcoming"].items():
            embed.add_field(
                name="Free starting {}".format(day),
                value="\n".join(games),
                inline=False,
            )
            
        await ctx.send(embed=embed)
