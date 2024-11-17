from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from redbot.core import Config, commands
from redbot.core.bot import Red

from .models import LotteryManager


class MixinMeta(ABC):
    bot: Red
    config: Config
    manager: LotteryManager

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.bot: Red
        self.config: Config
        self.manager: LotteryManager

    @abstractmethod
    def format_help_for_context(self, ctx: commands.Context) -> str: ...


class CompositeMetaClass(commands.CogMeta, ABCMeta):
    pass
