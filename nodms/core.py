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

# flake8: noqa

# the implementation idea of this cog has been taken from the now archived <https://github.com/japandotorg/OB13-Cogs/tree/dpy2/nodms>

import asyncio
import contextlib
import logging
from typing import Any, Dict, Final, List, Literal, Optional, Union, cast

import diot
import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config, Group
from redbot.core.utils.chat_formatting import box, humanize_list, pagify
from redbot.core.utils.views import SimpleMenu

from ._tagscript import (
    BotAdapter,
    CommandAdapter,
    DMChannelAdapter,
    TagScriptConverter,
    UserAdapter,
    command_message,
    message,
    process_tagscript,
)

log: logging.Logger = logging.getLogger("red.seina.nodms.core")


class NoDMs(commands.Cog):
    """
    Restrict messages and/or commands in DMs.

    Restrict messages or any commands in DMs from others, with various
    configuration settings.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, 69_420_666, force_registration=True)
        _default: Dict[
            str,
            Union[
                bool,
                str,
                Literal["all", "messages", "commands"],
                Dict[str, Union[str, bool, List[int], List[str]]],
            ],
        ] = dict(
            type="all",
            toggle=False,
            message=dict(
                toggle=True,
                message=message,
                command=command_message,
            ),
            users=dict(
                whitelist=[],
                blacklist=[],
            ),
            commands=dict(
                whitelist=[],
                blacklist=[],
            ),
        )
        self.config.register_global(**_default)

        self.cache: diot.Diot = diot.Diot(**_default)
        self._cache_ready: asyncio.Event = asyncio.Event()
        self._task: asyncio.Task[None] = asyncio.create_task(self.initialize())

        self.bot.before_invoke(self._before_invoke_hook)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    def get_users_from_cache(
        self, type: Literal["whitelist", "blacklist"]
    ) -> List[Union[str, discord.User]]:
        users: List[Union[str, discord.User]] = []
        if type.lower() == "whitelist":
            if whitelist := cast(List[int], self.cache.users.whitelist):
                for wl in whitelist:
                    if user := self.bot.get_user(wl):
                        users.append(user)
                    else:
                        users.append("Unknown User ({})".format(wl))
            else:
                raise commands.UserFeedbackCheckFailure("There are no users in the whitelist.")
        elif type.lower() == "blacklist":
            if blacklist := cast(List[int], self.cache.users.blacklist):
                for bl in blacklist:
                    if user := self.bot.get_user(bl):
                        users.append(user)
                    else:
                        users.append("Unknown User ({})".format(bl))
            else:
                raise commands.UserFeedbackCheckFailure("There are no users in the blacklist.")
        else:
            raise commands.UserFeedbackCheckFailure(
                "Invalid type, Available: 'whitelist' or 'blacklist'."
            )
        return users

    def get_commands_from_cache(
        self, type: Literal["whitelist", "blacklist"]
    ) -> List[Union[str, commands.Command]]:
        _commands: List[Union[str, commands.Command]] = []
        if type.lower() == "whitelist":
            if whitelist := cast(List[str], self.cache.commands.whitelist):
                for wl in whitelist:
                    if command := self.bot.get_command(wl):
                        _commands.append(command)
                    else:
                        _commands.append("Unknown Command ({})".format(wl))
            else:
                raise commands.UserFeedbackCheckFailure("There are no commands in the whitelist.")
        elif type.lower() == "blacklist":
            if blacklist := cast(List[int], self.cache.commands.whitelist):
                for bl in blacklist:
                    if command := self.bot.get_command(bl):
                        _commands.append(command)
                    else:
                        _commands.append("Unknown Command ({})".format(bl))
            else:
                raise commands.UserFeedbackCheckFailure("There are no commands in the blacklist.")
        else:
            raise commands.UserFeedbackCheckFailure(
                "Invalid type, Available: 'whitelist' or 'blacklist'."
            )
        return _commands

    async def cog_unload(self) -> None:
        if self._task:
            self._task.cancel()
        self.bot.remove_before_invoke_hook(self._before_invoke_hook)

    async def initialize(self) -> None:
        config: Dict[
            str,
            Union[
                bool,
                str,
                Literal["all", "messages", "commands"],
                Dict[str, Union[str, bool, List[int], List[str]]],
            ],
        ] = await self.config.all()
        users: Dict[str, List[int]] = cast(Dict[str, List[int]], config["users"])
        _commands: Dict[str, List[str]] = cast(Dict[str, List[str]], config["commands"])
        message: Dict[str, str] = cast(Dict[str, str], config["message"])
        self.cache.update(
            **dict(
                type=config.get("type", "all"),
                toggle=config.get("toggle", False),
                message=dict(
                    toggle=message.get("toggle", True),
                    message=message.get("message", message),
                    command=message.get("command", command_message),
                ),
                users=dict(
                    whitelist=users.get("whitelist", []),
                    blacklist=users.get("blacklist", []),
                ),
                commands=dict(
                    whitelist=_commands.get("whitelist", []),
                    blacklist=_commands.get("blacklist", []),
                ),
            )
        )
        self._cache_ready.set()

    async def wait_until_cache_ready(self) -> None:
        await self._cache_ready.wait()

    async def _send_response(
        self, ctx: commands.Context, type: Literal["message", "command"]
    ) -> None:
        kwargs: Dict[str, Any] = await process_tagscript(
            (
                self.cache.message.message
                if type.lower() == "message"
                else self.cache.message.command
            ),
            {
                "user": UserAdapter(ctx.author),
                "author": UserAdapter(ctx.author),
                "dm": DMChannelAdapter(ctx.channel),
                "channel": DMChannelAdapter(ctx.channel),
                "bot": BotAdapter(self.bot),
                "{}".format(cast(discord.ClientUser, self.bot.user).name): BotAdapter(self.bot),
                "color": tse.StringAdapter(str(await ctx.embed_color())),
            },
        )
        if type.lower() == "command" and (command := ctx.command):
            kwargs.update(command=CommandAdapter(command))
        if not kwargs:
            if type.lower() == "message":
                await cast(Group, self.config.message).message.clear()
                self.cache.message.update(message=message)
            elif type.lower() == "command":
                await cast(Group, self.config.message).command.clear()
                self.cache.message.update(command=command_message)
            else:
                raise ValueError("Invalid type provided. Available types: 'message' or 'command'.")
            kwargs = await process_tagscript(
                message if type.lower() == "message" else command_message,
                {
                    "user": UserAdapter(ctx.author),
                    "author": UserAdapter(ctx.author),
                    "dm": DMChannelAdapter(ctx.channel),
                    "channel": DMChannelAdapter(ctx.channel),
                    "bot": BotAdapter(self.bot),
                    "{}".format(cast(discord.ClientUser, self.bot.user).name): BotAdapter(
                        self.bot
                    ),
                    "color": tse.StringAdapter(str(await ctx.embed_color())),
                },
            )
            if type.lower() == "command" and (command := ctx.command):
                kwargs.update(command=CommandAdapter(command))
        kwargs["reference"] = ctx.message.to_reference(fail_if_not_exists=False)
        kwargs["allowed_mentions"] = discord.AllowedMentions(replied_user=False)
        try:
            await ctx.send(**kwargs)
        except (discord.Forbidden, discord.HTTPException) as error:
            log.debug("Unable to send dm to {0} {0.id}.".format(ctx.author), exc_info=error)

    async def _before_invoke_hook(self, ctx: commands.Context) -> None:
        await self.wait_until_cache_ready()
        if (
            self.cache.toggle
            and self.cache.type.lower() in ["all", "commands"]
            and isinstance(ctx.channel, discord.DMChannel)
            and not await cast(Red, ctx.bot).is_owner(ctx.author)
            and not isinstance(ctx.command, commands.commands._AlwaysAvailableMixin)
        ):
            if user_wl := self.cache.users.whitelist:
                if ctx.author.id not in user_wl:
                    if self.cache.message.toggle:
                        await self._send_response(ctx, "command")
                    raise commands.CheckFailure()
            elif user_bl := self.cache.users.blacklist:
                if ctx.author.id in user_bl:
                    if self.cache.message.toggle:
                        await self._send_response(ctx, "command")
                    raise commands.CheckFailure()
            else:
                if self.cache.message.toggle:
                    await self._send_response(ctx, "command")
                raise commands.CheckFailure()

            if command_wl := self.cache.commands.whitelist:
                if ctx.command.qualified_name not in command_wl:
                    if self.cache.message.toggle:
                        await self._send_response(ctx, "command")
                    raise commands.CheckFailure()
            elif command_bl := self.cache.commands.blacklist:
                if ctx.command.qualified_name in command_bl:
                    if self.cache.message.toggle:
                        await self._send_response(ctx, "command")
                    raise commands.CheckFailure()
            else:
                if self.cache.message.toggle:
                    await self._send_response(ctx, "command")
                raise commands.CheckFailure()

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        await self.wait_until_cache_ready()
        ctx: commands.Context = cast(commands.Context, await self.bot.get_context(message))
        if message.author.id == ctx.me.id:
            return
        if (
            self.cache.toggle
            and self.cache.type.lower() in ["all", "messages"]
            and isinstance(message.channel, discord.DMChannel)
            and not await cast(Red, ctx.bot).is_owner(message.author)
        ):
            if ctx.command:
                return
            elif whitelist := self.cache.users.whitelist:
                if message.author.id not in whitelist:
                    with contextlib.suppress(discord.HTTPException):
                        await message.delete()
                    if self.cache.message.toggle:
                        await self._send_response(ctx, "message")
            elif blacklist := self.cache.users.blacklist:
                if message.author.id in blacklist:
                    with contextlib.suppress(discord.HTTPException):
                        await message.delete()
                    if self.cache.message.toggle:
                        await self._send_response(ctx, "message")
            else:
                with contextlib.suppress(discord.HTTPException):
                    await message.delete()
                if self.cache.message.toggle:
                    await self._send_response(ctx, "message")

    @commands.is_owner()
    @commands.group(name="nodms")
    async def _no_dms(self, _: commands.Context):
        """
        NoDMs configuration commands.
        """

    @_no_dms.command(name="toggle")  # type: ignore
    async def _no_dms_toggle(
        self,
        ctx: commands.Context,
        true_or_false: bool,
        type: Literal["all", "messages", "commands"],
    ):
        """
        Toggle whether to ignore DM messages and/or commands.

        Enabling the `<type>` argument `all` and `messages`
        will cause botname] to delete messages everytime someone
        DMs [botname]. Unwanted behaviour may occur if
        people try to spam the bot's DMs while these types
        are enabled.

        Message triggers are enabled by default, to disable
        them use the `[p]nodms message toggle <true_or_false>`
        command.

        **Arguments**:
        - `<true_or_false>` - enable/disable nodms for [botname].
        - `<type>` - whether to enable messages, commands or (both) all.
        """
        async with self.config.all() as config:
            config["toggle"] = true_or_false
            config["type"] = type
        self.cache.update(**dict(toggle=true_or_false, type=type))
        await ctx.tick(
            message="{} nodms for {}.".format("Enabled" if true_or_false else "Disabled", type)
        )

    @cast(commands.Group, _no_dms).group(name="message")
    async def _no_dms_message(self, _: commands.Context):
        """
        NoDMs message trigger configuration commands.
        """

    @_no_dms_message.command(name="toggle")
    async def _no_dms_message_toggle(self, ctx: commands.Context, true_or_false: bool):
        """
        Toggle whether to send messages or not.

        **Arguments**:
        - `<true_or_false>` - enable/disable message triggers for nodms.
        """
        await cast(Group, self.config.message).toggle.set(true_or_false)
        self.cache.message.update(**dict(toggle=True))
        await ctx.tick(
            message="{} nodms messages.".format("Enabled" if true_or_false else "Disabled")
        )

    @_no_dms_message.command(name="set", aliases=["configure"])
    async def _no_dms_message_set(
        self,
        ctx: commands.Context,
        type: Literal["messages", "commands", "clear"],
        *,
        argument: Optional[TagScriptConverter] = None,
    ):
        """
        Configure the nodms message trigger.

        **Arguments**:
        - `<type>    `: whether to configure message for messages, commands or clear
        the already configured type, using clear will reset both the messages
        trigger and commands trigger to default.
        - `<argument>`: the message to be sent by [botname], if argument is not
        privided the type is reset to default instead.

        **Blocks**:
        `embed` - [Embed to be sent for the trigger message](https://seina-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#embed-block)

        **Variables**:
        - `{color}  `: [botname]'s default embed color (no parameters).
            - usage: `{color}`
        - `{bot}    `: custom block for [botname] variables.
            - parameters: `id`, `name`, `nick`, `mention`, `avatar`, `created_at` or
            `verified`.
            - aliases: `{[botname]}`
            - usage: `{command(<parameter>)}`
        - `{user}   `: the user to dm [botname].
            - parameters: `id`, `created_at`, `timestamp`, `name`, `nick`,  `avatar`
            or `mention` (if no parameter is used, defaults to `name`).
            - aliases: `{author}`
            - usage: `{user(<parameter>)}`
        - `{channel}`: [botname]'s dm channel with the user/author.
            - parameters: `id`, `created_at` or `jump_url` (if no parameter is used,
            defaults to `jump_url`).
            - aliases: `{dm}`
            - usage: `{channel(<parameter>)}`
        - `{command}`: the command that was blocked, this block is only available
            when the "commands" type is used.
            - parameters: `name`, `cog_name`, `description`, `aliases` or
            `qualified_name` (if no parameter is used, defaults to `qualified_name`).
            - usage: `{command(<parameter>)}`

        **Examples**:
        - `[p]nodms message set commands {embed(description):You're not allowed to use the {command(name)} command in {bot(name)}'s dms.}`
        - `[p]nodms message set message {embed(description):You're not allowed to send messages in {bot(name)}'s dms.}`
        - `[p]nodms message set commands You're not allowed to use the {command(name)} command in {bot(name)}'s dms.`
        - `[p]nodms message set message You're not allowed to send messages in {bot(name)}'s dms.`
        """
        if type.lower() == "clear":
            if argument:
                raise commands.UserFeedbackCheckFailure(
                    "Please do not provide `<argument>` when using the clear type."
                )
            await self.config.message.clear()
            self.cache.message.update(**dict(message=message, command=command_message))
            await ctx.send(
                (
                    "The nodms messages were reverted to default.\n\n"
                    "Message Trigger: {}\n"
                    "Command Trigger: {}\n"
                ).format(
                    box(message, lang="json"),
                    box(command_message, lang="json"),
                )
            )
        elif type.lower() == "messages":
            if argument:
                await cast(Group, self.config.message).message.set(argument)
                self.cache.message.update(**dict(message=argument))
                await ctx.send(
                    "Successfully changed the message trigger.\n{}".format(
                        box(str(argument), lang="json")
                    )
                )
            else:
                await cast(Group, self.config.message).message.clear()
                self.cache.message.update(**dict(message=message))
                await ctx.send(
                    "The nodms message trigger was reverted to default.\n{}".format(
                        box(message, lang="json")
                    )
                )
        else:
            if argument:
                await cast(Group, self.config.message).command.set(argument)
                self.cache.message.update(**dict(command=argument))
                await ctx.send(
                    "Successfully changed the command trigger.\n{}".format(
                        box(str(argument), lang="json")
                    )
                )
            else:
                await cast(Group, self.config.message).command.clear()
                self.cache.message.update(**dict(command=command_message))
                await ctx.send(
                    "The nodms command trigger was reverted to default.\n{}".format(
                        box(message, lang="json")
                    )
                )

    @cast(commands.Group, _no_dms).group(name="whitelist", aliases=["wl", "allowlist"])
    async def _no_dms_whitelist(self, _: commands.Context):
        """
        Configure the whitelist for nodms.

        Warning: When the whitelist is in use, [botname] will ignore all
        users/commands not in the list.

        View the list using the `[p]nodms whitelist list <users/commands>` command,
        and/or make sure to remove everyone from the list to disable the whitelist.
        """

    @_no_dms_whitelist.command(name="users", aliases=["user"], require_var_positional=True)
    async def _no_dms_whitelist_users(
        self, ctx: commands.Context, add_or_remove: Literal["add", "remove"], *users: discord.User
    ):
        """
        Add or remove users from the whitelist.

        **Arguments**:
        - `<add_or_remove>`: add or remove users from the whitelist.
        - `<users>        `: list of users to be added/removed.
        """
        async with cast(Group, self.config.users).whitelist() as wl:
            for user in users:
                if add_or_remove.lower() == "add":
                    if user.id not in wl:
                        wl.append(user.id)
                elif add_or_remove.lower() == "remove":
                    if user.id in wl:
                        wl.remove(user.id)
            self.cache.users.update(**dict(whitelist=wl))

        await ctx.send(
            "Successfully {} {} roles to the whitelist.".format(
                "added" if add_or_remove.lower() == "add" else "removed", len(users)
            ),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_no_dms_whitelist.command(name="commands", aliases=["command"], require_var_positional=True)
    async def _no_dms_whitelist_commands(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        *commands: commands.CommandConverter,
    ):
        """
        Add or remove commands from the whitelist.

        **Arguments**:
        - `<add_or_remove>`: add or remove commands from the whitelist.
        - `<commands>     `: list of command names to be added/removed.
        """
        async with cast(Group, self.config.commands).whitelist() as wl:
            for command in commands:
                if add_or_remove.lower() == "add":
                    if command.qualified_name not in wl:
                        wl.append(command.qualified_name)
                elif add_or_remove.lower() == "remove":
                    if command.qualified_name in wl:
                        wl.remove(command.qualified_name)
            self.cache.commands.update(**dict(whitelist=wl))

        await ctx.send(
            "Successfully {} {} commands to the whitelist.".format(
                "added" if add_or_remove.lower() == "add" else "removed", len(commands)
            ),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_no_dms_whitelist.command(name="list")
    @commands.bot_has_permissions(embed_links=True)
    async def _not_dms_whitelist_list(
        self, ctx: commands.Context, option: Literal["users", "commands"]
    ):
        """
        View the whitelisted user/command list.

        **Arguments**:
        - `<option>`: whether to view the users or commands list.
        """
        async with ctx.typing():
            if option.lower() == "users":
                elements: List[str] = [
                    "{0.mention} ({0.id})".format(user) if isinstance(user, discord.User) else user
                    for user in self.get_users_from_cache("whitelist")
                ]
            else:
                elements: List[str] = [
                    "{}".format(
                        (
                            command.qualified_name
                            if isinstance(command, commands.Command)
                            else command
                        )
                        for command in self.get_commands_from_cache("whitelist")
                    )
                ]
            string: str = "\n".join(elements)
            embeds: List[discord.Embed] = []
            for page in pagify(string, delims=[" ", "\n"]):
                embeds.append(
                    discord.Embed(
                        color=await ctx.embed_color(),
                        title=(
                            "User Whitelist" if option.lower() == "users" else "Command Whitelist"
                        ),
                        description=page,
                    )
                )
        await SimpleMenu(embeds, disable_after_timeout=True).start(ctx)

    @cast(commands.Group, _no_dms).group(name="blacklist", aliases=["bl", "blocklist"])
    async def _no_dms_blacklist(self, _: commands.Context):
        """
        Configure the blacklist for nodms.

        View the list using the `[p]nodms blacklist list <users/commands>` command,
        and/or make sure to remove everyone from the list to disable the blacklist.
        """

    @_no_dms_blacklist.command(name="users", aliases=["user"], require_var_positional=True)
    async def _no_dms_blacklist_users(
        self, ctx: commands.Context, add_or_remove: Literal["add", "remove"], *users: discord.User
    ):
        """
        Add or remove users from the blacklist.

        **Arguments**:
        - `<add_or_remove>`: add or remove users from the blacklist.
        - `<users>        `: list of users to be added/removed.
        """
        async with cast(Group, self.config.users).blacklist() as bl:
            for user in users:
                if add_or_remove.lower() == "add":
                    if user.id not in bl:
                        bl.append(user.id)
                elif add_or_remove.lower() == "remove":
                    if user.id in bl:
                        bl.remove(user.id)
            self.cache.users.update(**dict(blacklist=bl))

        await ctx.send(
            "Successfully {} {} roles to the blacklist.".format(
                "added" if add_or_remove.lower() == "add" else "removed", len(users)
            ),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_no_dms_blacklist.command(name="commands", aliases=["command"], require_var_positional=True)
    async def _no_dms_blacklist_commands(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        *commands: commands.CommandConverter,
    ):
        """
        Add or remove commands from the blacklist.

        **Arguments**:
        - `<add_or_remove>`: add or remove commands from the blacklist.
        - `<commands>     `: list of command names to be added/removed.
        """
        async with cast(Group, self.config.commands).blacklist() as bl:
            for command in commands:
                if add_or_remove.lower() == "add":
                    if command.qualified_name not in bl:
                        bl.append(command.qualified_name)
                elif add_or_remove.lower() == "remove":
                    if command.qualified_name in bl:
                        bl.remove(command.qualified_name)
            self.cache.commands.update(**dict(blacklist=bl))

        await ctx.send(
            "Successfully {} {} commands to the blacklist.".format(
                "added" if add_or_remove.lower() == "add" else "removed", len(commands)
            ),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_no_dms_blacklist.command(name="list")
    @commands.bot_has_permissions(embed_links=True)
    async def _not_dms_blacklist_list(
        self, ctx: commands.Context, option: Literal["users", "commands"]
    ):
        """
        View the blacklisted user/command list.

        **Arguments**:
        - `<option>`: whether to view the users or commands list.
        """
        async with ctx.typing():
            if option.lower() == "users":
                elements: List[str] = [
                    "{0.mention} ({0.id})".format(user) if isinstance(user, discord.User) else user
                    for user in self.get_users_from_cache("blacklist")
                ]
            else:
                elements: List[str] = [
                    "{}".format(
                        (
                            command.qualified_name
                            if isinstance(command, commands.Command)
                            else command
                        )
                        for command in self.get_commands_from_cache("blacklist")
                    )
                ]
            string: str = "\n".join(elements)
            embeds: List[discord.Embed] = []
            for page in pagify(string, delims=[" ", "\n"]):
                embeds.append(
                    discord.Embed(
                        color=await ctx.embed_color(),
                        title=(
                            "User Blacklist" if option.lower() == "users" else "Command Blacklist"
                        ),
                        description=page,
                    )
                )
        await SimpleMenu(embeds, disable_after_timeout=True).start(ctx)

    @commands.bot_has_permissions(embed_links=True)
    @cast(commands.Group, _no_dms).command(name="settings", aliases=["showsettings", "show", "ss"])
    async def _no_dms_settings(self, ctx: commands.Context):
        """View the NoDMs configuration settings."""
        embed: discord.Embed = discord.Embed(
            title="NoDMs Settings",
            color=await ctx.embed_color(),
            description="**Toggle**: {}\n**Type**: {}\n**Messages**: {}".format(
                "Enabled" if self.cache.toggle else "Disabled",
                self.cache.type,
                "Enabled" if self.cache.message.toggle else "Disabled",
            ),
        )
        embed.add_field(
            name="Message Trigger",
            value=box(self.cache.message.message, lang="json"),
            inline=False,
        )
        embed.add_field(
            name="Command Trigger",
            value=box(self.cache.message.command, lang="json"),
            inline=False,
        )
        embed.set_thumbnail(url=cast(discord.ClientUser, self.bot.user).display_avatar.url)
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
