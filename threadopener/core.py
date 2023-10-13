"""
MIT License

Copyright (c) 2021-present Kuro-Rui

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
from typing import Dict, Final, List, Union, Optional

import discord
from redbot.core.bot import Red
from redbot.core import Config, commands
from redbot.core.utils.chat_formatting import humanize_list

from .abc import CompositeMetaClass
from .commands import Commands

log: logging.Logger = logging.getLogger("red.seina.threadopener")


class ThreadOpener(
    commands.Cog,
    Commands,
    metaclass=CompositeMetaClass,
):
    """
    A cog to open continuouS threads to messages in a channel.
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
        default_guilds: Dict[str, Optional[Union[List[int], bool]]] = {
            "toggle": False,
            "channels": [],
            "slowmode_delay": None,
            "auto_archive_duration": None,
        }
        self.config.register_guild(**default_guilds)

        self.spam_control: commands.CooldownMapping = commands.CooldownMapping.from_cooldown(
            1, 10, commands.BucketType.guild
        )

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

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
        ):
            await self.config.guild(message.guild).toggle.set(False)
            log.info(
                f"ThreadOpener has been disabled due to missing permissions in {message.guild.name}.",
            )
            return
        if "THREADS_ENABLED" not in message.guild.features:
            await self.config.guild(message.guild).toggle.set(False)
            log.info(
                f"ThreadOpener has been disabled due to missing threads channel feature in {message.guild.name}.",
            )
            return

        bucket = self.spam_control.get_bucket(message)
        current = message.created_at.timestamp()
        retry_after = bucket and bucket.update_rate_limit(current)
        if retry_after:
            return

        slowmode_delay = await self.config.guild(message.guild).slowmode_delay()
        auto_archive_duration = await self.config.guild(message.guild).auto_archive_duration()

        try:
            await message.create_thread(
                name=f"{message.author.global_name}",
                auto_archive_duration=auto_archive_duration,
                slowmode_delay=slowmode_delay,
                reason="ThreadOpener initiate.",
            )
        except discord.Forbidden:
            await message.channel.send(
                "I do not have permissions to create threads in this channel."
            )
        except discord.HTTPException:
            await message.channel.send(
                "Something went wrong while creating threads in this channel."
            )
            log.exception(
                f"Something went wrong while creating threads in {message.channel.id}.",
                exc_info=True,
            )
        except ValueError:
            await message.channel.send("This guild does not have a guild info attached to it")
            log.exception(
                f"Guild {message.guild.id} does not have a guild info attached to it.",
                exc_info=True,
            )
