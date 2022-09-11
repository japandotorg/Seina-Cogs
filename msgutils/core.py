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

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, inline


class MsgUtils(commands.Cog):
    """Utilities to view raw messages"""

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @classmethod
    async def initialize(cls, bot: Red):
        await bot.wait_until_red_ready()

    async def red_get_data_for_user(self, *, user_id):
        """Get a user's personal data."""
        data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        return

    async def _dump(self, ctx, channel: discord.TextChannel = None, msg_id: int = None):
        if msg_id:
            try:
                msg = await channel.fetch_message(msg_id)
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
    async def editmsg(self, ctx, channel: discord.TextChannel, msg_id: int, *, new_msg: str):
        """
        Gven a channel and an ID for a message printed in that channel, replaces it
        """
        try:
            msg = await channel.fetch_message(msg_id)
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
    async def dumpchannel(self, ctx, channel: discord.TextChannel, msg_id: int = None):
        """
        Gven a channel and an ID for a message printed in that channel, dumps it
        boxed wth formatted escaped and some issues cleaned up.
        """
        await self._dump(ctx, channel, msg_id)

    @commands.command()
    @commands.mod_or_permissions(manage_messages=True)
    async def dumpmsg(self, ctx, msg_id: int = None):
        """
        Gven an ID for a message printed in the current channel, dumps it
        boxed wth formatted escaped and some issues cleaned up.
        """
        await self._dump(ctx, ctx.channel, msg_id)

    @commands.command(aliases=["dumpexactmsg"])
    @commands.mod_or_permissions(manage_messages=True)
    async def dumpmsgexact(self, ctx, msg_id: int):
        """
        Given a ID for a message printed in the current channel, dumps it
        boxed with formatting escaped.
        """
        msg = await ctx.channel.fetch_message(msg_id)
        content = msg.content.strip()
        content = box(content.replace("`", "\u200b`"))
        await ctx.send(content)
