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

import logging
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    Union,
)

import discord
from redbot.core import modlog
from redbot.core.bot import Red
from typing_extensions import Self

from .abc import Manager
from .dataclass import Punishment

if TYPE_CHECKING:
    from .core import ModManager

ManagerT = TypeVar("ManagerT", bound="ModManager")

log: logging.Logger = logging.getLogger("red.seina.modmanager.manager")


class PunishmentManagerProtocol(Protocol):
    bot: Red

    def __init__(self, cog: ModManager) -> None:
        ...


class PunishmentManager(
    Manager,
    PunishmentManagerProtocol,
    Generic[ManagerT],
):
    __slots__: Tuple[str, ...] = ("cog",)

    def __init__(self, cog: ModManager) -> None:
        self.cog: ModManager = cog
        self.bot: Red = cog.bot

    @staticmethod
    async def _get_ban(
        member: Union[discord.Member, discord.User],
        guild: discord.Guild,
        limit: int = 1000,
    ) -> Optional[discord.User]:
        banned: List[discord.BanEntry] = [entry async for entry in guild.bans(limit=limit)]
        for ban in banned:
            if ban.user.id == member.id:
                return ban.user
            else:
                return None

    def _get_manager(self) -> Self:
        return self

    async def _ban(
        self,
        guild: discord.Guild,
        member: Union[discord.User, discord.Member, int],
        reason: str = "No reason provided.",
    ) -> None:
        if member in (guild.me.id, guild.me, guild.owner_id, guild.owner):
            log.debug("Cannot ban myself or the guild owner.")
            return
        if (
            isinstance(member, discord.Member)
            and guild.me.top_role.position < member.top_role.position
        ):
            log.debug("Cannot ban someone with higher hierarchy than me.")
            return
        try:
            await guild.ban(
                discord.Object(member if isinstance(member, int) else member.id), reason=reason
            )
            if await self.cog.config.guild(guild).modlog():
                await modlog.create_case(
                    self.bot,
                    guild,
                    discord.utils.utcnow(),
                    "forceban",
                    member,
                    moderator=guild.me,
                    reason=reason,
                )
        except Exception as error:
            log.exception("Failed to ban **{}**.".format(member), exc_info=error)
            raise error

    async def _kick(
        self,
        member: discord.Member,
        reason: str = "No reason provided.",
    ) -> None:
        if member.guild.me.top_role.position < member.top_role.position:
            log.debug("Can't kick someone with higher hierarchy than me.")
            return
        if member in (member.guild.me, member.guild.owner):
            log.debug("Can't kick myself or the guild owner.")
            return
        try:
            await member.kick(reason=reason)
            if await self.cog.config.guild(member.guild).modlog():
                await modlog.create_case(
                    self.bot,
                    member.guild,
                    discord.utils.utcnow(),
                    "forcekick",
                    member,
                    moderator=member.guild.me,
                    reason=reason,
                )
        except Exception as error:
            log.exception("Failed to kick **{}**.".format(member), exc_info=error)
            raise error

    async def _in_ban_list(self, id: int, guild: discord.Guild) -> bool:
        data: Dict[str, str] = await self.cog.config.guild(guild).bans()
        return str(id) in data.keys()

    async def _in_kick_list(self, id: int, guild: discord.Guild) -> bool:
        data: Dict[str, str] = await self.cog.config.guild(guild).kicks()
        return str(id) in data.keys()

    async def _get_ban_list(self, guild: discord.Guild) -> Dict[str, str]:
        ret: Dict[str, str] = await self.cog.config.guild(guild).bans()
        if not ret:
            return {}
        return ret

    async def _get_kick_list(self, guild: discord.Guild) -> Dict[str, str]:
        ret: Dict[str, str] = await self.cog.config.guild(guild).kicks()
        if not ret:
            return {}
        return ret

    async def _add_to_ban_list(
        self,
        users: Iterable[Union[discord.Member, discord.User]],
        guild: discord.Guild,
        reason: str = "No reason provided.",
    ) -> None:
        async with self.cog.config.guild(guild).bans() as b:
            for item in users:
                item = str(getattr(item, "id", item))
                b[item] = reason

    async def _remove_from_ban_list(
        self,
        users: Iterable[Union[discord.Member, discord.User]],
        guild: discord.Guild,
    ) -> None:
        async with self.cog.config.guild(guild).bans() as b:
            for item in users:
                item = str(getattr(item, "id", item))
                b.pop(item, None)

    async def _edit_ban_reason(
        self,
        user: Union[discord.User, discord.Member, int],
        reason: str,
        *,
        guild: discord.Guild,
    ) -> None:
        data = self.cog.config.guild(guild).bans()
        user_id = getattr(user, "id", user)
        async with data as b:
            b[str(user_id)] = reason

    async def _clear_ban_list(self, guild: discord.Guild) -> None:
        await self.cog.config.guild(guild).bans.clear()

    async def _check_ban_list_and_ban_users(self, guild: discord.Guild) -> None:
        data: Dict[str, str] = await self.cog.config.guild(guild).bans()
        for member_id, reason in data.items():
            try:
                user: discord.User = await self.bot.get_or_fetch_user(int(member_id))
            except discord.HTTPException as error:
                log.exception(
                    "Failed to get/fetch user_id {}".format(member_id),
                    exc_info=error,
                )
                continue
            punishment: Punishment = Punishment(
                punishment_manager=self,
                punsihment_type="ban",
                punishment_reason=reason,
            )
            ban: Optional[discord.User] = await self._get_ban(user, guild)
            if not ban:
                await self.punish(user, guild, punishment)

    async def _add_to_kick_list(
        self,
        users: Iterable[Union[discord.Member, discord.User]],
        guild: discord.Guild,
        reason: str = "No reason provided.",
    ) -> None:
        async with self.cog.config.guild(guild).kicks() as k:
            for item in users:
                item = str(getattr(item, "id", item))
                k[item] = reason

    async def _remove_from_kick_list(
        self,
        users: Iterable[Union[discord.Member, discord.User]],
        guild: discord.Guild,
    ) -> None:
        async with self.cog.config.guild(guild).kicks() as k:
            for item in users:
                item = str(getattr(item, "id", item))
                k.pop(item, None)

    async def _clear_kick_list(self, guild: discord.Guild) -> None:
        await self.cog.config.guild(guild).kicks.clear()

    async def _edit_kick_reason(
        self,
        user: Union[discord.User, discord.Member, int],
        reason: str,
        *,
        guild: discord.Guild,
    ) -> None:
        data = self.cog.config.guild(guild).bans()
        user_id = getattr(user, "id", user)
        async with data as k:
            k[str(user_id)] = reason

    async def _check_kick_list_and_kick_users(self, guild: discord.Guild) -> None:
        data: Dict[str, str] = await self.cog.config.guild(guild).kicks()
        for member_id, reason in data.items():
            try:
                member: discord.Member = await self.bot.get_or_fetch_member(guild, int(member_id))
            except discord.NotFound:
                continue
            except discord.HTTPException as error:
                log.exception(
                    "Failed to get/fetch member_id {}".format(member_id),
                    exc_info=error,
                )
                continue
            punishment: Punishment = Punishment(
                punishment_manager=self,
                punsihment_type="kick",
                punishment_reason=reason,
            )
            await self.punish(member, guild, punishment)

    async def _punish(
        self,
        user: Union[discord.User, discord.Member],
        guild: discord.Guild,
        punishment: Punishment,
    ) -> None:
        if punishment.punsihment_type == "ban":
            try:
                await self._ban(guild, user, punishment.punishment_reason)
            except discord.Forbidden as error:
                raise error
            else:
                self.bot.dispatch("punishment", user, guild, punishment)
        elif punishment.punsihment_type == "kick":
            if not isinstance(user, discord.Member):
                return
            try:
                await self._kick(user, punishment.punishment_reason)
            except discord.Forbidden as error:
                raise error
            else:
                self.bot.dispatch("punishment", user, guild, punishment)
        else:
            return

    async def punish(
        self,
        user: Union[discord.User, discord.Member],
        guild: discord.Guild,
        punishment: Punishment,
    ) -> None:
        try:
            await self._punish(user, guild, punishment)
        except discord.Forbidden as error:
            log.exception(
                "Failed to punish member **{} ({})**".format(user, user.id), exc_info=error
            )
