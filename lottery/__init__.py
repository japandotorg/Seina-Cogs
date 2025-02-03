from redbot.core.bot import Red

from .core import Lottery


async def setup(bot: Red) -> None:
    cog: Lottery = Lottery(bot)
    await bot.add_cog(cog)
