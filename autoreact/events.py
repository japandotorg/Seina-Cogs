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
