from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from redbot.core import Config, commands
from redbot.core.bot import Red


class CompositeMetaClass(commands.CogMeta, ABCMeta):
    pass


class MixinMeta(ABC, metaclass=CompositeMetaClass):
    bot: Red
    config: Config

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)

    @staticmethod
    @abstractmethod
    async def validate_tagscript(tagscript: str) -> bool: ...

    @abstractmethod
    def format_help_for_context(self, ctx: commands.Context) -> str: ...
