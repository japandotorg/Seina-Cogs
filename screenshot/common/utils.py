"""
MIT License

Copyright (c) 2024-present japandotorg

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

# isort: off
import hashlib
import logging
import functools
from typing import TYPE_CHECKING, Callable

import discord
from redbot.core import commands

if TYPE_CHECKING:
    from ..core import Screenshot

try:
    import regex as re
except ModuleNotFoundError:
    import re as re
# isort: on


log: logging.Logger = logging.getLogger("red.seina.screenshot.core")


def counter(func: Callable[["Screenshot"], str]) -> Callable[["Screenshot"], str]:
    @functools.wraps(func)
    def wrapper(self: "Screenshot") -> str:
        string: str = func(self)
        return hashlib.sha1(string.encode("utf-8")).hexdigest()

    return wrapper


class URLConverter(commands.Converter[str]):
    async def convert(self, ctx: commands.Context, argument: str) -> str:
        if not re.match(r"https?://", argument):
            return "https://{}".format(argument)
        return argument


class DeleteView(discord.ui.View):
    def __init__(self, *, timeout: float = 120.0) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message = discord.utils.MISSING
