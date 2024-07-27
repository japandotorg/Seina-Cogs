"""
MIT License

Copyright (c) 2021-present Kuro-Rui

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

from typing import Dict, List, Literal, Optional, Union, cast

import discord
from redbot.core import commands
from redbot.core.config import Group
from redbot.core.utils.views import SimpleMenu
from redbot.core.utils.chat_formatting import box, humanize_list, pagify

import TagScriptEngine as tse

from ._tagscript import TagScriptConverter, DefaultNameConverter
from .abc import CompositeMetaClass, MixinMeta


class Commands(MixinMeta, metaclass=CompositeMetaClass):
    @commands.guild_only()
    @commands.group(name="threadopener")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.bot_has_permissions(manage_threads=True, create_public_threads=True)
    async def _thread_opener(self, _: commands.GuildContext):
        """Manage ThreadOpener settings."""

    @_thread_opener.command(name="toggle")
    async def _toggle(self, ctx: commands.GuildContext, true_or_false: bool):
        """
        Toggle ThreadOpener enable or disable.
        """
        await self.config.guild(ctx.guild).toggle.set(true_or_false)
        await ctx.send(f"Thread opener is now {'enabled' if true_or_false else 'disabled'}.")

    @_thread_opener.command(name="channels", aliases=["channel"])
    async def _channels(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        channels: commands.Greedy[discord.TextChannel],
    ):
        """
        Add or remove channels for your guild.

        **Arguments:**
        - `<add_or_remove>` should be either `add` to add channels or `remove` to remove channels.
        - `<channels>` channels to be added.

        **Example:**
        - `[p]threadopener channels add #channel`
        - `[p]threadopener channels remove #channel`

        **Note:**
        - You can add or remove multiple channels at once.
        - You can also use channel ID instead of mentioning the channel.
        """
        async with self.config.guild(ctx.guild).channels() as c:
            for channel in channels:
                if add_or_remove.lower() == "add":
                    if channel.id not in c:
                        c.append(channel.id)
                elif add_or_remove.lower() == "remove":
                    if channel.id in c:
                        c.remove(channel.id)

        channels: int = len(channels)

        await ctx.send(
            f"{'Added' if add_or_remove.lower() == 'add' else 'Removed'} "
            f"{channels} {'channel' if channels == 1 else 'channels'}."
        )

    @_thread_opener.group(name="blacklist", aliases=["bl"])
    async def _blacklist(self, _: commands.GuildContext):
        """
        Base command for Thread Opener blacklists.

        **Commands:**
        - `[p]threadopener blacklist users <add_or_remove> <users>`
        - `[p]threadopener blacklist roles <add_or_remove> <roles>`
        """

    @_blacklist.command(name="users", aliases=["user", "members", "member"])
    async def _blacklist_users(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        users: commands.Greedy[discord.User],
    ):
        """
        Add or remove users for your guild's blacklist.

        **Arguments:**
        - `<add_or_remove>` should be either `add` to add users or `remove` to remove users.
        - `<users>` users to be added.

        **Example:**
        - `[p]threadopener blacklist users add @inthedark.org`
        - `[p]threadopener blacklist users remove @inthedark.org`

        **Note:**
        - You can add or remove multiple users at once.
        - You can also use user ID instead of mentioning the user.
        """
        async with cast(Group, self.config.guild(ctx.guild).blacklist).users() as bl:
            for user in users:
                if add_or_remove.lower() == "add":
                    if user.id not in bl:
                        bl.append(user.id)
                elif add_or_remove.lower() == "remove":
                    if user.id in bl:
                        bl.remove(user.id)

        users: int = len(users)

        await ctx.send(
            f"{'Added' if add_or_remove.lower() == 'add' else 'Removed'} "
            f"{users} {'user' if users == 1 else 'users'}."
        )

    @_thread_opener.command(name="roles", aliases=["role"])
    async def _blacklist_roles(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        roles: commands.Greedy[discord.Role],
    ):
        """
        Add or remove roles for your guild's blacklist.

        **Arguments:**
        - `<add_or_remove>` should be either `add` to add roles or `remove` to remove roles.
        - `<users>` roles to be added.

        **Example:**
        - `[p]threadopener blacklist roles add @members`
        - `[p]threadopener blacklist roles remove @members`

        **Note:**
        - You can add or remove multiple roles at once.
        - You can also use role ID instead of mentioning the role.
        """
        async with cast(Group, self.config.guild(ctx.guild).blacklist).roles() as bl:
            for role in roles:
                if add_or_remove.lower() == "add":
                    if role.id not in bl:
                        bl.append(role.id)
                elif add_or_remove.lower() == "remove":
                    if role.id in bl:
                        bl.remove(role.id)

        roles: int = len(roles)

        await ctx.send(
            f"{'Added' if add_or_remove.lower() == 'add' else 'Removed'} "
            f"{roles} {'role' if roles == 1 else 'roles'}."
        )

    @_thread_opener.command(name="list")
    async def _blacklist_list(
        self, ctx: commands.GuildContext, users_or_roles: Literal["users", "roles"] = "users"
    ):
        """
        View the blacklist.

        **Arguments:**
        ` `<users_or_roles>` should be either ``users`` to view the user blacklist
            or `roles` to view the role blacklist.
        """
        config: Dict[str, List[int]] = await self.config.guild(ctx.guild).blacklist()
        if users_or_roles.lower() == "users":
            if not (users := config["users"]):
                raise commands.UserFeedbackCheckFailure("There are no users in the blacklist.")
            description: str = "\n".join(
                [
                    (
                        f"\t- [{idx + 1}] {u.name} (`{u.id}`)"
                        if (u := self.bot.get_user(user))
                        else f"\t- Unknown/Deleted User (`{user}`)"
                    )
                    for idx, user in enumerate(users)
                ]
            )
            pages: List[str] = list(pagify(description))
            embeds: List[discord.Embed] = []
            for idx, page in enumerate(pages):
                embed: discord.Embed = discord.Embed(
                    title="User Blacklist",
                    description=page,
                    color=await ctx.embed_color(),
                )
                embed.set_footer(text="Page {}/{}".format(idx + 1, len(pages)))
                embeds.append(embed)
            await SimpleMenu(embeds, disable_after_timeout=True).start(ctx)
        elif users_or_roles.lower() == "roles":
            if not (roles := config["roles"]):
                raise commands.UserFeedbackCheckFailure("There are no roles in the blacklist.")
            description: str = "\n".join(
                [
                    (
                        f"\t - [{idx + 1}] {r.name} (`{r.id}`)"
                        if (r := ctx.guild.get_role(role))
                        else f"\t- Unknown/Deleted Role (`{role}`)"
                    )
                    for idx, role in enumerate(roles)
                ]
            )
            pages: List[str] = list(pagify(description))
            embeds: List[discord.Embed] = []
            for idx, page in enumerate(pages):
                embed: discord.Embed = discord.Embed(
                    title="Role Blacklist",
                    description=page,
                    color=await ctx.embed_color(),
                )
                embed.set_footer(text="Page {}/{}".format(idx + 1, len(pages)))
                embeds.append(embed)
            await SimpleMenu(embeds, disable_after_timeout=True).start(ctx)

    @_thread_opener.command(name="archive")
    async def _archive(
        self, ctx: commands.GuildContext, amount: Literal[0, 60, 1440, 4320, 10080]
    ):
        """
        Change the archive duration of threads.

        - Use `0` to disable auto archive duration of threads.
        """
        if amount == 0:
            await self.config.guild(ctx.guild).auto_archive_duration.clear()
            await ctx.send("Disabled auto archive duration.")
            return
        await self.config.guild(ctx.guild).auto_archive_duration.set(amount)
        await ctx.send(f"Auto archive duration is now {amount}.")

    @_thread_opener.command(name="slowmode", aliases=["slow"])
    async def _slowmode(self, ctx: commands.GuildContext, amount: commands.Range[int, 0, 21600]):
        """
        Change the slowmode of threads.

        - Use `0` to dsiable slowmode delay in threads.
        """
        if amount == 0:
            await self.config.guild(ctx.guild).slowmode_delay.clear()
            await ctx.send("Disabled slowmode on opening threads.")
        await self.config.guild(ctx.guild).slowmode_delay.set(amount)
        await ctx.send(f"Slowmode is now {amount}.")

    @_thread_opener.command(name="name", aliases=["defaultname", "default", "dn"])
    async def _name(
        self, ctx: commands.GuildContext, *, tagscript: Optional[DefaultNameConverter] = None
    ):
        """
        Change the default thread name for ThreadOpener.

        (Supports TagScript)

        **Attributes:**
        - `{server}`: [Your guild/server.](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#server-block)
        - `{author}`: [Author of the thread.](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#author-block)
        - `{created}`: Formatted time string of when the thread was created.
        - `{counter}`: Counter of how created thread. (Everytime a thread is created using ThreadOpener the counter goes up by 1.)

        **Example:**
        - `[p]threadopener name {author(name)}:{created}:{counter}`
        - `[p]threadopener name {author(name)}-{counter}`
        """
        if not tagscript:
            await self.config.guild(ctx.guild).default_thread_name.clear()
            await ctx.send("Successfully reset the default thread name.")
            return
        try:
            formatted: str = self.format_thread_name(ctx.author, formatting=tagscript, counter=1)
        except tse.TagScriptError:
            raise commands.BadArgument(
                "Something is wrong with your tagscript, please fix and retry again."
            )
        await self.config.guild(ctx.guild).default_thread_name.set(tagscript)
        await ctx.send(
            "Successfully changed the default name tagscript to - \n\n"
            + "Tagscript: {} \n".format(box(str(tagscript), lang="json"))
            + "Formatted Example: {} \n".format(box(str(formatted), lang="json"))
        )

    @_thread_opener.group(name="message")
    async def _message(self, _: commands.GuildContext):
        """
        Manage thread opener notifications when they are opened.
        """

    @_message.command(name="toggle")
    async def _message_toggle(self, ctx: commands.GuildContext, true_or_false: bool):
        """Toggle the thread opener notification message."""
        await self.config.guild(ctx.guild).message_toggle.set(true_or_false)
        await ctx.send(
            f"ThreadOpener notifications are now {'enabled' if true_or_false else 'disabled'}."
        )

    @_message.command(name="buttons")
    async def _buttons(self, ctx: commands.GuildContext, true_or_false: bool):
        """
        Toggle buttons from the thread opener notification message. (Enabled by default.)
        """
        await cast(Group, self.config.guild(ctx.guild).buttons).toggle.set(true_or_false)
        await ctx.send(
            f"Thread opener buttons are now {'enabled' if true_or_false else 'disabled'}."
        )

    @_message.command(name="set")
    async def _message_set(
        self,
        ctx: commands.GuildContext,
        *,
        message: Optional[TagScriptConverter] = None,
    ):
        """
        Change the thread opener notification message.

        (Supports Tagscript)

        **Blocks:**
        - [Assugnment Block](https://seina-cogs.readthedocs.io/en/latest/tags/tse_blocks.html#assignment-block)
        - [If Block](https://seina-cogs.readthedocs.io/en/latest/tags/tse_blocks.html#if-block)
        - [Embed Block](https://seina-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#embed-block)
        - [Command Block](https://seina-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#command-block)

        **Variable:**
        - `{server}`: [Your guild/server.](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#server-block)
        - `{author}`: [Author of the message.](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#author-block)
        - `{color}`: [botname]'s default color.

        **Example:**
        ```
        {embed(description):Welcome to the thread.}
        {embed(thumbnail):{member(avatar)}}
        {embed(color):{color}}
        ```
        """
        if message:
            await self.config.guild(ctx.guild).message.set(message)
            await ctx.send(
                "Successfully changed the thread opener notification message. {}".format(
                    box(str(message), lang="json")
                )
            )
        else:
            await self.config.guild(ctx.guild).message.clear()
            await ctx.send("Successfully reset the thread opener notification message.")

    @_thread_opener.command(name="showsettings", aliases=["ss", "show"])
    async def _show_settings(self, ctx: commands.GuildContext):
        """Show ThreadOpener settings."""
        data: Dict[str, Union[List[int], bool, Optional[int], str, Dict[str, bool]]] = (
            await self.config.guild(ctx.guild).all()
        )
        active_channels: List[str] = []
        for cid in cast(List[int], data["channels"]):
            channel = ctx.guild.get_channel(cid)
            if not channel:
                async with self.config.guild(ctx.guild).channels() as channels:
                    channels.remove(cid)
                continue
            active_channels.append(channel.mention)
        embed: discord.Embed = discord.Embed(
            title="ThreadOpener Settings",
            description=(
                f"ThreadOpener is currently "
                f"**{'enabled' if data['toggle'] else 'disabled'}**.\n"
                f"Threads created using ThreadOpener - {data['counter']}."
            ),
            color=await ctx.embed_color(),
        )
        embed.add_field(
            name="Auto Archive Duration",
            value=data["auto_archive_duration"],
        )
        embed.add_field(name="Slowmode Delay", value=data["slowmode_delay"])
        embed.add_field(
            name="Default Thread Name",
            value=box(str(data["default_thread_name"]), lang="json"),
            inline=False,
        )
        embed.add_field(
            name=f"Message Toggle: {data['message_toggle']}",
            value=box(str(data["message"]), lang="json"),
            inline=False,
        )
        if active_channels and len(active_channels) > 0:
            embed.add_field(
                name="Active Channels",
                value=humanize_list(active_channels)[:2000],
                inline=False,
            )
        await ctx.send(embed=embed)
