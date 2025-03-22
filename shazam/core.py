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
from typing import Final, List, Literal, Optional, TypeAlias

import aiohttp
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list
from redbot.core.utils.views import SimpleMenu
from shazamio.serializers import PlayList

from .model import Shazam as Client
from .model import Shazamed
from .utils import TopFlags, is_valid_url, with_context_typing

log: logging.Logger = logging.getLogger("red.seina.shazam")

RequestType: TypeAlias = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class Shazam(commands.Cog):
    """
    Search songs on Shazam.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.2.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.client: Client = Client(cog=self)

    async def cog_unload(self) -> None:
        if hasattr(self, "session"):
            self.bot.loop.create_task(self.session.close())

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n: Literal["\n", ""] = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @commands.group(name="shazam", invoke_without_command=True)
    @commands.has_permissions(embed_links=True, attach_files=True)
    @commands.bot_has_permissions(embed_links=True, attach_files=True)
    @with_context_typing()
    async def shazam(
        self,
        ctx: commands.Context,
        *,
        url_or_attachment: Optional[str],
    ):
        """
        Find a song name from video or audio using Shazam.
        """
        if url_or_attachment and is_valid_url(url_or_attachment):
            song: Shazamed = await self.client.recognize_from_url(url_or_attachment)
        elif ctx.message.attachments:
            attachment: discord.File = await ctx.message.attachments[0].to_file()
            try:
                song: Shazamed = await self.client.recognize(attachment.fp.read())
            except ValueError as error:
                await ctx.send(
                    str(error),
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
        elif (
            ctx.message.reference
            and (reply := ctx.message.reference.resolved)
            and isinstance(ctx.channel, (discord.Thread, discord.TextChannel))
        ):
            if isinstance(reply, discord.DeletedReferencedMessage):
                await ctx.send(
                    "Could not find any attachments on the referenced message.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            if not reply.attachments:
                await ctx.send(
                    "Referenced message has no attachments.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            attachment: discord.File = await reply.attachments[0].to_file()
            song: Shazamed = await self.client.recognize(attachment.fp.read())
        else:
            await ctx.send_help()
            return
        embed: discord.Embed = discord.Embed(
            description="[**{title}** - **{artist}**]({url})\n\n{metadata}".format(
                title=song.track.title,
                artist=song.track.subtitle,
                url=song.share["href"],
                metadata=song.metadata,
            )
        )
        embed.set_thumbnail(url=song.share["image"])
        embed.set_footer(text="shazam.com", icon_url="https://i.imgur.com/USbgv50h.jpg")
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @shazam.command(name="top")
    @commands.has_permissions(embed_links=True, attach_files=True)
    @commands.bot_has_permissions(embed_links=True, attach_files=True)
    @with_context_typing()
    async def shazam_top(self, ctx: commands.Context, *, flags: TopFlags):
        """
        Get top tracks from the shazam leaderboards.

        **Flag Help**:
        - `genre (aliases: g)`: search genre specific leaderboard.
        - `country (aliases: cy, cr, co)`: search country specific leaderboard.
        - `city (aliases: ct, ci)`: search city specific leaderboard.
        - `limit (aliases: l)`: limit how many tracks should this command return.

        **Flag Usage**:
        - `genre`: pop, hiphop, dance, electronic, soul, alternative, rock, latin, film, country, afro,
        worldwide, reggae, house, kpop, french, singer, mexicano.
        - `country`: country must be an ISO 3166-3 alpha-2 code. (eg: RU,NL,UA)
        - `city`: city name can be found [here](<https://github.com/dotX12/dotX12/blob/main/city.json>).

        **Examples**:
        - `[p]shazam top g:hiphop`
        - `[p]shazam top cr:us ct:detroit`
        - `[p]shazam top cr:us`
        - `[p]shazam top cr:us g:hiphop`
        """
        playlists: List[PlayList] = await self.client.from_flags(flags)
        embeds: List[discord.Embed] = []
        for idx, pl in enumerate(playlists):
            embed: discord.Embed = discord.Embed(
                description=(
                    "[**{index}**. **{name}**]({url})\n\n"
                    "- **Artist**: {artist}\n"
                    "- **Album**: {album}\n"
                    "- **Track Number:** {num} (disk {disk})\n"
                    "- **Release Date**: {release}\n"
                    "- **Genre**: {genre}\n"
                    "{rating}"
                ).format(
                    index=idx + 1,
                    name=pl.attributes.name,
                    url=pl.attributes.url,
                    artist=pl.attributes.artist_name,
                    album=pl.attributes.album_name,
                    num=pl.attributes.track_number,
                    disk=pl.attributes.disc_number,
                    release=pl.attributes.release_date,
                    genre=humanize_list(pl.attributes.genre_names),
                    rating=(
                        "- **Rating:** {}\n".format(rating.capitalize())
                        if (rating := pl.attributes.content_rating)
                        else ""
                    ),
                )
            )
            embed.set_thumbnail(
                url=pl.attributes.artwork.url.format(
                    w=pl.attributes.artwork.width, h=pl.attributes.artwork.height
                )
            )
            embed.set_footer(
                text="{}/{}".format(idx + 1, len(playlists)),
                icon_url="https://i.imgur.com/USbgv50h.jpg",
            )
            embeds.append(embed)
        await SimpleMenu(embeds, disable_after_timeout=True).start(ctx)
