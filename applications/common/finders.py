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
