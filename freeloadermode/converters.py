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

from typing import Dict

from redbot.core import commands

from ._tagscript import TagError


class TagScriptConverter(commands.Converter[str]):
    async def convert(self, ctx: commands.GuildContext, argument: str) -> str:
        try:
            await ctx.cog._validate_tagscript(argument)  # type: ignore
        except TagError as e:
            raise commands.BadArgument(str(e))
        return argument


class TimeConverter(commands.Converter[int]):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        conversions: Dict[str, int] = {
            "s": 1,
            "m": 60,
            "h": 3600,
            "d": 86400,
            "w": 604800,
            "mo": 604800 * 30,
        }
        if str(argument[-1]) not in conversions:
            if not str(argument).isdigit():
                raise commands.BadArgument(
                    f"Unable to convert {argument} to a time.",
                )
            return int(argument)

        multiplier = conversions[str(argument[-1])]
        argument = argument[:-1]

        if not str(argument).isdigit():
            raise commands.BadArgument(
                f"Unable to convert {argument} to a time.",
            )
        if int(argument) * multiplier <= 0:
            raise commands.BadArgument(
                "You cannot have a time less than 0.",
            )

        return int(argument) * multiplier


class BanLengthConverter(commands.Converter[int]):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        if not argument.isnumeric():
            raise commands.BadArgument(
                "Please enter a valid time length.",
            )
        elif int(argument) < 1:
            raise commands.BadArgument(
                "You cannot set the time length to anything less than 1 day.",
            )
        elif int(argument) > 7:
            raise commands.BadArgument(
                "You cannot set the time length to anything greater than 7 days."
            )
        return int(argument)
