from typing import Union

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list

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

        `<guild> :` The server the corresponding role and emoji is from.
        `<role>  :` The applied role for the badge.
        `<emoji> :` The corresponding emoji.
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
        
        `<name> :` Name of the default emoji. Available options - {}.
        `<emoji>:` The corresponding emoji.
        """.format(
            humanize_list(list(StatusEmoji.__args__), style="or")
        )
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
        
        `<name> :` Name of the default emoji. Available options - {}.
        `<emoji>:` The corresponding emoji.
        """.format(
            humanize_list(list(DeviceEmoji.__args__), style="or")
        )
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_device_emoji(name, emoji_id)
        await ctx.tick()

    @_info_set_emoji.command(name="badge", usage="<name> <emoji>")  # type: ignore
    async def _info_set_emoji_badge(
        self, ctx: commands.Context, name: BadgeEmoji, emoji: Union[int, discord.Emoji]
    ):
        """
        Configure the default status emojis.
        
        **Arguments**:
        
        `<name> :` Name of the default emoji. Available options - {}.
        `<emoji>:` The corresponding emoji.
        """.format(
            humanize_list(list(BadgeEmoji.__args__), style="or")
        )
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_badge_emoji(name, emoji_id)
        await ctx.tick()

    @_info_set_emoji.command(name="select", usage="<name> <emoji>")  # type: ignore
    async def _info_set_emoji_select(
        self, ctx: commands.Context, name: SelectEmoji, emoji: Union[int, discord.Emoji]
    ):
        """
        Configure the default status emojis.
        
        **Arguments**:
        
        `<name> :` Name of the default emoji. Available options - {}.
        `<emoji>:` The corresponding emoji.
        """.format(
            humanize_list(list(SelectEmoji.__args__), style="or")
        )
        emoji_id: int = emoji.id if isinstance(emoji, discord.Emoji) else emoji
        await self.cache.set_select_emoji(name, emoji_id)
        await ctx.tick()
