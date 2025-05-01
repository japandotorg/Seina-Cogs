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

import abc
from typing import Generic, TypeVar, Union

import discord
from redbot.core import commands
from redbot.core.bot import Red

try:
    from emoji import EMOJI_DATA
except ImportError:
    from emoji import (
        UNICODE_EMOJI_ENGLISH as EMOJI_DATA,  # pyright: ignore[reportAttributeAccessIssue]
    )


T = TypeVar("T")


class Finder(abc.ABC, Generic[T]):
    @abc.abstractmethod
    async def finder(self, interaction: discord.Interaction[Red], argument: str) -> T:
        raise NotImplementedError


class EmojiFinder(Finder[Union[str, discord.Emoji]], commands.EmojiConverter):
    async def convert(self, ctx: commands.Context, argument: str) -> Union[str, discord.Emoji]:
        if argument in EMOJI_DATA:
            return argument
        try:
            return await super().convert(ctx, argument=argument)
        except commands.BadArgument:
            raise commands.UserFeedbackCheckFailure(
                "Failed to get/convert the emoji, try again later."
            )

    async def finder(
        self, interaction: discord.Interaction[Red], argument: str
    ) -> Union[str, discord.Emoji]:
        if argument in EMOJI_DATA:
            return argument
        ctx: commands.Context = await interaction.client.get_context(interaction)
        try:
            return await super().convert(ctx, argument=argument)
        except commands.BadArgument:
            raise commands.BadArgument("Failed to get/convert the emoji, try again later.")
