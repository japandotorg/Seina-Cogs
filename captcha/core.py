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
import os
import random
import string
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Final, List, Optional, Union

import discord
import TagScriptEngine as tse
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.data_manager import bundled_data_path

from ._tagscript import TAGSCRIPT_LIMIT as TAGSCRIPT_LIMIT
from ._tagscript import TagCharacterLimitReached as TagCharacterLimitReached
from ._tagscript import message_after_captcha as message_after_captcha_string
from ._tagscript import message_before_captcha as message_before_captcha_string
from ._tagscript import process_tagscript as process_tagscript
from .abc import CompositeMetaClass
from .commands import CaptchaCommands
from .objects import CaptchaObj

DELETE_AFTER: Final[int] = 10

log: logging.Logger = logging.getLogger("red.seina.captcha")


def captcha_object() -> ModuleType:
    from captcha import objects

    return objects


class Captcha(
    commands.Cog,
    CaptchaCommands,
    metaclass=CompositeMetaClass,
):
    """Captcha cog."""

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
        default_guild: Dict[str, Union[Optional[int], bool, str]] = {
            "toggle": False,
            "channel": None,
            "timeout": 120,
            "tries": 3,
            "role_after_captcha": None,
            "message_before_captcha": message_before_captcha_string,
            "message_after_captcha": message_after_captcha_string,
        }
        self.config.register_guild(**default_guild)

        self._captchas: Dict[int, discord.Message] = {}
        self._verification_phase: Dict[int, int] = {}
        self._user_tries: Dict[int, List[discord.Message]] = {}

        self._config: Dict[int, Dict[str, Any]] = {}

        self.data_path: Path = bundled_data_path(self)
        self.font_data: str = os.path.join(self.data_path, "DroidSansMono.ttf")

        self.task: asyncio.Task = asyncio.create_task(self._initialize())

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    async def _initialize(self) -> None:
        await self.bot.wait_until_red_ready()
        await self._build_cache()

    async def _build_cache(self) -> None:
        self._config: Dict[int, Dict[str, Any]] = await self.config.all_guilds()

    async def cog_unload(self) -> None:
        self.task.cancel()
        await super().cog_unload()

    async def validate_tagscript(self, tagscript: str) -> bool:
        length = len(tagscript)
        if length > TAGSCRIPT_LIMIT:
            raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
        return True

    async def _get_or_fetch_guild(self, guild_id: int) -> Optional[discord.Guild]:
        guild: Optional[discord.Guild] = self.bot.get_guild(guild_id)
        if guild is not None:
            return guild
        if not self.bot.is_ws_ratelimited():
            try:
                guild: Optional[discord.Guild] = await self.bot.fetch_guild(guild_id)
            except discord.HTTPException:
                pass
            else:
                return guild

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        if member.bot:
            return
        if await self.bot.cog_disabled_in_guild(self, member.guild):
            return
        if not await self.config.guild(member.guild).toggle():
            return
        if (
            not member.guild.me.guild_permissions.kick_members
            or not member.guild.me.guild_permissions.manage_roles
            or not member.guild.me.guild_permissions.embed_links
            or not member.guild.me.guild_permissions.attach_files
        ):
            await self.config.guild(member.guild).toggle.set(False)
            log.info(f"Disabled captcha verification due to missing permissions.")
            return

        if not await self.bot.allowed_by_whitelist_blacklist(member):
            await member.kick(
                reason=f"{member.id} failed to complete captcha verification because of being blacklisted by the bot."
            )
            return

        verif_channel: int = await self.config.guild(member.guild).channel()
        if not verif_channel:
            return
        channel: discord.TextChannel = member.guild.get_channel(int(verif_channel))  # type: ignore

        self._verification_phase[member.id] = 0
        self._user_tries[member.id] = []

        message_string: str = "".join(random.choice(string.ascii_uppercase) for _ in range(6))

        captcha: CaptchaObj = CaptchaObj(self, width=300, height=100)
        captcha.generate(message_string)
        captcha.write(message_string, f"{str(self.data_path)}/{member.id}.png")

        captcha_file: discord.File = discord.File(f"{str(self.data_path)}/{member.id}.png")

        message_before_captcha: str = await self.config.guild(
            member.guild
        ).message_before_captcha()

        color: discord.Color = await self.bot.get_embed_color(channel)

        kwargs: Dict[str, Any] = process_tagscript(
            message_before_captcha,
            {
                "member": tse.MemberAdapter(member),
                "guild": tse.GuildAdapter(member.guild),
                "color": tse.StringAdapter(str(color)),
            },
        )
        if not kwargs:
            await self.config.guild(member.guild).message_before_captcha.clear()
            kwargs: Dict[str, Any] = process_tagscript(
                message_before_captcha_string,
                {
                    "member": tse.MemberAdapter(member),
                    "guild": tse.GuildAdapter(member.guild),
                    "color": tse.StringAdapter(str(color)),
                },
            )
        kwargs["file"] = captcha_file
        temp_captcha: discord.Message = await channel.send(**kwargs)

        self._captchas[member.id] = temp_captcha
        self._user_tries[member.id].append(temp_captcha)

        timeout: int = await self.config.guild(member.guild).timeout()

        try:

            def check(message: discord.Message) -> bool:
                return (
                    message.content.upper() == message_string
                    and message.author.id == member.id
                    and message.channel.id == channel.id
                )

            await self.bot.wait_for(
                "message",
                check=check,
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            await member.kick(
                reason=f"{member.id} failed to solve captcha verification in time.",
            )
            del self._captchas[member.id]
            del self._verification_phase[member.id]
            del self._user_tries[member.id]
        else:
            del self._verification_phase[member.id]

            message_after_captcha: str = await self.config.guild(
                member.guild
            ).message_after_captcha()

            color: discord.Color = await self.bot.get_embed_color(channel)

            kwargs: Dict[str, Any] = process_tagscript(
                message_after_captcha,
                {
                    "member": tse.MemberAdapter(member),
                    "guild": tse.GuildAdapter(member.guild),
                    "color": tse.StringAdapter(str(color)),
                },
            )
            if not kwargs:
                await self.config.guild(member.guild).message_after_captcha.clear()
                kwargs: Dict[str, Any] = process_tagscript(
                    message_after_captcha_string,
                    {
                        "member": tse.MemberAdapter(member),
                        "guild": tse.GuildAdapter(member.guild),
                        "color": tse.StringAdapter(str(color)),
                    },
                )
            temp_success_message: discord.Message = await channel.send(**kwargs)

            self._user_tries[member.id].append(temp_success_message)

            os.remove(f"{str(self.data_path)}/{member.id}.png")

            role_id: int = await self.config.guild(member.guild).role_after_captcha()
            role: Optional[discord.Role] = discord.utils.get(member.guild.roles, id=role_id)

            try:
                await member.add_roles(role, reason=f"Captcha solved by {member.display_name}!")  # type: ignore
            except (discord.Forbidden, discord.HTTPException):
                log.exception(f"Failed to add roles to {member.id}.", exc_info=True)

        await asyncio.sleep(DELETE_AFTER)

        for user_try in self._user_tries[member.id]:
            await user_try.delete()

        await self._captchas[member.id].delete()
        del self._captchas[member.id]
        del self._user_tries[member.id]

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: discord.RawMemberRemoveEvent) -> None:
        member: Union[discord.Member, discord.User] = payload.user
        guild: Optional[discord.Guild] = await self._get_or_fetch_guild(payload.guild_id)
        if guild is None:
            return
        if await self.bot.cog_disabled_in_guild_raw(self.__class__.__name__, payload.guild_id):
            return
        if not await self.config.guild(guild).toggle():
            return

        if (
            not guild.me.guild_permissions.kick_members
            or not guild.me.guild_permissions.manage_roles
            or not guild.me.guild_permissions.embed_links
            or not guild.me.guild_permissions.attach_files
        ):
            await self.config.guild(guild).toggle.set(False)
            log.info(f"Disabled captcha verification due to missing permissions.")
            return

        if member.id in self._verification_phase:
            for user_try in self._user_tries[member.id]:
                await user_try.delete()
            await self._captchas[member.id].delete()
            del self._captchas[member.id]
            try:
                del self._verification_phase[member.id]
            except KeyError:
                pass
            os.remove(f"{str(self.data_path)}/{member.id}.png")
            del self._user_tries[member.id]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if message.is_system():
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        if not await self.config.guild(message.guild).toggle():
            return

        if (
            not message.guild.me.guild_permissions.kick_members
            or not message.guild.me.guild_permissions.manage_roles
            or not message.guild.me.guild_permissions.embed_links
            or not message.guild.me.guild_permissions.attach_files
        ):
            await self.config.guild(message.guild).toggle.set(False)
            log.info(f"Disabled captcha verification due to missing permissions.")
            return

        member: discord.Member = message.author  # type: ignore

        if not await self.bot.allowed_by_whitelist_blacklist(member):
            return

        verification_channel: int = await self.config.guild(message.guild).channel()
        if not verification_channel:
            return

        # fmt: off
        if (
            member.id in self._verification_phase 
            and message.channel.id == verification_channel
        ):
            self._verification_phase[member.id] += 1
            self._user_tries[member.id].append(message)

            tries: int = await self.config.guild(message.guild).tries()

            if self._verification_phase[member.id] >= tries:
                await member.kick(
                    reason=f"{member.id} failed to complete the captcha verification!"
                )

                for user_try in self._user_tries[member.id]:
                    await user_try.delete()

                await self._captchas[member.id].delete()
                del self._captchas[member.id]

                try:
                    del self._verification_phase[member.id]
                except KeyError:
                    pass

                os.remove(f"{str(self.data_path)}/{member.id}.png")
                del self._user_tries[member.id]
        # fmt: on
