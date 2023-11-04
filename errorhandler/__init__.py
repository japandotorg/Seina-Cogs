"""
GNU General Public License Version 3.0

Copyright (c) 2018-2023 Sitryk
Copyright (c) 2023-present japandotorg
"""

from redbot.core.bot import Red

from .core import ErrorHandler


async def setup(bot: Red) -> None:
    cog = ErrorHandler(bot)
    await bot.add_cog(cog)
