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

import re
import time
from io import BytesIO
from typing import Any, Dict, Final, List

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .utils import bin_float, hex_float, oct_float, safe_eval


class Calculator(commands.Cog):
    """
    Does math
    """

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

    @classmethod
    async def initialize(cls, bot: Red) -> None:
        await bot.wait_until_red_ready()

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Any = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)

    @commands.command(name="calculate", aliases=["calc", "c"])
    async def calc(self, ctx: commands.Context, num_base: str, *, expr: str = ""):
        """
        Does math.

        It has access to the following basic math functions
        ceil, comb, [fact]orial, gcd, lcm, perm, log, log2,
        log10, sqrt, acos, asin, atan, cos, sin, tain
        and the constants pi, e, tau.

        num_base: str
            The base you want to calculate in.
            Can be heex, oct, bin and for decimal ignore this argument
        expr: str
            A expression to calculate.
        """
        num_bases: Dict[str, Any] = {
            "h": (16, hex_float, "0x"),
            "o": (8, oct_float, "0o"),
            "b": (2, bin_float, "0b"),
        }

        start: float = time.monotonic()

        base, method, prefix = num_bases.get(num_base[0].lower(), (None, None, None))

        if not base:  # If we haven't given a base it is decimal
            base = 10
            expr = f"{num_base} {expr}"  # we want the whole expression

        if prefix:
            expr = expr.replace(prefix, "")  # Remove the prefix for a simple regex

        regex = r"[0-9a-fA-F]+" if base == 16 else r"\d+"

        if method:  # no need to extract numbers if we aren't converting
            numbers = [int(num, base) for num in re.findall(regex, expr)]
            expr = re.sub(regex, "{}", expr).format(*numbers)

        result: Any = safe_eval(compile(expr, "<calc>", "eval", flags=1024).body)

        end: float = time.monotonic()

        embed: discord.Embed = discord.Embed(color=await ctx.embed_color())

        if method:
            embed.description = (
                f"```py\n{expr}\n\n>>> {prefix}{method(result)}\n\nDecimal: {result}```"
            )
            embed.set_footer(text=f"Calculated in {round((end - start) * 1000, 3)} ms")
            return await ctx.send(embed=embed)

        embed.description = f"```py\n{expr}\n\n>>> {result}```"
        embed.set_footer(text=f"Calculated in {round((end - start) * 1000, 3)} ms")
        await ctx.send(embed=embed)
