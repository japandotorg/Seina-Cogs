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

from __future__ import annotations

import io
import logging
from typing import Any, Dict, Final, List, Literal, Optional

import aiohttp
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.chat_formatting import humanize_list

from .exceptions import CommandWarning
from .model import Shazam

log: logging.Logger = logging.getLogger("red.seina.massunban")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

_ = Translator("Shazam", __file__)


@cog_i18n(_)
class Shazam(commands.Cog):
    """
    Search songs on Shazam.
    """

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.shazam: Shazam = Shazam(bot, self)

    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, io.BytesIO]:
        """
        Nothing to delete
        """
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"User_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, io.BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Optional[int] = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @commands.command(name="shazam")
    @commands.has_permissions(embed_links=True, attach_files=True)
    @commands.bot_has_permissions(embed_links=True, attach_files=True)
    async def _shazam(self, ctx: commands.Context, *, url_or_attachment: Optional[str]):
        """
        Find a song name from video or audio using Shazam.
        """
        if url_or_attachment:
            result = await self.shazam.recognize_from_url(url_or_attachment)

        elif ctx.message.attachments:
            attachment = await ctx.message.attachments[0].to_file()
            result = await self.shazam.recognize_file(attachment.fp.read())

        elif (
            ctx.message.reference
            and ctx.message.reference.message_id
            and isinstance(ctx.channel, (discord.Thread, discord.TextChannel))
        ):
            reply_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if not reply_message.attachments:
                raise CommandWarning(_("Referenced message has no attachments"))
            attachment = await reply_message.attachments[0].to_file()
            result = await self.shazam.recognize_file(attachment.fp.read())

        else:
            return await ctx.send_help()

        if result is None:
            raise CommandWarning(_("I was unable to recognize any music from this."))

        metadata = "\n".join([f'`{data["title"]}:` {data["text"]}' for data in result.metadata])

        embed: discord.Embed = discord.Embed(
            description=f"**{result.song}** by **{result.artist}**\n>>> {metadata}",
            color=await ctx.embed_color(),
        )
        embed.set_author(
            name=_("Shazam"), url=result.url, icon_url="https://i.imgur.com/USbgv50h.jpg"
        )
        embed.set_thumbnail(url=result.cover_art)
        await ctx.send(embed=embed)
