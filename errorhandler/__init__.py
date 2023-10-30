from redbot.core.bot import Red

from .core import ErrorHandler


async def setup(bot: Red) -> None:
    cog = ErrorHandler(bot)
    await bot.add_cog(cog)
