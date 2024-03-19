"""
MIT License

Copyright (c) 2024-present japandotorg

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

import discord
from redbot.core import commands

from .abc import CompositeMetaClass, MixinMeta
from .utils import search_for_emojis


class EventMixin(MixinMeta, metaclass=CompositeMetaClass):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.guild is None:
            return
        await self.wait_until_cog_ready()
        if message.guild.id in self.cache.autoreact:
            asyncio.ensure_future(self.do_autoreact(message))
        if message.guild.id in self.cache.event:
            if "images" in self.cache.event[message.guild.id] and message.attachments:
                asyncio.ensure_future(self.do_autoreact_event(message, "event"))
            if "spoilers" in self.cache.event[message.guild.id] and (
                message.content.count("||") > 2
            ):
                asyncio.ensure_future(self.do_autoreact_event(message, "spoilers"))
            if "emojis" in self.cache.event[message.guild.id] and search_for_emojis(
                message.content
            ):
                asyncio.ensure_future(self.do_autoreact_event(message, "emojis"))
            if "stickers" in self.cache.event[message.guild.id] and message.stickers:
                asyncio.ensure_future(self.do_autoreact_event(message, "stickers"))
