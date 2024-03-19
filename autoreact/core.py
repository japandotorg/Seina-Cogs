import asyncio
import contextlib
from typing import Dict, Final, List, Self

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .abc import CompositeMetaClass
from .cache import Cache
from .events import EventMixin
from .commands import Commands


class AutoReact(
    commands.Cog,
    EventMixin,
    Commands,
    metaclass=CompositeMetaClass,
):
    """Create automatic reactions for triggers and pre-defined events."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.cache: Cache[Self] = Cache(self)
        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        default_guild: Dict[str, Dict[str, List[str]]] = {
            "reaction": {},  # {keyword: [emoji,]}
            "event": {},  # {event: [emoji,]}
        }
        self.config.register_guild(**default_guild)
        self._cog_ready: asyncio.Event = asyncio.Event()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed: str = super().format_help_for_context(ctx)
        n: str = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"**Author:** {humanize_list(self.__author__)}",
            f"**Version:** {str(self.__version__)}",
        ]
        return "\n".join(text)

    async def cog_load(self) -> None:
        await self.cache.initialize()
        self._cog_ready.set()

    async def wait_until_cog_ready(self) -> None:
        await self._cog_ready.wait()

    async def do_autoreact(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        for keyword, reactions in self.cache.autoreact[message.guild.id].items():
            if keyword in message.content:
                with contextlib.suppress(discord.HTTPException, TypeError):
                    asyncio.gather(*(message.add_reaction(reaction) for reaction in reactions))
                await asyncio.sleep(0.001)

    async def do_autoreact_event(self, message: discord.Message, type: str) -> None:
        if message.guild is None:
            return
        reactions: List[str] = self.cache.event[message.guild.id][type]
        asyncio.gather(*(message.add_reaction(reaction) for reaction in reactions))
