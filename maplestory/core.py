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

import discord
from redbot.core.bot import Red # type: ignore
from redbot.core import commands # type: ignore

from .utils import _fetch_user

class MapleStory(commands.Cog):
    """
    Retrives information from the MapleStory API.
    """
    
    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"
    
    async def red_delete_data_for_user(self, **kwargs):
        """
        No data to delete.
        """
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
    @commands.command(name="maplestory", aliases=["mpinfo"])
    async def _maple_story(self, ctx: commands.Context, *args):
        """
        A simple command which fetches user information from the maplestory API servers.
        """
        username = " ".join(args)
        data = _fetch_user(username)
        overall_data = data[0]
        world_data = data[1]
        
        info = (
            "```prolog\n"
            "Overall Rank : {}\n"
            "World        : {}\n"
            "World Rank   : {}\n"
            "Job          : {}\n"
            "Level        : {}\n"
            "Exp          : {}\n"
            "\n```"
        ).format(
            overall_data["Rank"],
            overall_data["WorldName"],
            world_data["Rank"],
            overall_data["JobName"],
            overall_data["Level"],
            overall_data["Exp"],
        )
        
        embed: discord.Embed = discord.Embed(
            title=overall_data["CharacterName"],
            color=await ctx.embed_color()
        )
        embed.add_field(
            name="Info:",
            value=info
        )
        embed.set_image(
            url=overall_data["CharacterImgUrl"]
        )
        
        await ctx.send(embed=embed)
