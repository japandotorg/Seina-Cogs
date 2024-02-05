"""
GNU General Public License Version 3.0

Copyright (c) 2018-2023 Sitryk
Copyright (c) 2023-present japandotorg
"""

from abc import ABC, ABCMeta, abstractmethod
from typing import Any

from redbot.core import Config, commands
from redbot.core.bot import Red


class MixinMeta(ABC):
    bot: Red
    config: Config

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.bot: Red
        self.config: Config

    @abstractmethod
    def format_help_for_context(self, ctx: commands.Context) -> str:
        raise NotImplementedError()


class CompositeMetaClass(commands.CogMeta, ABCMeta):
    pass
