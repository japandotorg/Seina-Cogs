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

from __future__ import annotations

import asyncio
from typing import Any, Dict, Literal

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import pagify
from redbot.core.utils.predicates import MessagePredicate

from .abc import CompositeMetaClass, MixinMeta


class Commands(MixinMeta, metaclass=CompositeMetaClass):
    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.bot_has_permissions(ban_members=True, kick_members=True)
    @commands.group(name="modmanager", aliases=["mm", "mmanager", "manager"])  # type: ignore
    async def _mod_manager(self, _: commands.GuildContext):
        """Mod Manager Commands."""

    @_mod_manager.command(name="toggle")  # type: ignore
    async def _toggle(self, ctx: commands.GuildContext, toggle: bool):
        """Toggle Mod Manager."""
        await self.config.guild(ctx.guild).toggle.set(toggle)
        await ctx.send(
            f"Mod Manager is now {'enabled' if toggle else 'disabled'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_mod_manager.command(name="modlog")  # type: ignore
    async def _modlog(self, ctx: commands.GuildContext, toggle: bool):
        """Toggle the Mod Manager modlogs."""
        await self.config.guild(ctx.guild).modlog.set(toggle)
        await ctx.send(
            f"Mod Manager modlog is now {'enabled' if toggle else 'disabled'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_mod_manager.group(name="force")  # type: ignore
    async def _force(self, _: commands.GuildContext):
        """Force add users to the ban or kick list."""

    @_force.command(name="ban")  # type: ignore
    async def _ban(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        users: commands.Greedy[commands.RawUserIdConverter],
        *,
        reason: str = "No reason provided.",
    ):
        """Force add users to the ban list."""
        if add_or_remove.lower() == "add":
            await self.manager._add_to_ban_list(users, ctx.guild, reason)  # type: ignore
        elif add_or_remove.lower() == "remove":
            if not await self.manager._get_ban_list(ctx.guild):
                await ctx.send(
                    "There are no users in the ban list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            await self.manager._remove_from_ban_list(users, ctx.guild)  # type: ignore
        else:
            await ctx.send_help(ctx.command)
            return
        await ctx.send(
            f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {len(users)} users.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_force.command(name="kick")  # type: ignore
    async def _kick(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove", "clear"],
        users: commands.Greedy[commands.RawUserIdConverter],
        *,
        reason: str = "No reason provided.",
    ):
        """Force add users to the kick list."""
        if add_or_remove.lower() == "add":
            await self.manager._add_to_kick_list(users, ctx.guild, reason)  # type: ignore
        elif add_or_remove.lower() == "remove":
            if not await self.manager._get_kick_list(ctx.guild):
                await ctx.send(
                    "There are no users in the kick list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            await self.manager._remove_from_kick_list(users, ctx.guild)  # type: ignore
        else:
            await ctx.send_help(ctx.command)
            return
        await ctx.send(
            f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {len(users)} users.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_mod_manager.command(name="list")  # type: ignore
    async def _list(
        self,
        ctx: commands.GuildContext,
        ban_or_kick: Literal["ban", "kick"],
    ):
        """Showcase the ban or kick list."""
        if ban_or_kick.lower() == "ban":
            if not (ban_list := await self.manager._get_ban_list(ctx.guild)):
                await ctx.send(
                    "There are no users in the ban list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            message: str = "Ban List:"
            for key, value in ban_list.items():
                name: str = (
                    u.name if (u := self.bot.get_user(int(key))) else "Unknown/Deleted User"
                )
                message += f"\n\t- [{key}] {name}: {value}"
            await ctx.send_interactive(pagify(message, page_length=1800), "yml")
        elif ban_or_kick.lower() == "kick":
            if not (kick_list := await self.manager._get_kick_list(ctx.guild)):
                await ctx.send(
                    "There are no users in the kick list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            message: str = "Kick List:"
            for key, value in kick_list.items():
                name: str = (
                    u.name if (u := self.bot.get_user(int(key))) else "Unknown/Deleted User"
                )
                message += f"\n\t- [{key}] {name}: {value}"
            await ctx.send_interactive(pagify(message, page_length=1800), "yml")
        else:
            await ctx.send_help(ctx.command)

    @_mod_manager.command(name="reason")  # type: ignore
    async def _reason(
        self,
        ctx: commands.GuildContext,
        ban_or_kick: Literal["ban", "kick"],
        user: discord.User,
        *,
        reason: str,
    ):
        """Change the ban or kick reason."""
        if ban_or_kick.lower() == "ban":
            if not await self.manager._in_ban_list(user.id, ctx.guild):
                await ctx.send(
                    "That user is not in the ban list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            try:
                await self.manager._edit_ban_reason(user, reason, guild=ctx.guild)
            except KeyError:
                await ctx.send(
                    "That user was not in the ban list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            await ctx.send(
                "Done. Edited the reason for that user.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        elif ban_or_kick.lower() == "kick":
            if not await self.manager._in_kick_list(user.id, ctx.guild):
                await ctx.send(
                    "That user is not in the kick list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            try:
                await self.manager._edit_kick_reason(user, reason, guild=ctx.guild)
            except KeyError:
                await ctx.send(
                    "That user was not in the kick list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            await ctx.send(
                "Done. Edited the reason for that user.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        else:
            await ctx.send_help(ctx.command)

    @_mod_manager.command(name="clear")  # type: ignore
    async def _clear(self, ctx: commands.GuildContext, ban_or_kick: Literal["ban", "kick"]):
        """Clear the ban or kick list."""
        if ban_or_kick.lower() == "ban":
            await ctx.send(
                "Would you like to clear the ban list? (y/n)",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            predicate: MessagePredicate = MessagePredicate.yes_or_no(ctx)
            try:
                await self.bot.wait_for("message", check=predicate, timeout=60.0)
            except asyncio.TimeoutError:
                await ctx.send(
                    "Confirmation timed out.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            if not predicate.result:
                await ctx.send(
                    "Okay, I won't clear the ban list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            await self.manager._clear_ban_list(ctx.guild)
            await ctx.send(
                "Cleared the ban list.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        elif ban_or_kick.lower() == "kick":
            await ctx.send(
                "Would you like to clear the kick list? (y/n)",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            predicate: MessagePredicate = MessagePredicate.yes_or_no(ctx)
            try:
                await self.bot.wait_for("message", check=predicate, timeout=60.0)
            except asyncio.TimeoutError:
                await ctx.send(
                    "Confirmation timed out.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            if not predicate.result:
                await ctx.send(
                    "Okay, I won't clear the kick list.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
            await self.manager._clear_kick_list(ctx.guild)
            await ctx.send(
                "Cleared the kick list.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        else:
            await ctx.send_help(ctx.command)

    @_mod_manager.command(name="settings", aliases=["show", "showsettings"])  # type: ignore
    async def _settings(self, ctx: commands.GuildContext):
        """Show the Mod Manager settings."""
        config: Dict[str, Any] = await self.config.guild(ctx.guild).all()
        embed: discord.Embed = discord.Embed(
            title="Mod Manager Settings",
            description=f"Mod Manager is {'enabled' if config['toggle'] else 'disabled'}.",
            color=await ctx.embed_color(),
        )
        embed.add_field(name="Modlogs", value=config["modlog"], inline=True)
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
