from typing import Union

import discord
from redbot.core import commands

from .abc import CompositeMetaClass, MixinMeta
from .cache import BadgeEmoji, DeviceEmoji, SelectEmoji, StatusEmoji


class SettingsCommands(MixinMeta, metaclass=CompositeMetaClass):
    @commands.is_owner()
    @commands.group(name="infoset")
    async def _info_set(self, _: commands.Context):
        """
        Settings configuration.
        """

    @_info_set.command(name="special")  # type: ignore
    async def _info_set_special(
        self,
        ctx: commands.Context,
        guild: Union[int, discord.Guild],
        role: Union[int, discord.Role],
        emoji: Union[int, discord.Emoji],
    ):
        """
        Configure the special badges.

        **Arguments**:

        `<guild> :` The server the corresponding role is from.
        `<role>  :` The applied role for the badge.
        `<emoji> :` The corresponding emoji (any emoji [botname] has access to).
        """
        guild_id: int = guild.id if isinstance(guild, discord.Guild) else guild
        role_id: int = role.id if isinstance(role, discord.Role) else role
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_special_badge(guild_id, role_id, emoji_id)
        await ctx.tick()

    @_info_set.group(name="emoji", aliases=["e"])  # type: ignore
    async def _info_set_emoji(self, _: commands.Context):
        """
        Emoji settings configuration
        """

    @_info_set_emoji.command(name="status", usage="<name> <emoji>")  # type: ignore
    async def _info_set_emoji_status(
        self, ctx: commands.Context, name: StatusEmoji, emoji: Union[int, discord.Emoji]
    ):
        """
        Configure the default status emojis.
        
        **Arguments**:
        
        `<name> :` Name of the default emoji. Available options - online, away, 
        dnd, offline, or streaming.
        `<emoji>:` The corresponding emoji.
        """
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_status_emoji(name, emoji_id)
        await ctx.tick()

    @_info_set_emoji.command(name="device", usage="<name> <emoji>")  # type: ignore
    async def _info_set_emoji_device(
        self, ctx: commands.Context, name: DeviceEmoji, emoji: Union[int, discord.Emoji]
    ):
        """
        Configure the default device emojis.
        
        **Arguments**:
        
        `<name> :` Name of the default emoji. Available options - mobile_online, 
        mobile_idle, mobile_dnd, mobile_offline, web_online, web_idle, web_dnd, 
        web_offline, desktop_online, desktop_idle, desktop_dnd, or desktop_offline.
        `<emoji>:` The corresponding emoji.
        """
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_device_emoji(name, emoji_id)
        await ctx.tick()

    @_info_set_emoji.command(name="badge", usage="<name> <emoji>")  # type: ignore
    async def _info_set_emoji_badge(
        self, ctx: commands.Context, name: BadgeEmoji, emoji: Union[int, discord.Emoji]
    ):
        """
        Configure the default badge emojis.
        
        **Arguments**:
        
        `<name> :` Name of the default emoji. Available options - staff, 
        early_supporter, verified_bot_developer, active_developer, bug_hunter, 
        bug_hunter_level_2, partner, verified_bot, hypesquad, hypesquad_balance, 
        hypesquad_bravery, hypesquad_brilliance, nitro, 
        discord_certified_moderator, or bot_http_interactions.
        `<emoji>:` The corresponding emoji.
        """
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_badge_emoji(name, emoji_id)
        await ctx.tick()

    @_info_set_emoji.command(name="select", usage="<name> <emoji>")  # type: ignore
    async def _info_set_emoji_select(
        self, ctx: commands.Context, name: SelectEmoji, emoji: Union[int, discord.Emoji]
    ):
        """
        Configure the default select emojis.
        
        **Arguments**:
        
        `<name> :` Name of the default emoji. Available options - roles, home, 
        avatar, banner, or gavatar.
        `<emoji>:` The corresponding emoji.
        """
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_select_emoji(name, emoji_id)
        await ctx.tick()
