"""
Mozilla Public License Version 2.0

Copyright (c) 2023-present japandotorg
"""

from typing import List

from redbot.core.bot import Red
from redbot.core.errors import CogLoadError

from .core import Purge

conflicting_cogs: List[str] = ["Cleanup"]


async def setup(bot: Red) -> None:
    for cog_name in conflicting_cogs:
        if bot.get_cog(cog_name):
            raise CogLoadError(
                f"This cog conflicts with {cog_name} and both cannot be loaded at the same time."
            )

    cog = Purge(bot)
    await bot.add_cog(cog)
