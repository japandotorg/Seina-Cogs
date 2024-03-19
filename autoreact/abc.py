from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red

from .cache import Cache

if TYPE_CHECKING:
    from .core import AutoReact


class CompositeMetaClass(commands.CogMeta, ABCMeta):
    pass


class MixinMeta(ABC, metaclass=CompositeMetaClass):
    bot: Red
    config: Config
    cache: Cache["AutoReact"]

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)

    @abstractmethod
    def format_help_for_context(self, ctx: commands.Context) -> str: ...

    @abstractmethod
    async def wait_until_cog_ready(self) -> None: ...

    @abstractmethod
    async def do_autoreact(self, message: discord.Message) -> None: ...

    @abstractmethod
    async def do_autoreact_event(self, message: discord.Message, type: str) -> None: ...
