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

import re
from typing import TYPE_CHECKING, Dict, Optional, Union, cast

import discord
from emoji import EMOJI_DATA
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


class UnicodeOrPartialEmojiConverter(commands.Converter[Union[str, discord.PartialEmoji]]):
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Union[str, discord.PartialEmoji]:
        argument: str = argument.strip()
        return (
            argument
            if argument in EMOJI_DATA.keys()
            else await commands.PartialEmojiConverter().convert(ctx, argument)
        )


class PollAnswerConverter(commands.Converter[Dict[str, Union[str, discord.PartialEmoji, None]]]):
    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Dict[str, Union[str, discord.PartialEmoji, None]]:
        split = re.split(r";|\||-", argument)
        try:
            answer, emoji = split
        except ValueError:
            answer, emoji = split[0], None
        if not 1 <= (length := len(answer)) <= 300:
            raise commands.BadArgument(
                "Question can only be of 300 characters, recieved {} instead.".format(length)
            )
        if emoji is not None:
            emoji: Optional[Union[str, discord.PartialEmoji]] = (
                await UnicodeOrPartialEmojiConverter().convert(ctx, cast(str, emoji).strip())
            )
        return {"text": answer, "emoji": emoji}
