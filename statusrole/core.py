"""
MIT License

Copyright (c) 2021-2023 Obi-Wan3
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

import io
import re
from collections import defaultdict
from typing import Any, Dict, Final, List, Literal, Match, Tuple

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class StatusRole(commands.Cog):
    """
    Roles for Certain Custom Statuses.

    Assign roles to users for the duration in which they have certain custom statuses.
    """

    __author__: Final[List[str]] = ["Obi-Wan3", "inthedark.org#0666"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            None,
            identifier=69420,
            force_registration=True,
            cog_name="StatusRole",
        )
        default_guild: Dict[str, Any] = {
            "roles": {},
            "channel": None,
            "blacklist": [],
        }
        self.blacklist: defaultdict[Any, List[str]] = defaultdict(lambda: [])
        self.config.register_guild(**default_guild)
        self.bot.loop.create_task(self.initialize(self.bot))

    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, io.BytesIO]:
        """
        Nothing to delete.
        """
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, io.BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Any = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def initialize(self, bot: Red) -> None:
        await bot.wait_until_red_ready()
        for guild in bot.guilds:
            await self._update_cache(guild)

    async def _update_cache(self, guild: discord.Guild):
        self.blacklist[guild] = await self.config.guild(guild).blacklist()

    @commands.Cog.listener("on_member_update")
    async def _member_update_listener(self, before: discord.Member, after: discord.Member) -> None:
        if (
            before.bot
            or after.id in self.blacklist[after.guild]  # Member is a bot
            or await self.bot.cog_disabled_in_guild(self, before.guild)
            or not after.guild.me.guild_permissions.manage_roles  # Cog disabled in guild
            or before.activity == after.activity  # Cannot manage roles  # Activity did not change
        ):
            return

        can_embed = False
        log_channel = await self.config.guild(before.guild).channel()
        if log_channel:
            log_channel: discord.TextChannel | None = before.guild.get_channel(log_channel)
            perms = log_channel.permissions_for(after.guild.me)
            if not perms.send_messages:
                log_channel = None
            else:
                if perms.embed_links:
                    can_embed = True

        async with self.config.guild(before.guild).roles() as status_roles:
            for name, sr in status_roles.items():
                if not sr["toggle"]:
                    continue

                role = before.guild.get_role(sr["role"])
                before_status = await self._custom_activity(before.activities)
                after_status = await self._custom_activity(after.activities)

                # Role hierarchy check
                if not role or role >= after.guild.me.top_role:
                    continue

                # Now have custom status (did not have before)
                if not before_status and after_status:
                    if await self._status_matches(
                        sr["status"], sr["emoji"], after_status, after.guild
                    ):
                        await self._maybe_add_role(after, role, name)
                        if log_channel:
                            await self._send_log(
                                log_channel,
                                True,
                                after,
                                role,
                                after_status.name,
                                after_status.emoji.name if after_status.emoji else "None",
                                can_embed,
                            )

                # Had custom status (does not anymore)
                elif before_status and not after_status:
                    if await self._status_matches(
                        sr["status"], sr["emoji"], before_status, after.guild
                    ):
                        await self._maybe_remove_role(after, role, name)
                        if log_channel:
                            await self._send_log(
                                log_channel, False, after, role, "None", "None", can_embed
                            )

                # Custom status changed
                elif before_status and after_status and before_status != after_status:
                    before_match = await self._status_matches(
                        sr["status"], sr["emoji"], before_status, after.guild
                    )
                    after_match = await self._status_matches(
                        sr["status"], sr["emoji"], after_status, after.guild
                    )

                    if not before_match and after_match:
                        await self._maybe_add_role(after, role, name)
                        if log_channel:
                            await self._send_log(
                                log_channel,
                                True,
                                after,
                                role,
                                after_status.name,
                                after_status.emoji.name if after_status.emoji else "None",
                                can_embed,
                            )

                    elif before_match and not after_match:
                        await self._maybe_remove_role(after, role, name)
                        if log_channel:
                            await self._send_log(
                                log_channel,
                                False,
                                after,
                                role,
                                after_status.name,
                                after_status.emoji.name if after_status.emoji else "None",
                                can_embed,
                            )

    @staticmethod
    async def _maybe_add_role(member: discord.Member, role: discord.Role, name: str) -> None:
        if role not in member.roles:
            await member.add_roles(role, reason=f"StatusRole: new custom status matched {name}")

    @staticmethod
    async def _maybe_remove_role(member: discord.Member, role: discord.Role, name: str) -> None:
        if role in member.roles:
            await member.remove_roles(
                role, reason=f"StatusRole: custom status no longer matches {name}"
            )

    @staticmethod
    async def _custom_activity(
        activities: Tuple[discord.activity.ActivityTypes, ...]
    ) -> discord.CustomActivity | None:
        for act in activities:
            if isinstance(act, discord.CustomActivity):
                return act
        return None

    @staticmethod
    async def _status_matches(
        st: Any,
        em: Any,
        user_status: discord.CustomActivity,
        guild: discord.Guild,
    ):
        status = user_status.name
        emoji = user_status.emoji

        if (not st and not em) or (not status and not emoji):
            return False

        async def _st_match(r: Any, s: str | None) -> Match[str] | bool | None:
            if not r:
                return True
            else:
                if not s:
                    return False
                try:
                    pattern = "|".join(rf"(\s|^){re.escape(word)}(\s|$)" for word in r)
                    return re.search(pattern, s, flags=re.I)
                except re.error:
                    return False

        async def _em_match(r: Any, e: discord.PartialEmoji | None) -> bool | None:
            if not r:
                return True
            else:
                if not e:
                    return False
                else:
                    if r is True:
                        if e.is_custom_emoji() and e.id in [
                            emoji.id for emoji in guild.emojis
                        ]:  # Emoji in guild
                            return True
                    elif e.is_custom_emoji() and r[1] == e.id:  # Custom emoji matches
                        return True
                    elif e.is_unicode_emoji() and r[0] == e.name:  # Default emoji matches
                        return True

        return await _st_match(st, status) and (await _em_match(em, emoji))

    @staticmethod
    async def _send_log(
        channel: discord.TextChannel,
        assign: bool,
        user: discord.Member,
        role: discord.Role,
        status: str | None,
        emoji: str | None,
        can_embed: bool,
    ):
        embed: discord.Embed = discord.Embed(title=f"StatusRole `{role.name}`")
        embed.add_field(name="Member", value=user.mention)
        embed.add_field(name="New Status", value=f"`{status}`")
        embed.add_field(name="New Emoji", value=f"`{emoji}`")

        # Role assigned
        if assign:
            embed.title += "Added"
            embed.color = discord.Color.green()
            plaintext = f"StatusRole: {user.mention} custom status changed to `{status}` with emoji `{emoji}`, {role.mention} assigned"

        # Role removed
        else:
            embed.title += "Removed"
            embed.color = discord.Color.red()
            plaintext = f"StatusRole: {user.mention} custom status changed to `{status}` with emoji `{emoji}`, {role.mention} removed"

        if can_embed:
            await channel.send(embed=embed)
        else:
            await channel.send(plaintext)

    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    @commands.group(name="statusrole")
    async def _status_role(self, ctx: commands.Context):
        """StatusRole Settings"""

    @_status_role.command(name="logchannel")
    async def _log_channel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Set the StatusRole log channel (leave blank to disable logs)."""
        await self.config.guild(ctx.guild).channel.set(channel.id if channel else None)
        return await ctx.tick()

    @_status_role.command(name="add")
    async def _add(
        self, ctx: commands.Context, pair_name: str, role: discord.Role, *statuses_to_match: str
    ):
        """Add a role to be assigned to users with any of the input status(es) (list of words separated by spaces)."""
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("That role is above you in the role hierarchy!")

        async with self.config.guild(ctx.guild).roles() as roles:
            if pair_name in roles.keys():
                return await ctx.send(
                    "There is already a StatusRole with this name! Please edit/delete it or choose another name."
                )
            roles[pair_name] = {
                "role": role.id,
                "emoji": None,
                "status": statuses_to_match,
                "toggle": True,
            }
        return await ctx.send(
            f"`{role.name}` will now be assigned to users with any emoji and status matching any of the following words: {humanize_list([f'`{s}`' for s in statuses_to_match])}."
        )

    @_status_role.group(name="edit")
    async def _edit(self, ctx: commands.Context):
        """Edit a StatusRole"""

    @_edit.command(name="role")
    async def _edit_role(self, ctx: commands.Context, pair_name: str, role: discord.Role):
        """Edit a StatusRole's role to be assigned."""
        async with self.config.guild(ctx.guild).roles() as roles:
            if pair_name not in roles.keys():
                return await ctx.send("There is no StatusRole with this name!")
            roles[pair_name]["role"] = role.id
        return await ctx.tick()

    @_edit.command(name="emoji")
    async def _edit_emoji(
        self,
        ctx: commands.Context,
        pair_name: str,
        emoji: discord.PartialEmoji | bool | str | None = None,
    ):
        """Edit a StatusRole's required emoji (you can also enter True for any emoji in this server, or leave blank to remove)."""
        async with self.config.guild(ctx.guild).roles() as roles:
            if pair_name not in roles.keys():
                return await ctx.send("There is no StatusRole with this name!")
            if type(emoji) == bool:
                if emoji:
                    roles[pair_name]["emoji"] = True
                else:
                    return await ctx.send(
                        "Please enter `True` if you would like the StatusRole to match any emoji in this server. Otherwise, leave this field blank or input a specific emoji."
                    )
            elif isinstance(emoji, discord.PartialEmoji):
                roles[pair_name]["emoji"] = (emoji.name, emoji.id)
            elif emoji:
                roles[pair_name]["emoji"] = (emoji, None)
            else:
                roles[pair_name]["emoji"] = None
        return await ctx.tick()

    @_edit.command(name="status")
    async def _edit_status(self, ctx: commands.Context, pair_name: str, *statuses_to_match: str):
        """Edit a StatusRole's status(es) to be matched (list of words separated by spaces, leave blank to remove text status matching)."""
        async with self.config.guild(ctx.guild).roles() as roles:
            if pair_name not in roles.keys():
                return await ctx.send("There is no StatusRole with this name!")
            roles[pair_name]["status"] = statuses_to_match
        return await ctx.tick()

    @_edit.command(name="toggle")
    async def _edit_toggle(self, ctx: commands.Context, pair_name: str, true_or_false: bool):
        """Toggle a StatusRole assignment temporarily."""
        async with self.config.guild(ctx.guild).roles() as roles:
            if pair_name not in roles.keys():
                return await ctx.send("There is no StatusRole with this name!")
            roles[pair_name]["toggle"] = true_or_false
        return await ctx.tick()

    @_status_role.command(name="remove", aliases=["delete"])
    async def _remove(self, ctx: commands.Context, pair_name: str, enter_true_to_confirm: bool):
        """Remove a StatusRole from being assigned."""
        if not enter_true_to_confirm:
            return await ctx.send("Please provide `true` as the parameter to confirm.")

        async with self.config.guild(ctx.guild).roles() as roles:
            if pair_name not in roles.keys():
                return await ctx.send("There is no StatusRole with this name!")
            del roles[pair_name]
        return await ctx.tick()

    @commands.bot_has_permissions(manage_roles=True)
    @_status_role.command(name="forcecheck", require_var_positional=True)
    async def _force_update(self, ctx: commands.Context, *statusroles: str):
        """Force a manual check of every user on this server for the provided StatusRoles."""

        async with ctx.typing():
            can_embed = False
            log_channel = await self.config.guild(ctx.guild).channel()
            if log_channel:
                log_channel: discord.TextChannel | None = ctx.guild.get_channel(log_channel)
                perms = log_channel.permissions_for(ctx.guild.me)
                if not perms.send_messages:
                    log_channel = None
                else:
                    if perms.embed_links:
                        can_embed = True

            async with self.config.guild(ctx.guild).roles() as roles:
                for sr in statusroles:
                    if sr not in roles.keys():
                        await ctx.send(f"Skipping `{sr}` as there no StatusRole with that name.")
                        statusroles.remove(sr)

                members = ctx.guild.members
                await ctx.send(
                    f"Updating `{len(statusroles)}` StatusRoles for all `{len(members)}` members in the server, this may take a while..."
                )
                for m in members:
                    m_status = await self._custom_activity(m.activities)
                    if m_status:
                        for sr in statusroles:
                            if not roles[sr]["toggle"]:
                                await ctx.send(f"Skipping `{sr}` as it is toggled off.")
                                continue

                            r = (
                                ctx.guild.get_role(roles[sr]["role"])
                                if roles[sr]["role"]
                                else None
                            )
                            if not r or r >= ctx.guild.me.top_role:
                                continue

                            if await self._status_matches(
                                roles[sr]["status"], roles[sr]["emoji"], m_status, ctx.guild
                            ):
                                await self._maybe_add_role(m, r, sr)
                                if log_channel:
                                    await self._send_log(
                                        log_channel,
                                        True,
                                        m,
                                        r,
                                        m_status.name,
                                        m_status.emoji.name if m_status.emoji else "None",
                                        can_embed,
                                    )
                            else:
                                await self._maybe_remove_role(m, r, sr)
                                if log_channel:
                                    await self._send_log(
                                        log_channel,
                                        False,
                                        m,
                                        r,
                                        m_status.name,
                                        m_status.emoji.name if m_status.emoji else "None",
                                        can_embed,
                                    )

        return await ctx.send("Force update completed!")

    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    @_status_role.group(name="blacklist", aliases=["blocklist"])
    async def _blacklist(self, ctx: commands.Context):
        """
        Manage statusrole blacklist.
        """
        if ctx.invoked_subcommand is None:
            pass

    @_blacklist.command(name="add", aliases=["+", "create"])
    async def _blacklist_add(self, ctx: commands.Context, user: discord.Member):
        """
        Add a user to the status role blacklist.
        """
        async with self.config.guild(ctx.guild).blacklist() as blacklist:
            if not user.id in blacklist:
                blacklist.append(user.id)
                await ctx.tick()
            else:
                await ctx.send("User is already blacklisted.")
        await self._update_cache(ctx.guild)

    @_blacklist.command(name="remove", aliases=["-", "delete"])
    async def _blacklist_remove(self, ctx: commands.Context, user: discord.Member):
        """
        Remove a user from the status role blacklist.
        """
        async with self.config.guild(ctx.guild).blacklist() as blacklist:
            try:
                blacklist.remove(user.id)
                await ctx.tick()
            except ValueError:
                await ctx.send("User not blacklisted.")
            finally:
                await self._update_cache(ctx.guild)

    @_blacklist.command(name="list", aliases=["view"])
    async def _blacklist_list(self, ctx: commands.Context):
        for user_id in await self.config.guild(ctx.guild).blacklist():
            user = ctx.guild.get_member(user_id)
            embed: discord.Embed = discord.Embed(
                title="Blacklist List",
                description=f"{user.display_name} | {user.name}#{user.discriminator}({user.id})",
                color=await ctx.embed_color(),
            )
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @_status_role.command(name="view", aliases=["list"])
    async def _view(self, ctx: commands.Context):
        """View the StatusRole settings for this server."""
        settings = await self.config.guild(ctx.guild).all()

        logchannel = None
        if settings["channel"] and (ch := ctx.guild.get_channel(settings["channel"])):
            logchannel = ch.mention

        embed = discord.Embed(
            title="StatusRole Settings",
            color=await ctx.embed_color(),
            description=f"Log Channel: {logchannel}",
        )

        for name, statusrole in settings["roles"].items():
            embed.add_field(
                name=name,
                value=f"""
                **Role:** {ctx.guild.get_role(statusrole["role"]).mention if ctx.guild.get_role(statusrole["role"]) else None}
                **Emoji:** {("Any in Server" if statusrole["emoji"] is True else statusrole["emoji"][0]) if statusrole["emoji"] else "Any"}
                **Status:** {humanize_list([f'`{s}`' for s in statusrole["status"]]) if statusrole["status"] else None}
                **Toggle:** {statusrole["toggle"]}
                """,
            )
        await ctx.send(embed=embed)
