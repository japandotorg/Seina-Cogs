"""
MIT License

Copyright (c) 2020-2023 PhenoM4n4n
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

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Union, List, Tuple, Optional

import discord
from redbot.core import commands
from redbot.core.modlog import Case, create_case

from .abc import MixinMeta, CompositeMetaClass
from .converters import FuzzyRole, StrictRole
from .utils import my_role_heirarchy

log: logging.Logger = logging.getLogger("red.phenom4n4n.roleutils.autorole")


class AutoRole(MixinMeta, metaclass=CompositeMetaClass):
    """Manage autoroles and sticky roles."""

    async def initialize(self) -> None:
        log.debug("AutoRole Initialize")
        await super().initialize()

    async def _bulk_add_roles_to_member(
        self,
        member: discord.Member,
        roles: List[discord.Role],
    ) -> Tuple[List[discord.Role], List[discord.Role]]:
        to_add: List[discord.Role] = []
        not_needed: List[discord.Role] = []
        for role in roles:
            allowed = my_role_heirarchy(member.guild, role)
            if not allowed:
                not_needed.append(role)
            elif role in member.roles:
                not_needed.append(role)
            else:
                to_add.append(role)
        if to_add:
            await member.add_roles(*to_add, reason="[RoleUtils] assigned autorole added.")
            await self._create_case(
                member.guild,
                type="autorole",
                reason="[RoleUtils] assigned autorole added.",
                user=member,
            )
        return to_add, not_needed

    # https://github.com/TrustyJAID/Trusty-cogs/blob/master/roletools/events.py#L138
    async def _check_for_guild_verification(
        self, member: discord.Member, guild: discord.Guild
    ) -> Union[bool, int]:
        if member.roles:
            return False
        allowed_discord: timedelta = datetime.now(timezone.utc) - member.created_at
        allowed_server: timedelta = (
            (datetime.now(timezone.utc) - member.joined_at)
            if member.joined_at
            else timedelta(minutes=10)
        )
        if guild.verification_level.value >= 2 and allowed_discord < timedelta(minutes=5):
            log.debug("Waiting 5 minutes for %s in %s", member.name, guild)
            return 300 - int(allowed_discord.total_seconds())
        elif guild.verification_level.value >= 3 and allowed_server <= timedelta(minutes=10):
            log.debug("Waiting 10 minutes for %s in %s", member.name, guild)
            return 600 - int(allowed_server.total_seconds())
        return False

    async def _wait_for_guild_verification(
        self, member: discord.Member, guild: discord.Guild
    ) -> None:
        wait = await self._check_for_guild_verification(member, guild)
        if wait:
            log.debug("Waiting %s seconds before allowing the user to have a role", wait)
            await asyncio.sleep(int(wait))

    async def _create_case(
        self,
        guild: discord.Guild,
        type: str,
        reason: str,
        user: Union[discord.User, discord.Member],
        until: Optional[datetime] = None,
        moderator: Optional[Union[discord.Member, discord.ClientUser]] = None,
    ) -> Optional[Case]:
        try:
            case = await create_case(
                self.bot,
                guild,
                discord.utils.utcnow(),
                type,
                user,
                moderator=moderator if moderator is not None else guild.me,
                reason=reason,
                until=until,
            )
        except RuntimeError:
            case = None
        return case

    async def _auto_apply_role(self, member: discord.Member, roles: List[discord.Role]) -> None:
        await self._wait_for_guild_verification(member, member.guild)
        await self._bulk_add_roles_to_member(member, roles)

    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.group(name="autorole")
    async def _autorole(self, _: commands.GuildContext):
        """Manage autoroles and sticky roles."""

    @_autorole.command()
    async def toggle(self, ctx: commands.GuildContext, toggle: bool):
        """Toggle the auto role system."""
        await self.config.guild(ctx.guild).autoroles.toggle.set(toggle)
        await ctx.send(
            f"Auto role system is now {'enabled' if toggle else 'disabled'}.",
        )

    @_autorole.command()
    async def add(self, ctx: commands.GuildContext, *, role: StrictRole):
        """Add a role to be added to all new members on join."""
        async with self.config.guild(ctx.guild).autoroles.roles() as roles:
            if role.id not in roles:
                roles.append(role.id)
            else:
                raise commands.UserFeedbackCheckFailure(
                    f"{role.name} ({role.id}) is already an assigned autorole.",
                )
        await ctx.send(f"Assigned {role.name} ({role.id}) as an autorole.")

    @_autorole.command()
    async def remove(self, ctx: commands.Context, *, role: FuzzyRole):
        """Remove an autorole."""
        async with self.config.guild(ctx.guild).autoroles.roles() as roles:
            if role.id in roles:
                roles.remove(role.id)
            else:
                raise commands.UserFeedbackCheckFailure(
                    f"{role.name} ({role.id}) is not an assigned autorole.",
                )
        await ctx.send(f"Removed {role.name} ({role.id}) from the autoroles list.")

    @_autorole.group(name="humans")
    async def _humans(self, _: commands.Context):
        """Manage autoroles for humans."""

    @_humans.command(name="toggle")
    async def humans_toggle(self, ctx: commands.Context, toggle: bool):
        """Toggle the human only autorole system."""

    @_humans.command(name="add")
    async def humans_add(self, ctx: commands.Context, *, role: FuzzyRole):
        """Add a role to be added to all new humans on join."""

    @_humans.command(name="remove")
    async def humans_remove(self, ctx: commands.Context, *, role: Union[FuzzyRole, int]):
        """Remove an autorole for humans."""

    @_autorole.group(name="bots")
    async def _bots(self, ctx: commands.Context):
        """Manage autoroles for bots."""

    @_bots.command(name="add")
    async def bots_add(self, ctx: commands.Context, *, role: FuzzyRole):
        """Add a role to be added to all new bots on join."""

    @_bots.command(name="remove")
    async def bots_remove(self, ctx: commands.Context, *, role: Union[FuzzyRole, int]):
        """Remove an autorole for bots."""

    @_autorole.group(invoke_without_command=True, name="sticky")
    async def _sticky(self, ctx: commands.Context, true_or_false: bool = None):
        """Toggle whether the bot should reapply roles on member joins and leaves."""

    @_sticky.command(aliases=["bl"])
    async def blacklist(self, ctx: commands.Context, *, role: FuzzyRole):
        """Blacklist a role from being reapplied on joins."""

    @_sticky.command(aliases=["unbl"])
    async def unblacklist(self, ctx: commands.Context, *, role: Union[FuzzyRole, int]):
        """Remove a role from the sticky blacklist."""

    # @commands.Cog.listener("on_member_join")
    async def on_member_join_autorole(self, member: discord.Member):
        pass

    # @commands.Cog.listener("on_member_join")
    async def on_member_join_humans_autorole(self, member: discord.Member):
        pass
