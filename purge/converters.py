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

from typing import Annotated, Literal, Optional

import discord
from redbot.core import commands


class Snowflake(object):
    @classmethod
    async def convert(cls, ctx: commands.GuildContext, argument: str) -> int:
        try:
            return int(argument)
        except ValueError:
            param = ctx.current_parameter
            if param:
                raise commands.BadArgument(
                    f"{param.name} argument expected a Discord ID not {argument!r}.",
                )
            raise commands.BadArgument(
                f"Expected a Discord ID not {argument!r}.",
            )


class RawMessageIdsConverter(commands.Converter[int]):
    async def convert(self, ctx: commands.GuildContext, argument: str) -> int:
        if argument.isnumeric() and len(argument) >= 17 and int(argument) < 2**63:
            return int(argument)
        raise commands.BadArgument(
            f"`{argument}` does not look like a valid message ID.",
        )


class PurgeFlags(commands.FlagConverter):
    user: Optional[discord.User] = commands.flag(
        description="Remove messages from this user", default=None
    )
    contains: Optional[str] = commands.flag(
        description="Remove messages that contains this string (case sensitive)", default=None
    )
    prefix: Optional[str] = commands.flag(
        description="Remove messages that start with this string (case sensitive)", default=None
    )
    suffix: Optional[str] = commands.flag(
        description="Remove messages that end with this string (case sensitive)", default=None
    )
    after: Annotated[Optional[int], Snowflake] = commands.flag(
        description="Search for messages that come after this message ID", default=None
    )
    before: Annotated[Optional[int], Snowflake] = commands.flag(
        description="Search for messages that come before this message ID", default=None
    )
    bot: bool = commands.flag(
        description="Remove messages from bots (not webhooks!)", default=False
    )
    webhooks: bool = commands.flag(description="Remove messages from webhooks", default=False)
    embeds: bool = commands.flag(description="Remove messages that have embeds", default=False)
    files: bool = commands.flag(description="Remove messages that have attachments", default=False)
    emoji: bool = commands.flag(
        description="Remove messages that have custom emoji", default=False
    )
    reactions: bool = commands.flag(
        description="Remove messages that have reactions", default=False
    )
    require: Literal["any", "all"] = commands.flag(
        description='Whether any or all of the flags should be met before deleting messages. Defaults to "all"',
        default="all",
    )
