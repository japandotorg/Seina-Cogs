from typing import Any, Dict, List

import discord
import TagScriptEngine as tse
from redbot.core import commands

from ._tagscript import boosted, process_tagscript, unboosted
from .abc import CompositeMetaClass, MixinMeta


class EventMixin(MixinMeta, metaclass=CompositeMetaClass):
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot:

            return
        if message.guild.system_channel_flags.premium_subscriptions and message.type in (
            discord.MessageType.premium_guild_subscription,
            discord.MessageType.premium_guild_tier_1,
            discord.MessageType.premium_guild_tier_2,
            discord.MessageType.premium_guild_tier_3,
        ):
            self.bot.dispatch("member_boost", message.author)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if not after.guild:
            return
        if role := after.guild.premium_subscriber_role:
            if role in before.roles and role not in after.roles:
                self.bot.dispatch("member_unboost", before)
            elif role not in before.roles and role in after.roles:
                self.bot.dispatch("member_boost", after)

    @commands.Cog.listener()
    async def on_member_boost(self, member: discord.Member) -> None:
        guild: discord.Guild = member.guild
        channels: List[int] = await self.config.guild(guild).boost_message.channels()  # type: ignore
        message: str = await self.config.guild(guild).boost_message.boosted()  # type: ignore
        toggle: bool = await self.config.guild(guild).boost_message.toggle()  # type: ignore
        if not toggle:
            return
        kwargs: Dict[str, Any] = process_tagscript(
            message,
            {
                "member": tse.MemberAdapter(member),
                "guild": tse.GuildAdapter(guild),
            },
        )
        if not kwargs:
            await self.config.guild(member.guild).boost_message.boosted.clear()  # type: ignore
            kwargs: Dict[str, Any] = process_tagscript(
                boosted,
                {
                    "member": tse.MemberAdapter(member),
                    "guild": tse.GuildAdapter(guild),
                },
            )
        for channel_id in channels:
            channel: discord.TextChannel = guild.get_channel(channel_id)  # type: ignore
            if channel:
                await channel.send(**kwargs)

    @commands.Cog.listener()
    async def on_member_unboost(self, member: discord.Member) -> None:
        guild: discord.Guild = member.guild
        channels: List[int] = await self.config.guild(guild).boost_message.channels()  # type: ignore
        message: str = await self.config.guild(guild).boost_message.unboosted()  # type: ignore
        toggle: bool = await self.config.guild(guild).boost_message.toggle()  # type: ignore
        if not toggle:
            return
        kwargs: Dict[str, Any] = process_tagscript(
            message,
            {
                "member": tse.MemberAdapter(member),
                "guild": tse.GuildAdapter(guild),
            },
        )
        if not kwargs:
            await self.config.guild(member.guild).boost_message.unboosted.clear()  # type: ignore
            kwargs: Dict[str, Any] = process_tagscript(
                unboosted,
                {
                    "member": tse.MemberAdapter(member),
                    "guild": tse.GuildAdapter(guild),
                },
            )
        for channel_id in channels:
            channel: discord.TextChannel = guild.get_channel(channel_id)  # type: ignore
            if channel:
                await channel.send(**kwargs)
