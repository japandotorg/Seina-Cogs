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

import logging
from typing import Any, Dict, Final, List, Optional, Tuple, Union

import discord
import TagScriptEngine as tse
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, warning

from ._tagscript import (
    TAGSCRIPT_LIMIT,
    TagCharacterLimitReached,
    process_tagscript,
    thread_message,
)
from .abc import CompositeMetaClass
from .commands import Commands
from .cooldown import ThreadCooldown

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
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_420_666,
            force_registration=True,
        )
        default_guilds: Dict[str, Optional[Union[List[int], Any]]] = {
            "channels": [],
            "toggle": False,
            "slowmode_delay": None,
            "message_toggle": False,
            "message": thread_message,
            "auto_archive_duration": 10080,
        }
        self.config.register_guild(**default_guilds)

        cooldown: Tuple[float, float, commands.BucketType] = (3, 10, commands.BucketType.guild)

        self.spam_control: ThreadCooldown = ThreadCooldown.from_cooldown(*cooldown)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def red_delete_data_for_user(self, **kwargs: Any) -> None:
        """Nothing to delete."""
        return

    async def validate_tagscript(self, tagscript: str) -> bool:
        length = len(tagscript)
        if length > TAGSCRIPT_LIMIT:
            raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        if message.is_system():
            return
        if message.author.bot:
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        if not isinstance(message.channel, discord.TextChannel):
            return
        if not await self.config.guild(message.guild).toggle():
            return
        if not message.channel.id in (await self.config.guild(message.guild).channels()):
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

        bucket = self.spam_control.get_bucket(message)
        current = message.created_at.timestamp()
        retry_after = bucket and bucket.update_rate_limit(current)
        if retry_after and message.author.id not in self.bot.owner_ids:  # type: ignore
            log.debug(f"{message.channel} ratelimit exhausted, retry after: {retry_after}.")
            return

        slowmode_delay: int = await self.config.guild(message.guild).slowmode_delay()
        auto_archive_duration: Any = await self.config.guild(message.guild).auto_archive_duration()
        message_toggle: bool = await self.config.guild(message.guild).message_toggle()

        try:
            thread = await message.create_thread(
                name=f"{message.author.global_name}",
                auto_archive_duration=auto_archive_duration,
                slowmode_delay=slowmode_delay,
                reason="ThreadOpener initiate.",
            )
        except discord.Forbidden:
            await message.channel.send(
                warning("I do not have permissions to create threads in this channel.")
            )
        except discord.HTTPException:
            await message.channel.send(
                warning("Something went wrong while creating threads in this channel.")
            )
            log.exception(
                f"Something went wrong while creating threads in {message.channel.id}.",
                exc_info=True,
            )
        except ValueError:
            await message.channel.send(
                warning("This server does not have a guild info attached to it")
            )
            log.exception(
                f"Guild {message.guild.id} does not have a guild info attached to it.",
                exc_info=True,
            )
        else:
            if message_toggle:
                threadmessage: str = await self.config.guild(message.guild).message()
                color = await self.bot.get_embed_color(message.channel)
                kwargs = process_tagscript(
                    threadmessage,
                    {
                        "server": tse.GuildAdapter(message.guild),
                        "author": tse.MemberAdapter(message.author),  # type: ignore
                        "member": tse.MemberAdapter(message.author),  # type: ignore
                        "color": tse.StringAdapter(str(color)),
                    },
                )
                if not kwargs:
                    await self.config.guild(message.guild).message.clear()
                    kwargs = process_tagscript(
                        thread_message,
                        {
                            "server": tse.GuildAdapter(message.guild),
                            "author": tse.MemberAdapter(message.author),  # type: ignore
                            "member": tse.MemberAdapter(message.author),  # type: ignore
                            "color": tse.StringAdapter(str(color)),
                        },
                    )
                await thread.send(**kwargs)
