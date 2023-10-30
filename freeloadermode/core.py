"""
MIT License

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
import logging
import contextlib
from datetime import datetime, timedelta, timezone
from typing import Coroutine, Final, List, Dict, Union, Any, Optional, Literal

import discord
from discord.ext import tasks
from redbot.core.bot import Red
from redbot.core import Config, commands, modlog
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import humanize_list

import TagScriptEngine as tse
from redbot.core.utils.mod import get_audit_reason

from .abc import CompositeMetaClass
from ._tagscript import (
    TAGSCRIPT_LIMIT,
    TagCharacterLimitReached,
    freeloader_message,
    process_tagscript,
)
from .commands import CommandsMixin

log: logging.Logger = logging.getLogger("red.seina.freeloadermode")


class FreeloaderMode(
    commands.Cog,
    CommandsMixin,
    metaclass=CompositeMetaClass,
):
    """
    An useful cog dedicated to banning those stupid freeloaders that leave your server right after an event or something.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    def __init__(self, bot: Red) -> None:
        super().__init__()

        self.bot: Red = bot

        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        default_guild: Dict[str, Any] = {
            "toggled": False,
            "untoggletime": None,
            "ignored": [],
            "tempban_duration": None,
            "action": "ban",
            "log_channel": None,
            "current_tempbans": [],
            "message": freeloader_message,
        }
        default_member: Dict[str, Union[bool, float]] = {
            "banned_until": False,
        }
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)

        self._tempban_expirations_task.start()
        self.task: asyncio.Task[Any] = self._create_task(self._initialize())

        if 759180080328081450 in self.bot.owner_ids:  # type: ignore
            with contextlib.suppress(RuntimeError, ValueError):
                self.bot.add_dev_env_value(self.__class__.__name__.lower(), lambda x: self)

    @staticmethod
    def _task_done_callback(task: asyncio.Task[Any]) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as error:
            log.exception("Task failed.", exc_info=error)

    @staticmethod
    async def _register_casetype() -> None:
        ban_case: Dict[str, Union[str, bool]] = {
            "name": "freeloaderban",
            "default_setting": True,
            "image": "✖️",
            "case_str": "Freeloader Ban",
        }
        tempban_case: Dict[str, Union[str, bool]] = {
            "name": "freeloadertempban",
            "default_setting": True,
            "image": "✖️",
            "case_str": "Freeloader TempBan",
        }
        unban_case: Dict[str, Union[str, bool]] = {
            "name": "freeloaderunban",
            "default_setting": True,
            "image": "✔️",
            "case_str": "Freeloader Unban",
        }

        try:
            await modlog.register_casetype(**ban_case)  # type: ignore
            await modlog.register_casetype(**tempban_case)  # type: ignore
            await modlog.register_casetype(**unban_case)  # type: ignore
        except RuntimeError:
            pass

    def _create_task(
        self, coroutine: Coroutine, *, name: Optional[str] = None
    ) -> asyncio.Task[Any]:
        task: asyncio.Task[Any] = asyncio.create_task(coroutine, name=name)
        task.add_done_callback(self._task_done_callback)
        return task

    async def cog_unload(self) -> None:
        if 759180080328081450 in self.bot.owner_ids:  # type: ignore
            with contextlib.suppress(KeyError):
                self.bot.remove_dev_env_value(self.__class__.__name__.lower())

        self.task.cancel()
        self._tempban_expirations_task.cancel()

    async def _initialize(self) -> None:
        await self.bot.wait_until_red_ready()
        await self._register_casetype()

    async def _validate_tagscript(self, tagscript: str) -> bool:
        length = len(tagscript)
        if length > TAGSCRIPT_LIMIT:
            raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
        return True

    async def _create_case(
        self,
        guild: discord.Guild,
        type: str,
        reason: str,
        user: Union[discord.User, discord.Member],
        until: Optional[datetime] = None,
        moderator: Optional[Union[discord.Member, discord.ClientUser]] = None,
    ) -> Optional[modlog.Case]:
        try:
            case: Optional[modlog.Case] = await modlog.create_case(
                self.bot,
                guild,
                discord.utils.utcnow(),
                type,
                user,
                moderator=moderator if moderator is not None else user,
                reason=reason,
                until=until,
            )
        except RuntimeError:
            case: Optional[modlog.Case] = None

        return case

    async def _notify_banned_user(self, member: discord.Member) -> None:
        time: int = await self.config.guild(member.guild).tempban_duration()
        action: str = await self.config.guild(member.guild).action()
        message: str = await self.config.guild(member.guild).message()

        kwargs: Dict[str, Union[str, discord.Embed]] = process_tagscript(
            message,
            {
                "server": tse.GuildAdapter(member.guild),
                "member": tse.MemberAdapter(member),
                "action": tse.StringAdapter(str(action)),
                "time": tse.IntAdapter(int(time))
                if str(action) == "tempban"
                else tse.StringAdapter("infinite"),
            },
        )

        if not kwargs:
            await self.config.guild(member.guild).message.clear()
            kwargs: Dict[str, Union[str, discord.Embed]] = process_tagscript(
                freeloader_message,
                {
                    "server": tse.GuildAdapter(member.guild),
                    "member": tse.MemberAdapter(member),
                    "action": tse.StringAdapter(str(action)),
                    "time": tse.IntAdapter(int(time))
                    if str(action) == "tempban"
                    else tse.StringAdapter("infinite"),
                },
            )

        try:
            await member.send(**kwargs)  # type: ignore
        except (discord.Forbidden, discord.HTTPException):
            log.debug(
                f"Unable to send dm to {member} ({member.id}).",
            )

    async def _check_guild_tempban_expirations(
        self, guild: discord.Guild, guild_tempbans: List[int]
    ) -> bool:
        changed: bool = False
        for uid in guild_tempbans.copy():
            unban_time: datetime = datetime.fromtimestamp(
                await self.config.member_from_ids(guild.id, uid).banned_until(),
                timezone.utc,
            )
            if datetime.now(timezone.utc) > unban_time:
                try:
                    await guild.unban(
                        discord.Object(id=uid), reason="Freeloader tempban finished."
                    )
                    await self._create_case(
                        guild,
                        type="freeloaderunban",
                        reason="Freeloader tempban finished.",
                        user=await self.bot.get_or_fetch_user(uid),
                        moderator=self.bot.user,
                    )
                except discord.NotFound:
                    guild_tempbans.remove(uid)
                    changed: bool = True
                except discord.HTTPException as error:
                    if error.code == 50013 or error.status == 403:
                        log.info(
                            "Failed to unban ({uid}) user from "
                            f"{guild.name} ({guild.id}) guild due to permissions."
                        )
                        break
                    log.info(f"Failed to unban member error code: {error.code}.")
                else:
                    guild_tempbans.remove(uid)
                    changed: bool = True
        return changed

    async def _check_tempban_expirations(self) -> None:
        guilds_data: Dict[int, Dict[str, Any]] = await self.config.all_guild()
        async for guild_id, guild_data in AsyncIter(guilds_data.items(), steps=100):
            if not (guild := self.bot.get_guild(guild_id)):
                continue
            if guild.unavailable or not guild.me.guild_permissions.ban_members:
                continue
            if await self.bot.cog_disabled_in_guild(self, guild):
                continue
            guild_tempbans: List[int] = guild_data["current_tempbans"]
            if not guild_tempbans:
                continue
            async with self.config.guild(guild).current_tempbans.get_lock():
                if await self._check_guild_tempban_expirations(guild, guild_tempbans):
                    await self.config.guild(guild).current_tempbans.set(guild_tempbans)

    async def _tempban(
        self,
        guild: discord.Guild,
        author: discord.Member,
        member: Union[discord.User, discord.Member, discord.Object],
        duration: int = 1,
        *,
        reason: Optional[str] = None,
    ) -> None:
        unban_time: datetime = datetime.now(timezone.utc) + timedelta(days=duration)

        await self.config.member(member).banned_until.set(unban_time.timestamp())  # type: ignore
        async with self.config.guild(guild).current_tempbans() as current_tempbans:
            current_tempbans.append(member.id)

        audit_reason: str = get_audit_reason(author, reason, shorten=True)  # type: ignore

        try:
            await guild.ban(member, reason=audit_reason)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return
        else:
            await self._notify_banned_user(member)  # type: ignore

        await self._create_case(
            guild,
            type="freeloadertempban",
            reason="Member left while freeloader mode was toggled!",
            user=member,  # type: ignore
            until=unban_time,
            moderator=self.bot.user,
        )

    @tasks.loop(minutes=69, reconnect=True)
    async def _tempban_expirations_task(self) -> None:
        try:
            await self._check_tempban_expirations()
        except Exception:
            log.exception(
                "Something went wrong in `_check_tempban_expirations`.",
                exc_info=True,
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        if member.bot:
            return

        guild: discord.Guild = member.guild

        if await self.bot.cog_disabled_in_guild(self, guild):
            return

        if not (await self.config.guild(guild).toggled()):
            return

        time: int = await self.config.guild(guild).untoggletime()

        if time is None:
            pass
        else:
            if time - datetime.utcnow().timestamp() <= 0:
                await self.config.guild(guild).toggled.clear()
                await self.config.guild(guild).untoggletime.clear()
                return

        if member.id in (await self.config.guild(guild).ignored()):
            return

        try:
            await guild.fetch_ban(member)
            return
        except discord.NotFound:
            pass
        except discord.Forbidden:
            await self.config.guild(guild).toggled.clear()
            log.exception(
                f"I'm unable to ban users in {guild.name}, disabled freeloadermode.",
                exc_info=True,
            )
            return

        action: Literal["ban", "tempban"] = await self.config.guild(guild).action()

        if action.lower() == "ban":
            try:
                await guild.ban(member, reason="Member left while freeloader mode was toggled.")
            except discord.NotFound:
                return
            else:
                await self._notify_banned_user(member)

            await self._create_case(
                guild,
                type="freeloaderban",
                reason="Member left while freeloader mode was toggled!",
                user=member,
                moderator=self.bot.user,
            )
        else:
            tempban_time: int = await self.config.guild(guild).tempban_duration()

            await self._tempban(
                guild=guild,
                author=guild.me,
                member=member,
                duration=tempban_time,
                reason="Member left while freeloader mode was toggled!",
            )

        log_channel: Optional[discord.TextChannel] = guild.get_channel(
            await self.config.guild(guild).log_channel()  # type: ignore
        )

        if not log_channel:
            return

        embed: discord.Embed = discord.Embed(
            title="**Freeloader Detected**",
            description=(
                "I detected a freeloader who left the server after freeloader mode was turned on.\n"
                + (
                    "I have banned them from the server"
                    + (
                        f" for {tempban_time} days"  # type: ignore
                        if action.lower() == "tempban"
                        else ""
                    )
                    + "."
                )
                + "\n\n"
                f"Username: {member.name}\n"
                f"ID: {member.id}\n"
                f"Joined: <t:{int(member.joined_at.timestamp())}:R>\n"  # type: ignore
                f"Left: <t:{int(datetime.now().timestamp())}:R>"
            ),
            color=await self.bot.get_embed_color(log_channel),
        )

        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass
