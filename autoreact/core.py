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

import asyncio
import contextlib
from typing import Dict, Final, List, Literal, Pattern

import discord
from redbot.core.bot import Red  # isort: skip
from redbot.core import Config, commands
from redbot.core.utils.chat_formatting import humanize_list

from .cache import Cache
from .events import EventMixin
from .commands import Commands
from .abc import CompositeMetaClass

try:
    import regex as re  # pyright: ignore[reportMissingModuleSource]
except (ImportError, ModuleNotFoundError):
    import re


class AutoReact(
    Commands,
    EventMixin,
    commands.Cog,
    metaclass=CompositeMetaClass,
):
    """Create automatic reactions for triggers and pre-defined events."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.cache: Cache = Cache(self)

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
        self._task: asyncio.Task[None] = discord.utils.MISSING

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed: str = super().format_help_for_context(ctx)  # pyright: ignore[reportAbstractUsage]
        n: str = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"**Author:** {humanize_list(self.__author__)}",
            f"**Version:** {str(self.__version__)}",
        ]
        return "\n".join(text)

    async def cog_load(self) -> None:
        if self._task is discord.utils.MISSING:
            self.task: asyncio.Task[None] = asyncio.create_task(
                self.initialize()
            )

    async def cog_unload(self) -> None:
        if self._task is not discord.utils.MISSING:
            if not self._task.cancelled():
                self._task.cancel()

    async def initialize(self) -> None:
        await self.cache.initialize()
        self._cog_ready.set()

    async def wait_until_cog_ready(self) -> None:
        _: Literal[True] = await self._cog_ready.wait()

    async def do_autoreact(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        for keyword, reactions in self.cache.autoreact[
            message.guild.id
        ].items():
            pattern: Pattern[str] = re.compile(keyword)
            if pattern.search(message.content):
                with contextlib.suppress(
                    discord.HTTPException, TypeError
                ):
                    _: asyncio.futures.Future[List[None]] = (
                        asyncio.gather(
                            *(
                                message.add_reaction(reaction)
                                for reaction in reactions
                            )
                        )
                    )
                await asyncio.sleep(0.001)  # TODO: remove this

    async def do_autoreact_event(
        self, message: discord.Message, type: str
    ) -> None:
        if message.guild is None:
            return
        reactions: List[str] = self.cache.event[message.guild.id][
            type
        ]
        _: asyncio.futures.Future[List[None]] = asyncio.gather(
            *(
                message.add_reaction(reaction)
                for reaction in reactions
            )
        )
