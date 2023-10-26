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

from copy import copy
from typing import Final, List, Literal, Optional, Union, TypeAlias, Tuple, Any

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, inline
from redbot.core.utils.mod import get_audit_reason

from .converters import ChannelToggle, LockableChannel, LockableRole

RequestType: TypeAlias = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class Lock(commands.Cog):
    """
    Advanced channel and server locking.
    """

    __author__: Final[List[str]] = ["inthedark.org", "Phenom4n4n"]
    __version__: Final[str] = "1.1.5"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @staticmethod
    def update_overwrite(
        ctx: commands.Context, overwrite: discord.PermissionOverwrite, permissions: dict
    ) -> Tuple[discord.PermissionOverwrite, List[Any], str, List[str]]:
        base_perms = dict(iter(discord.PermissionOverwrite()))
        old_perms = copy(permissions)
        ctx.channel.permissions_for(ctx.author)  # type: ignore
        invalid_perms = []
        valid_perms = []
        not_allowed: List[str] = []
        for perm in old_perms:
            if perm in base_perms:
                valid_perms.append(f"`{perm}`")
            else:
                invalid_perms.append(f"`{perm}`")
                del permissions[perm]
        overwrite.update(**permissions)
        if invalid_perms:
            invalid = (
                f"\nThe following permissions were invalid:\n{humanize_list(invalid_perms)}\n"
            )
            possible = humanize_list([f"`{perm}`" for perm in base_perms])
            invalid += f"Possible permissions are:\n{possible}"
        else:
            invalid = ""
        return overwrite, valid_perms, invalid, not_allowed

    @commands.bot_has_permissions(manage_roles=True)
    @commands.admin_or_permissions(manage_roles=True)
    @commands.group(name="lock", invoke_without_command=True)
    async def _lock(
        self,
        ctx: commands.Context,
        channel: Optional[Union[LockableChannel, discord.VoiceChannel]] = None,
        roles_or_members: commands.Greedy[Union[LockableRole, discord.Member]] = None,  # type: ignore
    ):
        """
        Lock a channel.

        Provide a role or member if you would like to lock it for them.
        You can only lock a maximum of 10 things at once.

        **Examples:**
        - `[p]lock #testing`
        - `[p]lock 133251234164375552 @members`
        """
        try:
            await ctx.typing()
        except discord.Forbidden:
            return

        if not channel:
            channel = ctx.channel  # type: ignore
        if not roles_or_members:
            roles_or_members = [ctx.guild.default_role]  # type: ignore
        else:
            roles_or_members = roles_or_members[:10]  # type: ignore
        succeeded = []
        cancelled = []
        failed = []
        reason = get_audit_reason(ctx.author)  # type: ignore

        if isinstance(channel, discord.TextChannel):
            for role in roles_or_members:
                current_perms = channel.overwrites_for(role)  # type: ignore
                my_perms = channel.overwrites_for(ctx.me)
                if my_perms.send_messages != True:
                    my_perms.update(send_messages=True)
                    await channel.set_permissions(ctx.me, overwrite=my_perms)  # type: ignore
                if current_perms.send_messages == False:
                    cancelled.append(inline(role.name))  # type: ignore
                else:
                    current_perms.update(send_messages=False)
                    try:
                        await channel.set_permissions(role, overwrite=current_perms, reason=reason)  # type: ignore
                        succeeded.append(inline(role.name))  # type: ignore
                    except:
                        failed.append(inline(role.name))  # type: ignore
        elif isinstance(channel, discord.VoiceChannel):
            for role in roles_or_members:
                current_perms = channel.overwrites_for(role)  # type: ignore
                if current_perms.connect == False:
                    cancelled.append(inline(role.name))  # type: ignore
                else:
                    current_perms.update(connect=False)
                    try:
                        await channel.set_permissions(role, overwrite=current_perms, reason=reason)  # type: ignore
                        succeeded.append(inline(role.name))  # type: ignore
                    except:
                        failed.append(inline(role.name))  # type: ignore

        msg = ""
        if succeeded:
            msg += f"{channel.mention} has been locked for {humanize_list(succeeded)}.\n"  # type: ignore
        if cancelled:
            msg += f"{channel.mention} was already locked for {humanize_list(cancelled)}.\n"  # type: ignore
        if failed:
            msg += f"I failed to lock {channel.mention} for {humanize_list(failed)}.\n"  # type: ignore
        if msg:
            await ctx.send(msg)

    @_lock.command(name="server")  # type: ignore
    async def _lock_server(self, ctx: commands.Context, *roles: LockableRole):
        """
        Lock the server.

        Provide a role if you would like to lock if for that role.

        **Example:**
        - `[p]lock server @members`
        """
        if not roles:
            roles = [ctx.guild.default_role]  # type: ignore
        succeeded = []
        cancelled = []
        failed = []

        for role in roles:
            current_perms = role.permissions  # type: ignore
            if ctx.guild.me.top_role <= role:  # type: ignore
                failed.append(inline(role.name))  # type: ignore
            elif current_perms.send_messages == False:
                cancelled.append(inline(role.name))  # type: ignore
            else:
                current_perms.update(send_messages=False)
                try:
                    await role.edit(permissions=current_perms)  # type: ignore
                    succeeded.append(inline(role.name))  # type: ignore
                except:
                    failed.append(inline(role.name))  # type: ignore
        if succeeded:
            await ctx.send(f"The server has locked for {humanize_list(succeeded)}.")
        if cancelled:
            await ctx.send(f"The server was already locked for {humanize_list(cancelled)}.")
        if failed:
            await ctx.send(
                f"I failed to lock the server for {humanize_list(failed)}, probably because I was lower than the roles in heirarchy."
            )

    @commands.bot_has_permissions(manage_roles=True)
    @commands.admin_or_permissions(manage_roles=True)
    @commands.group(name="unlock", invoke_without_command=True)
    async def _unlock(
        self,
        ctx: commands.Context,
        channel: Optional[Union[LockableChannel, discord.VoiceChannel]] = None,
        state: Optional[ChannelToggle] = None,
        roles_or_members: commands.Greedy[Union[LockableRole, discord.Member]] = None,  # type: ignore
    ):
        """
        Unlock a channel.

        Provide a role or member if you would like to unlock it for them.
        If you would like to override-unlock for something, you can do so by pass `true` as the state argument.
        You can only unlock a maximum of 10 things at once.

        **Examples:**
        - `[p]unlock #testing`
        - `[p]unlock 133251234164375552 true`
        """
        try:
            await ctx.typing()
        except discord.Forbidden:
            return

        if not channel:
            channel = ctx.channel  # type: ignore
        if roles_or_members:
            roles_or_members = roles_or_members[:10]  # type: ignore
        else:
            roles_or_members = [ctx.guild.default_role]  # type: ignore
        succeeded = []
        cancelled = []
        failed = []
        reason = get_audit_reason(ctx.author)  # type: ignore

        if isinstance(channel, discord.TextChannel):
            for role in roles_or_members:
                current_perms = channel.overwrites_for(role)  # type: ignore
                if current_perms.send_messages != False and current_perms.send_messages == state:
                    cancelled.append(inline(role.name))  # type: ignore
                else:
                    current_perms.update(send_messages=state)  # type: ignore
                    try:
                        await channel.set_permissions(role, overwrite=current_perms, reason=reason)  # type: ignore
                        succeeded.append(inline(role.name))  # type: ignore
                    except:
                        failed.append(inline(role.name))  # type: ignore
        elif isinstance(channel, discord.VoiceChannel):
            for role in roles_or_members:
                current_perms = channel.overwrites_for(role)  # type: ignore
                if current_perms.connect in [False, state]:
                    current_perms.update(connect=state)  # type: ignore
                    try:
                        await channel.set_permissions(role, overwrite=current_perms, reason=reason)  # type: ignore
                        succeeded.append(inline(role.name))  # type: ignore
                    except:
                        failed.append(inline(role.name))  # type: ignore
                else:
                    cancelled.append(inline(role.name))  # type: ignore

        msg = ""
        if succeeded:
            msg += f"{channel.mention} has unlocked for {humanize_list(succeeded)} with state `{'true' if state else 'default'}`.\n"  # type: ignore
        if cancelled:
            msg += f"{channel.mention} was already unlocked for {humanize_list(cancelled)} with state `{'true' if state else 'default'}`.\n"  # type: ignore
        if failed:
            msg += f"I failed to unlock {channel.mention} for {humanize_list(failed)}.\n"  # type: ignore
        if msg:
            await ctx.send(msg)

    @_unlock.command(name="server")  # type: ignore
    async def _unlock_server(self, ctx: commands.Context, *roles: LockableRole):
        """
        Unlock the server.

        Provide a role if you would unlock it for that role.

        **Examples:**
        - `[p]unlock server @members`
        """
        if not roles:
            roles = [ctx.guild.default_role]  # type: ignore
        succeeded = []
        cancelled = []
        failed = []

        for role in roles:
            current_perms = role.permissions  # type: ignore
            if ctx.guild.me.top_role <= role:  # type: ignore
                failed.append(inline(role.name))  # type: ignore
            elif current_perms.send_messages == True:
                cancelled.append(inline(role.name))  # type: ignore
            else:
                current_perms.update(send_messages=True)
                try:
                    await role.edit(permissions=current_perms)  # type: ignore
                    succeeded.append(inline(role.name))  # type: ignore
                except:
                    failed.append(inline(role.name))  # type: ignore

        msg = []
        if succeeded:
            msg.append(f"The server has unlocked for {humanize_list(succeeded)}.")
        if cancelled:
            msg.append(f"The server was already unlocked for {humanize_list(cancelled)}.")
        if failed:
            msg.append(
                f"I failed to unlock the server for {humanize_list(failed)}, probably because I was lower than the roles in heirarchy."
            )
        if msg:
            await ctx.send("\n".join(msg))

    @commands.bot_has_permissions(manage_roles=True)
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command(name="viewlock")
    async def _viewlock(
        self,
        ctx: commands.Context,
        channel: Optional[Union[LockableChannel, discord.VoiceChannel]] = None,
        roles_or_members: commands.Greedy[Union[LockableRole, discord.Member]] = None,  # type: ignore
    ):
        """
        Prevent users from viewing a channel.

        Provide a role or member if you would like to lock it for them.
        You can only lock a maximum of 10 things at once.

        **Example:**
        - `[p]viewlock #testing`
        - `[p]viewlock 133251234164375552 @nubs`
        """
        try:
            await ctx.typing()
        except discord.Forbidden:
            return

        if not channel:
            channel = ctx.channel  # type: ignore
        if not roles_or_members:
            roles_or_members = [ctx.guild.default_role]  # type: ignore
        else:
            roles_or_members = roles_or_members[:10]  # type: ignore
        succeeded = []
        cancelled = []
        failed = []
        reason = get_audit_reason(ctx.author)  # type: ignore

        for role in roles_or_members:
            current_perms = channel.overwrites_for(role)  # type: ignore
            if current_perms.read_messages == False:
                cancelled.append(inline(role.name))  # type: ignore
            else:
                current_perms.update(read_messages=False)
                try:
                    await channel.set_permissions(role, overwrite=current_perms, reason=reason)  # type: ignore
                    succeeded.append(inline(role.name))  # type: ignore
                except:
                    failed.append(inline(role.name))  # type: ignore

        msg = ""
        if succeeded:
            msg += f"{channel.mention} has been viewlocked for {humanize_list(succeeded)}.\n"  # type: ignore
        if cancelled:
            msg += f"{channel.mention} was already viewlocked for {humanize_list(cancelled)}.\n"  # type: ignore
        if failed:
            msg += f"I failed to viewlock {channel.mention} for {humanize_list(failed)}.\n"  # type: ignore
        if msg:
            await ctx.send(msg)

    @commands.bot_has_permissions(manage_roles=True)
    @commands.admin_or_permissions(manage_roles=True)
    @commands.command(name="unviewlock", invoke_without_command=True)
    async def _unviewlock(
        self,
        ctx: commands.Context,
        channel: Optional[Union[LockableChannel, discord.VoiceChannel]] = None,
        state: Optional[ChannelToggle] = None,
        roles_or_members: commands.Greedy[Union[LockableRole, discord.Member]] = None,  # type: ignore
    ):
        """
        Allow users to view a channel.

        Provide a role or member if you would like to unlock it for them.
        If you would like to override-unlock for something, you can do so by pass `true` as the state argument.
        You can only unlock a maximum of 10 things at once.

        **Example:**
        - `[p]unviewlock #testing true`
        - `[p]unviewlock 133251234164375552 @boosters`
        """
        try:
            await ctx.typing()
        except discord.Forbidden:
            return

        if not channel:
            channel = ctx.channel  # type: ignore
        if not roles_or_members:
            roles_or_members = [ctx.guild.default_role]  # type: ignore
        else:
            roles_or_members = roles_or_members[:10]  # type: ignore
        succeeded = []
        cancelled = []
        failed = []
        reason = get_audit_reason(ctx.author)  # type: ignore

        for role in roles_or_members:
            current_perms = channel.overwrites_for(role)  # type: ignore
            if current_perms.read_messages != False and current_perms.read_messages == state:
                cancelled.append(inline(role.name))  # type: ignore
            else:
                current_perms.update(read_messages=state)  # type: ignore
                try:
                    await channel.set_permissions(role, overwrite=current_perms, reason=reason)  # type: ignore
                    succeeded.append(inline(role.name))  # type: ignore
                except:
                    failed.append(inline(role.name))  # type: ignore

        msg = ""
        if succeeded:
            msg += f"{channel.mention} has unlocked viewing for {humanize_list(succeeded)} with state `{'true' if state else 'default'}`.\n"  # type: ignore
        if cancelled:
            msg += f"{channel.mention} was already unviewlocked for {humanize_list(cancelled)} with state `{'true' if state else 'default'}`.\n"  # type: ignore
        if failed:
            msg += f"I failed to unlock {channel.mention} for {humanize_list(failed)}.\n"  # type: ignore
        if msg:
            await ctx.send(msg)
