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

import contextlib
import datetime
import functools
from typing import TYPE_CHECKING, Any, List, Optional, Set, Tuple, Union, cast

import discord
from redbot.cogs.mod.mod import Mod
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils import AsyncIter
from redbot.core.utils.common_filters import filter_invites

from .cache import Cache
from .utils import get_roles


class UISelect(discord.ui.Select["UIView"]):
    if TYPE_CHECKING:
        view: "UIView"

    def __init__(
        self,
        cache: Cache,
        user: discord.Member,
        banner_and_gavatar: Tuple[Optional[discord.Asset], Optional[discord.Asset]],
        callback: Any,
    ) -> None:
        self.user: discord.Member = user
        self.cache: Cache = cache

        banner, gavatar = banner_and_gavatar
        self.banner: Optional[discord.Asset] = banner
        self.gavatar: Optional[discord.Asset] = gavatar

        options: List[discord.SelectOption] = [
            discord.SelectOption(
                label="Home",
                emoji=self.cache.get_select_emoji("home"),
                value="home",
                description="General info, join dates, badges, status, etc...",
            ),
            discord.SelectOption(
                label="Avatar",
                emoji=self.cache.get_select_emoji("avatar"),
                value="avatar",
                description="View the user's global avatar...",
            ),
        ]
        if self.gavatar:
            options.append(
                discord.SelectOption(
                    label="Guid Avatar",
                    emoji=self.cache.get_select_emoji("gavatar"),
                    value="gavatar",
                    description="View the user's guild avatar...",
                )
            )
        if self.banner:
            options.append(
                discord.SelectOption(
                    label="Banner",
                    emoji=self.cache.get_select_emoji("banner"),
                    value="banner",
                    description="View the user's banner...",
                )
            )
        if get_roles(self.user):
            options.append(
                discord.SelectOption(
                    label="Roles",
                    emoji=self.cache.get_select_emoji("roles"),
                    value="roles",
                    description="View the user's roles..",
                )
            )
        super().__init__(
            custom_id="ui:select",
            placeholder="Choose a page to view...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.callback: functools.partial[Any] = functools.partial(callback, self)


class UIView(discord.ui.View):
    def __init__(
        self,
        ctx: commands.GuildContext,
        user: discord.Member,
        cache: Cache,
        banner_and_gavatar: Tuple[Optional[discord.Asset], Optional[discord.Asset]],
        *,
        timeout: float = 60.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.ctx: commands.GuildContext = ctx
        self.bot: Red = ctx.bot
        self.cache: Cache = cache

        self.user: discord.Member = user
        self.banner_and_gavatar: Tuple[Optional[discord.Asset], Optional[discord.Asset]] = (
            banner_and_gavatar
        )

        self.embed: discord.Embed = discord.utils.MISSING
        self._message: discord.Message = discord.utils.MISSING

        self._select: UISelect = UISelect(
            self.cache, self.user, self.banner_and_gavatar, self._callback
        )
        self.add_item(self._select)

    @staticmethod
    async def _callback(self: UISelect, interaction: discord.Interaction[Red]) -> None:
        await interaction.response.defer()
        value: str = self.values[0]
        if value == "home":
            embed: discord.Embed = await self.view._make_embed()
            await interaction.edit_original_response(embed=embed)
        elif value == "avatar":
            embed: discord.Embed = discord.Embed(
                color=self.user.color, title="{}'s Avatar".format(self.user.display_name)
            )
            embed.set_image(
                url=(self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)
            )
            await interaction.edit_original_response(embed=embed)
        elif value == "gavatar":
            embed: discord.Embed = discord.Embed(
                color=self.user.color,
                title="{}'s Guild Avatar".format(self.user.display_name),
            )
            if gavatar := self.gavatar:
                embed.set_image(url=gavatar.url)
            else:
                embed.description = "{}  does not have a guild specific avatar.".format(
                    self.user.mention
                )
            await interaction.edit_original_response(embed=embed)
        elif value == "banner":
            embed: discord.Embed = discord.Embed(
                color=self.user.color, title="{}'s Banner".format(self.user.display_name)
            )
            if banner := self.banner:
                embed.set_image(url=banner.url)
            else:
                embed.description = "{} does not have a banner.".format(self.user.mention)
            await interaction.edit_original_response(embed=embed)
        elif value == "roles":
            embed: discord.Embed = discord.Embed(
                color=self.user.color, title="{}'s Roles".format(self.user.display_name)
            )
            embed.description = (
                await self.view._format_roles()
                if get_roles(self.user)
                else "{} does not have any roles in this server.".format(self.user.mention)
            )
            await interaction.edit_original_response(embed=embed)

    @classmethod
    async def make_embed(
        cls,
        ctx: commands.GuildContext,
        user: discord.Member,
        cache: Cache,
        banner_and_gavatar: Tuple[Optional[discord.Asset], Optional[discord.Asset]],
    ) -> discord.Embed:
        self: "UIView" = cls(
            ctx=ctx, user=user, cache=cache, banner_and_gavatar=banner_and_gavatar
        )
        return await self._make_embed()

    async def on_timeout(self) -> None:
        for child in self.children:
            child: discord.ui.Item["UIView"]
            if hasattr(child, "disabled"):
                child.disabled = True  # type: ignore
        with contextlib.suppress(discord.HTTPException):
            if self._message is not discord.utils.MISSING:
                await self._message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(
                content="You're not the author of this message.", ephemeral=True
            )
            return False
        return True

    async def _format_roles(self) -> Union[str, Any]:
        roles: Optional[List[str]] = get_roles(self.user)
        if roles:
            string: str = ", ".join(roles)
            if len(string) > 4000:
                formatted: str = "and {number} more roles not displayed due to embed limits."
                available_length: int = 4000 - len(formatted)
                chunks = []
                remaining = 0
                for r in roles:
                    chunk = "{}\n".format(r)
                    size = len(chunk)
                    if size < available_length:
                        available_length -= size
                        chunks.append(chunk)
                    else:
                        remaining += 1
                chunks.append(formatted.format(number=remaining))
                string: str = "".join(chunks)
        else:
            string: str = discord.utils.MISSING
        return string

    async def _make_embed(self) -> discord.Embed:
        if self.embed is not discord.utils.MISSING:
            return self.embed
        user: discord.Member = self.user
        shared: Union[List[discord.Guild], Set[discord.Guild]] = (
            user.mutual_guilds
            if hasattr(user, "mutual_guilds")
            else {
                guild
                async for guild in AsyncIter(self.bot.guilds, steps=100)
                if user in guild.members
            }
        )
        mod: Mod = self.bot.get_cog("Mod")  # type: ignore
        try:
            names, _, nicks = await mod.get_names(user)
        except AttributeError:
            names, nicks = await mod.get_names_and_nicks(user)  # type: ignore | specially for melon
        created_dt: float = (
            cast(datetime.datetime, user.created_at)
            .replace(tzinfo=datetime.timezone.utc)
            .timestamp()
        )
        since_created: str = "<t:{}:R>".format(int(created_dt))
        if user.joined_at:
            joined_dt: float = (
                cast(datetime.datetime, user.joined_at)
                .replace(tzinfo=datetime.timezone.utc)
                .timestamp()
            )
            since_joined: str = "<t:{}:R>".format(int(joined_dt))
            user_joined: str = "<t:{}>".format(int(joined_dt))
        else:
            since_joined: str = "?"
            user_joined: str = "Unknown"
        user_created = "<t:{}>".format(int(created_dt))
        position: int = (
            sorted(
                self.ctx.guild.members, key=lambda m: m.joined_at or self.ctx.message.created_at
            ).index(user)
            + 1
        )
        created_on: str = "{}\n( {} )\n".format(user_created, since_created)
        joined_on: str = "{}\n( {} )\n".format(user_joined, since_joined)
        if self.bot.intents.presences:
            mobile, web, desktop = self.cache.get_member_device_status(user)
            status: str = mod.get_status_string(user)
            if status:
                description: str = "{}\n**Devices:** {} {} {}\n\n".format(
                    status, mobile, web, desktop
                )
            else:
                description: str = "{} {} {}\n\n".format(mobile, web, desktop)
        else:
            description: str = ""
        embed: discord.Embed = discord.Embed(
            description=(
                description + "**Shared Servers: {}**".format(len(shared))
                if len(shared) > 1
                else "**Shared Server: {}**".format(len(shared))
            ),
            color=user.color,
        )
        embed.add_field(name="Joined Discord on:", value=created_on)
        embed.add_field(name="Joined this Server on:", value=joined_on)
        if names:
            val = filter_invites(", ".join(names))
            embed.add_field(name="Previous Names:", value=val, inline=False)
        if nicks:
            val = filter_invites(", ".join(nicks))
            embed.add_field(name="Previous Nicknames:", value=val, inline=False)
        if user.voice and user.voice.channel:
            embed.add_field(
                name="Current Voice Channel:",
                value="{0.mention} ID: {0.id}".format(user.voice.channel),
                inline=False,
            )
        embed.set_footer(text="Member #{} | User ID: {}".format(position, user.id))
        name = " ~ ".join((str(user), user.nick)) if user.nick else user.display_name
        embed.title = name
        embed.set_thumbnail(url=user.display_avatar.with_static_format("png").url)
        badges, badge_count = await self.cache.get_user_badges(user)
        if badges:
            embed.add_field(
                name="Badges:" if badge_count > 1 else "Badge:", value=badges, inline=False
            )
        special = self.cache.get_special_badges(user)
        if special:
            embed.add_field(
                name="Special Badges:" if len(special) > 1 else "Special Badge:",
                value="\n".join(special),
                inline=False,
            )
        self.embed: discord.Embed = embed
        return embed
