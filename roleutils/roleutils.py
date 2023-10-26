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

# Multi-file class combining taken from https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/mod.py
import asyncio
import logging
from abc import ABC
from typing import Any, Coroutine, Dict, Final, List, Literal, Optional, Union

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import humanize_list

from .reactroles import ReactRoles
from .roles import Roles

log = logging.getLogger("red.phenom4n4n.roleutils")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class CompositeMetaClass(type(commands.Cog), type(ABC)):
    """
    This allows the metaclass used for proper type detection to
    coexist with discord.py's metaclass
    """


class RoleUtils(
    Roles,
    ReactRoles,
    commands.Cog,
    metaclass=CompositeMetaClass,
):
    """
    Useful role commands.

    Includes massroling, role targeting, and reaction roles.
    """

    __author__: Final[List[str]] = ["inthedark.org", "PhenoM4n4n"]
    __version__: Final[str] = "1.4.0"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        return (
            f"{pre_processed}{n}\n"
            f"Version: {self.__version__}\n"
            f"Author: {humanize_list(self.__author__)}"
        )

    def __init__(self, bot: Red, *_args: Any) -> None:
        self.cache: Dict[str, Any] = {}
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=326235423452394523,
            force_registration=True,
        )
        default_guild: Dict[str, Dict[str, Union[List[int], bool]]] = {
            "reactroles": {"channels": [], "enabled": True}
        }
        self.config.register_guild(**default_guild)

        default_guildmessage: Dict[str, Dict[str, Any]] = {"reactroles": {"react_to_roleid": {}}}
        self.config.init_custom("GuildMessage", 2)
        self.config.register_custom("GuildMessage", **default_guildmessage)
        super().__init__(*_args)
        self.initialize_task: asyncio.Task[Any] = self.create_task(self.initialize())

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        return

    async def initialize(self) -> None:
        log.debug("RoleUtils initialize")
        await super().initialize()

    @staticmethod
    def task_done_callback(task: asyncio.Task) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as error:
            log.exception("Task failed.", exc_info=error)

    def create_task(
        self, coroutine: Coroutine, *, name: Optional[str] = None
    ) -> asyncio.Task[Any]:
        task = asyncio.create_task(coroutine, name=name)
        task.add_done_callback(self.task_done_callback)
        return task
