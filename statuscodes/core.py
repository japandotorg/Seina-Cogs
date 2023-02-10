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

import difflib
from io import BytesIO
from typing import Any, Dict, Final, List, Literal, Tuple, Type, TypeVar

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .util import STATUS_CODES

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

RTT = TypeVar("RTT", bound="RequestType")


class StatusCodes(commands.Cog):
    """
    Find the meaning behind various status codes.
    """

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)
        self.bot: Red = bot

    async def cog_load(self) -> None:
        await self.bot.wait_until_red_ready()

    async def red_get_data_for_user(self, *, user_id: int) -> Dict[str, BytesIO]:
        """Get a user's personal data."""
        data: Any = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(
        self, *, requester: Type[RTT], user_id: int
    ) -> Dict[str, BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        data: Any = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)

    @commands.command(name="statuscodes", aliases=["statuscode"])
    async def statuscodes(self, ctx: commands.Context, *, code=None) -> None:
        """
        Find the meaning behind various status codes.
        """
        embed = discord.Embed(color=await ctx.embed_color())

        if not code:
            for codes in STATUS_CODES.values():
                message = ""

                for code, tag in codes.items():
                    if not code.isdigit():
                        continue
                    message += f"\n{code} {tag}"

                embed.add_field(
                    name=codes["title"],
                    value=f"{codes['message']}\n```prolog\n{message}\n```",
                    inline=False,
                )
            return await ctx.send(embed=embed)

        group = code[0]
        info = STATUS_CODES.get(group)
        if not info:
            statuses = {}
            for data in STATUS_CODES.values():
                for scode, tag in data.items():
                    if scode.isdigit():
                        statuses[tag] = scode
            match = difflib.get_close_matches(
                code,
                [*statuses],
                n=1,
                cutoff=0.0,
            )
            code = statuses[match[0]]
            info = STATUS_CODES.get(code[0])

            if not info:
                embed.description = f"```No {code} status code found in the {group}xx group```"
                return await ctx.send(embed=embed)

            embed.title = info["title"]
            embed.description = f"{info['message']}\n```prolog\n{code} {info[code]}```"
            await ctx.send(embed=embed)
