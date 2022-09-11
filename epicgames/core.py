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

from datetime import datetime

import discord
import pytz
from redbot.core import commands  # type: ignore
from redbot.core.bot import Red  # type: ignore

from .utils import _fetch_free_games  # type: ignore


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
        data = _fetch_free_games()

        for game in data["data"]["Catalog"]["searchStore"]["elements"]:
            if (
                game["price"]["totalPrice"]["originalPrice"] != 0
                and game["promotions"] is not None
            ):
                now = False

                if len(game["promotions"]["promotionalOffers"]) > 0:
                    now = True
                elif len(game["promotions"]["upcomingPromotionalOffers"]) > 0:
                    now = False

                embed: discord.Embed = discord.Embed(
                    title=game["title"],
                    color=(discord.Color.green() if now else discord.Color.red()),
                )
                embed.add_field(
                    name="Publisher:",
                    value=game["seller"]["name"],
                    inline=False,
                )
                embed.add_field(
                    name="Original Price:",
                    value=game["price"]["totalPrice"]["fmtPrice"]["originalPrice"],
                    inline=False,
                )

                game_data = datetime.strptime(
                    game["promotions"][
                        ("promotionalOffers" if now else "upcomingPromotionalOffers")
                    ][0]["promotionalOffers"][0][("endDate" if now else "startDate")],
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                ).replace(tzinfo=pytz.utc)

                embed.add_field(
                    name=("Ends:" if now else "Starts:"),
                    value=game_data.astimezone(pytz.timezone("US/Eastern")).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    + " EST",
                )
                
                for image in game['keyImages']:
                    if image['type'] == 'OfferImageWide':
                        url = image['url']

                        embed.set_image(url=url)

                await ctx.send(embed=embed)
