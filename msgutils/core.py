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

import re
from io import BytesIO
from typing import Any, Dict, Final, List, Literal, Type, TypeVar

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list, inline

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

RTT = TypeVar("RTT", bound="RequestType")


class MsgUtils(commands.Cog):
    """Utilities to view raw messages"""

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.bot: Red = bot

    async def cog_load(self) -> None:
        await self.bot.wait_until_red_ready()

    async def red_get_data_for_user(self, *, user_id: int) -> Dict[str, BytesIO]:
        """Get a user's personal data."""
        data: Any = f"No data is stored for user with ID {user_id}.\n"
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(
        self, *, requester: Type[RTT], user_id: int
    ) -> Dict[str, BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        data: Any = f"No data is stored for user with ID {user_id}.\n"
        return {"user_data.txt": BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)

    async def _dump(
        self, ctx: commands.Context, channel: discord.TextChannel, msg_id: int
    ) -> None:
        if msg_id:
            try:
                msg: discord.Message = await channel.fetch_message(msg_id)
            except discord.NotFound:
                await ctx.send("Invalid message id")
                return
            else:
                msg_limit = 2 if channel == ctx.channel else 1
                async for message in channel.history(limit=msg_limit):
                    msg = message
            content = msg.content.strip()
            content = re.sub(r"<(:[0-9a-z_]+:)\d{18}>", r"\1", content, flags=re.IGNORECASE)
            content = box(content.replace("`", "\u200b`"))
            await ctx.send(content)

    @commands.command()
    @commands.mod_or_permissions(manage_messages=True)
    async def editmsg(
        self, ctx: commands.Context, channel: discord.TextChannel, msg_id: int, *, new_msg: str
    ) -> None:
        """
        Gven a channel and an ID for a message printed in that channel, replaces it
        """
        try:
            msg: discord.Message = await channel.fetch_message(msg_id)
        except discord.NotFound:
            await ctx.send(inline("Cannot find the message, check the channel and message id."))
            return
        except discord.Forbidden:
            await ctx.send(inline("I do not have the permissions to do that."))
            return
        if msg.author.id != self.bot.user.id:
            await ctx.send(inline("I can only edit my own messages."))
            return

        await msg.edit(content=new_msg)
        await ctx.tick()

    @commands.command()
    @commands.mod_or_permissions(manage_messages=True)
    async def dumpchannel(
        self, ctx: commands.Context, channel: discord.TextChannel, msg_id: int
    ) -> None:
        """
        Gven a channel and an ID for a message printed in that channel, dumps it
        boxed wth formatted escaped and some issues cleaned up.
        """
        await self._dump(ctx, channel, msg_id)

    @commands.command()
    @commands.mod_or_permissions(manage_messages=True)
    async def dumpmsg(self, ctx: commands.Context, msg_id: int) -> None:
        """
        Gven an ID for a message printed in the current channel, dumps it
        boxed wth formatted escaped and some issues cleaned up.
        """
        await self._dump(ctx, ctx.channel, msg_id)

    @commands.command(aliases=["dumpexactmsg"])
    @commands.mod_or_permissions(manage_messages=True)
    async def dumpmsgexact(self, ctx: commands.Context, msg_id: int) -> None:
        """
        Given a ID for a message printed in the current channel, dumps it
        boxed with formatting escaped.
        """
        msg = await ctx.channel.fetch_message(msg_id)
        content = msg.content.strip()
        content = box(content.replace("`", "\u200b`"))
        await ctx.send(content)
