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
from typing import Final, List, Optional, Tuple, Union, Any, Dict, NoReturn

import discord
from redbot.core import commands
from redbot.core.utils.antispam import AntiSpam
from redbot.core.modlog import Case, create_case

from .abc import CompositeMetaClass, MixinMeta
from .converters import FuzzyRole, StrictRole

log: logging.Logger = logging.getLogger("red.seina.roleutils.autorole")


class AutoRoles(MixinMeta, metaclass=CompositeMetaClass):
    """Manage autoroles."""

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.queue: asyncio.Queue[discord.Member] = asyncio.Queue()
        self.spam: Dict[int, AntiSpam] = {}

        self._task: asyncio.Task[NoReturn] = asyncio.create_task(self._handler_task())

    async def initialize(self) -> None:
        log.debug("AutoRole Initialize")
        await super().initialize()

    async def cog_unload(self) -> None:
        if self._task:
            self._task.cancel()

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

    async def _handle_member_join(self, member: discord.Member):
        roles: List[discord.Role] = []
        settings: Dict[str, Any] = await self.config.guild(member.guild).autoroles.all()
        if settings["toggle"]:
            roles.extend(settings["roles"])
        if not member.bot and settings["humans"]["toggle"]:
            roles.extend(settings["humans"]["roles"])
        elif member.bot and settings["bots"]["toggle"]:
            roles.extend(settings["bots"]["roles"])
        roles: List[discord.Role] = [
            role
            for role in roles
            if member.get_role(role.id) is None and member.guild.me.top_role > role
        ]
        if not roles:
            return
        reason: Final[str] = f"[RoleUtils] assigned autorole added."
        try:
            await member.add_roles(*roles, reason=reason)
        except discord.HTTPException:
            log.exception(
                "Uh Oh! Something went wrong trying to add roles to %s", member, exc_info=True
            )
            return
        await self._create_case(member.guild, type="autorole", reason=reason, user=member)

    async def _handler_task(self):
        __intervals: List[Tuple[timedelta, int]] = [
            (timedelta(seconds=10), 5),
            (timedelta(minutes=10), 10),
            (timedelta(hours=1), 20),
            (timedelta(days=1), 40),
        ]
        while True:
            member: discord.Member = await self.queue.get()
            await self._wait_for_guild_verification(member, member.guild)
            if member.guild.id not in self.spam:
                self.spam[member.guild.id] = AntiSpam(__intervals)
            if self.spam[member.guild.id].spammy:
                await asyncio.sleep(69)
            self.spam[member.guild.id].stamp()
            await self._handle_member_join(member)

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
    async def remove(self, ctx: commands.GuildContext, *, role: FuzzyRole):
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
    async def _humans(self, _: commands.GuildContext):
        """Manage autoroles for humans."""

    @_humans.command(name="toggle")
    async def humans_toggle(self, ctx: commands.GuildContext, toggle: bool):
        """Toggle the human only autorole system."""
        await self.config.guild(ctx.guild).autoroles.humans.toggle.set(toggle)
        await ctx.send(
            f"Human auto role system is now {'enabled' if toggle else 'disabled'}.",
        )

    @_humans.command(name="add")
    async def humans_add(self, ctx: commands.GuildContext, *, role: StrictRole):
        """Add a role to be added to all new humans on join."""
        async with self.config.guild(ctx.guild).autoroles.humans.roles() as roles:
            if role.id not in roles:
                roles.append(role.id)
            else:
                raise commands.UserFeedbackCheckFailure(
                    f"{role.name} ({role.id}) is already an assigned humans autorole.",
                )
        await ctx.send(f"Assigned {role.name} ({role.id}) as an humans autorole.")

    @_humans.command(name="remove")
    async def humans_remove(self, ctx: commands.Context, *, role: FuzzyRole):
        """Remove an autorole for humans."""
        async with self.config.guild(ctx.guild).autoroles.humans.roles() as roles:
            if role.id in roles:
                roles.remove(role.id)
            else:
                raise commands.UserFeedbackCheckFailure(
                    f"{role.name} ({role.id}) is not an assigned humans autorole.",
                )
        await ctx.send(f"Removed {role.name} ({role.id}) from the humans autorole list.")

    @_autorole.group(name="bots")
    async def _bots(self, ctx: commands.Context):
        """Manage autoroles for bots."""

    @_bots.command(name="toggle")
    async def bots_toggle(self, ctx: commands.GuildContext, toggle: bool):
        """Toggle the bots only autorole system."""
        await self.config.guild(ctx.guild).autoroles.bots.toggle.set(toggle)
        await ctx.send(
            f"Bots auto role system is now {'enabled' if toggle else 'disabled'}.",
        )

    @_bots.command(name="add")
    async def bots_add(self, ctx: commands.Context, *, role: StrictRole):
        """Add a role to be added to all new bots on join."""
        async with self.config.guild(ctx.guild).autoroles.bots.roles() as roles:
            if role.id not in roles:
                roles.append(role.id)
            else:
                raise commands.UserFeedbackCheckFailure(
                    f"{role.name} ({role.id}) is already an assigned bots autorole.",
                )
        await ctx.send(f"Assigned {role.name} ({role.id}) as an bots autorole.")

    @_bots.command(name="remove")
    async def bots_remove(self, ctx: commands.Context, *, role: FuzzyRole):
        """Remove an autorole for bots."""
        async with self.config.guild(ctx.guild).autoroles.bots.roles() as roles:
            if role.id in roles:
                roles.remove(role.id)
            else:
                raise commands.UserFeedbackCheckFailure(
                    f"{role.name} ({role.id}) is not an assigned bots autorole.",
                )
        await ctx.send(f"Removed {role.name} ({role.id}) from the humans autorole list.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.pending:
            return
        await self.queue.put(member)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.pending and not after.pending:
            await self.queue.put(after)
