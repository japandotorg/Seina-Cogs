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
import TagScriptEngine as tse
from aiohttp import ClientSession
from redbot.core import Config, commands
from redbot.core.bot import Red

from .objects import Tag


class MixinMeta(ABC):
    """
    Base class for well behaved type hint detection with composite class.
    Basically, to keep developers sane when not all attributes are defined in each mixin.

    Strategy borrowed from redbot.cogs.mutes.abc
    """

    config: Config
    bot: Red
    session: ClientSession
    engine: Union[tse.AsyncInterpreter, tse.Interpreter]

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.guild_tag_cache: defaultdict[int, Dict[str, Tag]]
        self.global_tag_cache: Dict[str, Tag]
        self.dot_parameter: Optional[bool]
        self.async_enabled: Optional[bool]

    @staticmethod
    @abstractmethod
    def get_seed_from_context(ctx: commands.Context) -> Dict[str, tse.Adapter]: ...

    @staticmethod
    @abstractmethod
    def generate_tag_list(tags: List[Tag]) -> Dict[str, List[str]]: ...

    @staticmethod
    @abstractmethod
    async def show_tag_list(ctx, data: Dict[str, List[str]], name: str, icon_url: str) -> None: ...

    @classmethod
    @abstractmethod
    def handle_overrides(
        cls, command: commands.Command, overrides: Dict[Any, Any]
    ) -> commands.Command: ...

    @abstractmethod
    def create_task(self, coroutine: Coroutine, *, name: Optional[str] = None) -> asyncio.Task: ...

    @staticmethod
    @abstractmethod
    async def send_quietly(
        destination: discord.abc.Messageable, content: Optional[str] = None, **kwargs: Any
    ) -> Optional[discord.Message]: ...

    @staticmethod
    @abstractmethod
    async def delete_quietly(ctx: commands.Context) -> None: ...

    @abstractmethod
    async def cog_unload(self) -> None: ...

    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def cache_guild(self, guild_id: int, guild_data: Dict[str, Dict[str, Any]]) -> None: ...

    @abstractmethod
    async def show_tag_usage(
        self, ctx: commands.Context, guild: Optional[discord.Guild] = None
    ) -> None: ...

    @abstractmethod
    def search_tag(self, tag_name: str, guild: Optional[discord.Guild] = None) -> List[Tag]: ...

    @abstractmethod
    def get_tag(
        self,
        guild: Optional[discord.Guild],
        tag_name: str,
        *,
        check_global: bool = True,
        global_priority: bool = False,
    ) -> Optional[Tag]: ...

    @abstractmethod
    async def process_tag(
        self,
        ctx: commands.Context,
        tag: Tag,
        *,
        seed_variables: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[str]: ...

    @abstractmethod
    async def create_tag(
        self, ctx: commands.Context, tag_name: str, tagscript: str, *, global_tag: bool = False
    ): ...

    @abstractmethod
    def get_unique_tags(self, guild: Optional[discord.Guild] = None) -> List[Tag]: ...

    @abstractmethod
    async def validate_tagscript(self, ctx: commands.Context, tagscript: str) -> bool: ...

    @abstractmethod
    async def validate_tag_count(self, guild: discord.Guild) -> None: ...

    @abstractmethod
    async def message_eligible_as_tag(self, message: discord.Message) -> bool: ...

    @abstractmethod
    async def invoke_tag_message(
        self, message: discord.Message, prefix: str, tag_command: str
    ) -> None: ...

    @abstractmethod
    async def send_tag_response(
        self,
        ctx: commands.Context,
        actions: Dict[str, Any],
        content: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[discord.Message]: ...

    @abstractmethod
    async def process_command(
        self,
        command_message: discord.Message,
        silent: bool,
        reply: bool,
        overrides: Dict[Any, Any],
    ) -> None: ...

    @abstractmethod
    async def process_commands(
        self, messages: List[discord.Message], silent: bool, reply: bool, overrides: Dict[Any, Any]
    ) -> None: ...

    @abstractmethod
    async def validate_checks(self, ctx: commands.Context, actions: Dict[str, Any]) -> None: ...

    @abstractmethod
    async def validate_requires(self, ctx: commands.Context, requires: Dict[str, Any]) -> None: ...

    @abstractmethod
    async def validate_blacklist(
        self, ctx: commands.Context, blacklist: Dict[str, Any]
    ) -> None: ...

    @abstractmethod
    async def role_or_channel_convert(
        self, ctx: commands.Context, argument: str
    ) -> Optional[Union[discord.Role, discord.TextChannel]]: ...

    @abstractmethod
    async def react_to_list(
        self, ctx: commands.Context, message: discord.Message, args: List[str]
    ) -> None: ...


class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """
    This allows the metaclass used for proper type detection to
    coexist with discord.py's metaclass
    """
