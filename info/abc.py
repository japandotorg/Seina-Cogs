from abc import ABC, ABCMeta, abstractmethod
from pathlib import Path
from typing import Any

from redbot.core import Config, commands
from redbot.core.bot import Red

from .cache import Cache


class CompositeMetaClass(commands.CogMeta, ABCMeta):
    pass


class MixinMeta(ABC):
    bot: Red
    config: Config
    data_path: Path

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.bot: Red
        self.config: Config
        self.cache: Cache

    @abstractmethod
    def format_help_for_context(self, ctx: commands.Context) -> str:
        raise NotImplementedError()
