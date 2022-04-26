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
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .tio import Tio


class Compiler(commands.Cog):
    """
    Runs code using the TIO api.
    """

    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    async def initialize(self, bot: Red):
        await bot.wait_until_red_ready()

    async def red_delete_data_for_user(self, **kwargs):
        return

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)

    @commands.command(name="compile", aliases=["run"])
    async def execute_code(self, ctx, lang: str, args=None):
        """
        Runs code in 600+ languages.

        `[p]compile <language> <code>`

        PLEASE NOTE: due to discord.py limitations,
        if you would like to run code that has double brackets -
        " in it, you must type a \ flipped backslash in front of it.
        """
        query = " ".join(args[:])

        query = query.replace(("```" + lang), "")

        if lang == "python3":
            query = query.replace('"', "'")
            query = query.replace("```python", "")

        query = query.replace("`", "")
        query = query.strip()
        query = query.replace("\\n", ";")

        site = Tio()
        request = site.new_request(lang, query)

        embed = discord.Embed(
            title=f"{lang} code evaluation",
            color=await ctx.embed_color(),
        )
        embed.add_field(name="**Result**", value=site.send(request))
        embed.set_footer(text="Powered by TIO.RUN")

        await ctx.send(embed=embed)
