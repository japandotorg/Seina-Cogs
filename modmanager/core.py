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

import asyncio
import logging
from typing import Dict, Final, List, Union

import discord
import discord.ext.tasks
from redbot.core import commands, modlog
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils import AsyncIter

from .abc import CompositeMetaClass
from .commands import Commands
from .manager import PunishmentManager

log: logging.Logger = logging.getLogger("red.seina.modmanager")


class ModManager(
    Commands,
    commands.Cog,
    metaclass=CompositeMetaClass,
):
    """
    Force ban/kick users so that they stay in the ban/kick list
    even if someone tries to manually unban them.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_420_666,
            force_registration=True,
        )
        default_guild: Dict[str, Union[bool, Dict[str, str]]] = {
            "modlog": True,
            "toggle": False,
            "bans": {},
            "kicks": {},
        }
        self.config.register_guild(**default_guild)

        self.manager: PunishmentManager["ModManager"] = PunishmentManager(self)

        self._check_list_and_punish.start()

        self._task: asyncio.Task[None] = asyncio.create_task(self._register_casetypes())

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    async def cog_unload(self) -> None:
        self._check_list_and_punish.cancel()
        self._task.cancel()

    @staticmethod
    async def _register_casetypes() -> None:
        forceban: Dict[str, Union[str, bool]] = {
            "name": "forceban",
            "default_setting": True,
            "image": "\N{HAMMER}",
            "case_str": "Force Ban",
        }
        forcekick: Dict[str, Union[str, bool]] = {
            "name": "forcekick",
            "default_setting": True,
            "image": "\N{WOMANS BOOTS}",
            "case_str": "Force Ban",
        }
        try:
            await modlog.register_casetype(**forceban)  # type: ignore
            await modlog.register_casetype(**forcekick)  # type: ignore
        except RuntimeError:
            pass

    @discord.ext.tasks.loop(seconds=60, reconnect=True)
    async def _check_list_and_punish(self) -> None:
        all_guilds: Dict[int, Dict[str, Union[bool, Dict[str, str]]]] = (
            await self.config.all_guilds()
        )
        async for guild_id, guild_data in AsyncIter(all_guilds.items(), steps=100):
            if not (guild := self.bot.get_guild(guild_id)):
                continue
            if (
                guild.unavailable
                or not guild.me.guild_permissions.ban_members
                or not guild.me.guild_permissions.kick_members
            ):
                continue
            if await self.bot.cog_disabled_in_guild(self, guild):
                continue
            toggle = guild_data["toggle"]
            if not toggle:
                continue
            await asyncio.gather(
                self.manager._check_ban_list_and_ban_users(guild),
                self.manager._check_kick_list_and_kick_users(guild),
            )

    @_check_list_and_punish.before_loop
    async def _check_list_and_punish_before_loop(self) -> None:
        await self.bot.wait_until_red_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if await self.bot.cog_disabled_in_guild(self, member.guild):
            return
        config = await self.config.guild(member.guild).all()
        if not config["toggle"]:
            return
        await self.manager._check_kick_list_and_kick_users(member.guild)
