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

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, Union

import discord
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core.config import Config

if TYPE_CHECKING:
    from .dataclass import Punishment
    from .manager import PunishmentManager


class Manager(ABC):
    @abstractmethod
    async def punish(
        self,
        user: Union[discord.User, discord.Member],
        guild: discord.Guild,
        punishment: Punishment,
    ) -> None:
        ...


class MixinMeta(ABC):
    bot: Red
    config: Config
    manager: PunishmentManager

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.bot: Red
        self.config: Config
        self.manager: PunishmentManager


class CompositeMetaClass(commands.CogMeta, ABCMeta):
    pass
