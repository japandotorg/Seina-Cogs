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

import contextlib
import logging
from typing import Any, Dict, Final, List, Optional, Tuple, Union, cast

import discord
import TagScriptEngine as tse
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, warning

from ._tagscript import (
    TAGSCRIPT_LIMIT,
    TagCharacterLimitReached,
    default_thread_name,
    process_tagscript,
    thread_message,
)
from .abc import CompositeMetaClass
from .commands import Commands
from .cooldown import ThreadCooldown
from .views import ThreadView

log: logging.Logger = logging.getLogger("red.seina.threadopener")


class ThreadOpener(
    commands.Cog,
    Commands,
    metaclass=CompositeMetaClass,
):
    """
    A cog to open continuous threads to messages in a channel.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_420_666,
            force_registration=True,
        )
        default_guilds: Dict[
            str,
            Union[
                str,
                bool,
                List[int],
                Optional[int],
                Dict[str, bool],
                Dict[str, List[str]],
            ],
        ] = {
            "channels": [],
            "blacklist": {
                "users": [],
                "roles": [],
            },
            "toggle": False,
            "allow_bots": False,
            "slowmode_delay": None,
            "message_toggle": False,
            "message": thread_message,
            "auto_archive_duration": 10080,
            "default_thread_name": default_thread_name,
            "buttons": {"toggle": True},
            "counter": 1,
        }
        self.config.register_guild(**default_guilds)

        cooldown: Tuple[float, float, commands.BucketType] = (3, 10, commands.BucketType.guild)

        self.spam_control: ThreadCooldown = ThreadCooldown.from_cooldown(*cooldown)

        self.view: ThreadView = ThreadView()

    @staticmethod
    def format_thread_name(member: discord.Member, *, formatting: str, counter: int) -> str:
        interpreter: tse.Interpreter = tse.Interpreter([tse.LooseVariableGetterBlock()])
        output: tse.Response = interpreter.process(
            formatting,
            {
                "counter": tse.IntAdapter(counter),
                "author": tse.MemberAdapter(member),
                "member": tse.MemberAdapter(member),
                "server": tse.GuildAdapter(member.guild),
                "guild": tse.GuildAdapter(member.guild),
                "created": tse.StringAdapter(
                    discord.utils.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            },
        )
        return str(output.body)

    @staticmethod
    def check_for_role_or_user_blacklist(
        member: discord.Member, *, roles: List[int], users: List[int]
    ) -> bool:
        if not roles and not users:
            return False
        _roles: List[int] = [role.id for role in list(member.roles)]
        return any(role in roles for role in _roles) or any(user == member.id for user in users)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed: str = super().format_help_for_context(ctx)
        n: str = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def cog_load(self) -> None:
        self.bot.add_view(self.view)

    async def red_delete_data_for_user(self, **kwargs: Any) -> None:
        """Nothing to delete."""
        return

    async def validate_tagscript(self, tagscript: str) -> bool:
        length: int = len(tagscript)
        if length > TAGSCRIPT_LIMIT:
            raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if not isinstance(message.author, discord.Member):
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        if not isinstance(message.channel, discord.TextChannel):
            return
        config: Dict[
            str,
            Union[str, bool, List[int], Optional[int], Dict[str, bool], Dict[str, List[str]]],
        ] = await self.config.guild(message.guild).all()
        blacklist: Dict[str, List[int]] = cast(Dict[str, List[int]], config["blacklist"])
        if self.check_for_role_or_user_blacklist(
            message.author, roles=blacklist["roles"], users=blacklist["users"]
        ):
            return
        if not config["allow_bots"] and (
            message.author.bot or message.is_system() or message.webhook_id
        ):
            return
        if not cast(bool, config["toggle"]):
            return
        if message.channel.id not in cast(List[int], config["channels"]):
            return
        if (
            not message.guild.me.guild_permissions.manage_threads
            or not message.guild.me.guild_permissions.view_channel
            or not message.guild.me.guild_permissions.create_public_threads
        ):
            await self.config.guild(message.guild).toggle.set(False)
            await message.channel.send(
                "ThreadOpener has been disabled due to missing permissions in "
                f"{message.channel.name} ({message.channel.id})"
            )
            log.info(
                f"ThreadOpener has been disabled due to missing permissions in {message.guild.name}.",
            )
            return
        bucket: Optional[commands.Cooldown] = self.spam_control.get_bucket(message)
        current: float = message.created_at.timestamp()
        retry_after: Optional[float] = bucket and bucket.update_rate_limit(current)
        if retry_after and not self.bot.is_owner(message.author):
            log.debug(f"{message.channel} ratelimit exhausted, retry after: {retry_after}.")
            return
        slowmode_delay: int = cast(int, config["slowmode_delay"])
        auto_archive_duration: int = cast(int, config["auto_archive_duration"])
        message_toggle: int = cast(bool, config["message_toggle"])
        thread_name: str = self.format_thread_name(
            message.author, formatting=config["default_thread_name"], counter=config["counter"]
        )
        try:
            thread: discord.Thread = await message.create_thread(
                name=thread_name[:100],
                auto_archive_duration=auto_archive_duration,
                slowmode_delay=slowmode_delay,
                reason="ThreadOpener initiate.",
            )
        except discord.Forbidden:
            await message.channel.send(
                warning(
                    "I do not have permissions to create threads in this channel, "
                    "auto removing from enabled thread opener channels."
                )
            )
            async with self.config.guild(message.guild).channels() as channels:
                channels.remove(message.channel.id)
            return
        except discord.HTTPException:
            log.exception(
                f"Something went wrong while creating threads in {message.channel.jump_url}.",
                exc_info=True,
            )
            return
        except ValueError:
            log.exception(
                f"Message: {message.jump_url} does not have a guild info attached to it.",
                exc_info=True,
            )
            return
        await self.config.guild(message.guild).counter.set(int(config["counter"]) + 1)
        if not message_toggle:
            return
        threadmessage: str = cast(str, config["message"])
        color: discord.Color = await self.bot.get_embed_color(message.channel)
        kwargs: Dict[str, Any] = process_tagscript(
            threadmessage,
            {
                "server": tse.GuildAdapter(message.guild),
                "author": tse.MemberAdapter(message.author),
                "member": tse.MemberAdapter(message.author),
                "color": tse.StringAdapter(str(color)),
            },
        )
        if not kwargs:
            await self.config.guild(message.guild).message.clear()
            kwargs: Dict[str, Any] = process_tagscript(
                thread_message,
                {
                    "server": tse.GuildAdapter(message.guild),
                    "author": tse.MemberAdapter(message.author),
                    "member": tse.MemberAdapter(message.author),
                    "color": tse.StringAdapter(str(color)),
                },
            )
        if cast(Dict[str, bool], config["buttons"])["toggle"]:
            kwargs["view"] = self.view
        msg: discord.Message = await thread.send(**kwargs)
        with contextlib.suppress(discord.HTTPException):
            await msg.pin(
                reason="[ThreadOpener] auto pinned the thread message in {}.".format(
                    thread.jump_url
                )
            )
