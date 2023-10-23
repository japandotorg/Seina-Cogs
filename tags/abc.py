"""
MIT License

Copyright (c) 2020-2023 PhenoM4n4n
Copyright (c) 2023-present japandotorg

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
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Coroutine, Dict, List, Optional, Union

import discord
from aiohttp import ClientSession
from redbot.core import Config, commands
from redbot.core.bot import Red

from .objects import Tag
from .utils import RequesterType


class MixinMeta(ABC):
    """
    Base class for well behaved type hint detection with composite class.
    Basically, to keep developers sane when not all attributes are defined in each mixin.

    Strategy borrowed from redbot.cogs.mutes.abc
    """

    config: Config
    bot: Red
    session: ClientSession

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.guild_tag_cache: defaultdict[int, Dict[str, Tag]]
        self.global_tag_cache: Dict[str, Tag]
        self.dot_parameter: Optional[bool]
        self.async_enabled: Optional[bool]
        self.docs: Union[List[str], Dict[str, str]]

    @abstractmethod
    async def cog_unload(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def create_task(self, coroutine: Coroutine, *, name: Optional[str] = None) -> asyncio.Task:
        raise NotImplementedError()

    @abstractmethod
    async def cache_guild(self, guild_id: int, guild_data: Dict[str, Dict[str, Any]]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def search_tag(self, tag_name: str, guild: Optional[discord.Guild] = None) -> List[Tag]:
        raise NotImplementedError()

    @abstractmethod
    def get_tag(
        self,
        guild: Optional[discord.Guild],
        tag_name: str,
        *,
        check_global: bool = True,
        global_priority: bool = False,
    ) -> Optional[Tag]:
        raise NotImplementedError()

    @abstractmethod
    def get_unique_tags(self, guild: Optional[discord.Guild] = None) -> List[Tag]:
        raise NotImplementedError()

    @abstractmethod
    async def validate_tagscript(self, ctx: commands.Context, tagscript: str) -> bool:
        raise NotImplementedError()


class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """
    This allows the metaclass used for proper type detection to
    coexist with discord.py's metaclass
    """
