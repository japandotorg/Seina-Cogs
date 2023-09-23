"""
MIT License

Copyright (c) 2022-present japandotorg

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
from typing import Final, List, Literal, Optional

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .views import URLView

log: logging.Logger = logging.getLogger("red.seina.firstmesssage")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class FirstMessage(commands.Cog):
    """
    Provides a link to the first message in the provided channel.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @commands.command()
    @commands.has_permissions(read_message_history=True)
    @commands.bot_has_permissions(read_message_history=True)
    async def firstmessage(
        self,
        ctx: commands.Context,
        channel: Optional[
            discord.TextChannel
            | discord.Thread
            | discord.DMChannel
            | discord.GroupChannel
            | discord.User
            | discord.Member
        ] = commands.CurrentChannel,
    ):
        """
        Provide a link to the first message in current or provided channel.
        """
        try:
            messages = [message async for message in channel.history(limit=1, oldest_first=True)]

            chan = (
                f"<@{channel.id}>"
                if isinstance(channel, discord.DMChannel | discord.User | discord.Member)
                else f"<#{channel.id}>"
            )

            embed: discord.Embed = discord.Embed(
                color=await ctx.embed_color(),
                timestamp=messages[0].created_at,
                description=f"[First message in]({messages[0].jump_url}) {chan}",
            )
            embed.set_author(
                name=messages[0].author.display_name,
                icon_url=messages[0].author.avatar.url
                if messages[0].author.avatar
                else messages[0].author.display_avatar.url,
            )

        except (discord.Forbidden, discord.HTTPException, IndexError, AttributeError):
            log.exception(f"Unable to read message history for {channel.id}")
            return await ctx.maybe_send_embed("Unable to read message history for that channel.")

        view = URLView(label="Jump to message", jump_url=messages[0].jump_url)

        await ctx.send(embed=embed, view=view)
