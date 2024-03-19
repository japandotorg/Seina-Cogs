from redbot.core.bot import Red

from .core import AutoReact


async def setup(bot: Red) -> None:
    cog: AutoReact = AutoReact(bot)
    await bot.add_cog(cog)
