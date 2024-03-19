from redbot.core.bot import Red

from .core import BoostUtils


async def setup(bot: Red) -> None:
    cog: BoostUtils = BoostUtils(bot)
    await bot.add_cog(cog)