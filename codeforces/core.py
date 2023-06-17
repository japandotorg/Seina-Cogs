"""
MIT License

Copyright (c) 2023-present japandotorg

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

import io
import aiohttp
from datetime import datetime
from typing import Dict, Any, Final, List, Literal, Optional

import discord
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list


RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class CodeForces(commands.Cog):
    """
    Search users on Codeforces.
    """
    
    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.0"
    
    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        
    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, io.BytesIO]:
        """
        Nothing to delete
        """
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"User_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, io.BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Optional[int] = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def get_user(self, username: str) -> Dict[str, Any]:
        API_URL = "https://codeforces.com/api/user.info?handles=" + username + ";"
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL) as response:
                user_json = await response.json()
                return user_json

    @commands.has_permissions(embed_links=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="codeforces", aliases=["cfuser"])
    async def _codeforces(self, ctx: commands.Context, username: str):
        """
        Search user on https://codeforces.com/
        """
        handle = await self.get_user(username)
        if handle["status"] == "FAILED":
            error_embed: discord.Embed = discord.Embed(
                title="Error!",
                description=handle["comment"],
                color=await ctx.embed_color(),
            )
            await ctx.send(embed=error_embed)
            return
        for res in handle["result"]:
            async with ctx.typing():
                embed: discord.Embed = discord.Embed(
                    title=username,
                    description=(res["firstName"] if "firstName" in res else "")
                    + " "
                    + (res["lastName"] if "lastName" in res else ""),
                    color=await ctx.embed_color(),
                )
                embed.add_field(
                    name="City",
                    value=res["city"] if "city" in res else "unknown",
                    inline=True,
                )
                embed.add_field(
                    name="Country",
                    value=res["country"] if "country" in res else "unknown",
                    inline=True,
                )
                embed.add_field(
                    name="Friends",
                    value=res["friendOfCount"],
                    inline=True,
                )
                embed.add_field(
                    name="Rating",
                    value=res["rating"],
                    inline=True,
                )
                embed.add_field(
                    name="Rank",
                    value=res["rank"],
                    inline=True,
                )
                embed.add_field(
                    name="Max Rating",
                    value=res["maxRating"],
                    inline=True,
                )
                embed.add_field(
                    name="Max Rank",
                    value=res["maxRank"],
                    inline=True,
                )
                embed.add_field(
                    name="Organization",
                    value=res["organization"] if res["organization"] != "" else "unknown",
                    inline=True,
                )
                embed.add_field(
                    name="Last Online",
                    value=datetime.utcfromtimestamp(res["lastOnlineTimeSeconds"]).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    inline=True,
                )
                embed.set_thumbnail(url=res["avatar"])
            await ctx.send(embed=embed)
