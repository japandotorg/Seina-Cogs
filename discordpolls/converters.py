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

from typing import TYPE_CHECKING, List, Optional, Tuple

import discord
from redbot.core import commands

if TYPE_CHECKING:
    PollConverter = discord.Poll
else:

    class PollConverter(commands.MessageConverter):
        async def convert(self, ctx: commands.Context, argument: str) -> discord.Poll:
            message: discord.Message = await super().convert(ctx, argument)
            if not (poll := message.poll):
                raise commands.BadArgument(
                    "[**Message**](<{}>) does not have a poll attached.".format(
                        message.jump_url.strip()
                    )
                )
            return poll


class QuestionConverter(commands.Converter[Tuple[str, Optional[discord.PartialEmoji]]]):
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Tuple[str, Optional[discord.PartialEmoji]]:
        split: List[str] = argument.split(";")
        if (sl := len(split)) < 1 or not split[0] or sl > 2:
            raise commands.BadArgument("Invalid argument: `{}`.".format(str))
        question: str = split[0]
        if (length := len(question)) > 300:
            raise commands.BadArgument(
                "Question can only be of 300 characters, recieved {}.".format(length)
            )
        if emoji_id := split[1]:
            emoji: Optional[discord.PartialEmoji] = await commands.PartialEmojiConverter().convert(
                ctx, emoji_id
            )
        else:
            emoji: Optional[discord.PartialEmoji] = None
        return question, emoji


class OptionConverter(commands.Converter[Tuple[str, Optional[discord.PartialEmoji]]]):
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Tuple[str, Optional[discord.PartialEmoji]]:
        split: List[str] = argument.split("|")
        if (sl := len(split)) < 1 or not split[0] or sl > 2:
            raise commands.BadArgument("Invalid argument: `{}`.".format(str))
        question: str = split[0]
        if (length := len(question)) > 55:
            raise commands.BadArgument(
                "Option answer text can only be of 55 characters, recieved {}.".format(length)
            )
        if emoji_id := split[1]:
            emoji: Optional[discord.PartialEmoji] = await commands.PartialEmojiConverter().convert(
                ctx, emoji_id
            )
        else:
            emoji: Optional[discord.PartialEmoji] = None
        return question, emoji
