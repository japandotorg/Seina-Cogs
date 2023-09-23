"""
MIT License

Copyright (c) 2021-2023 aikaterna
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

import re
from typing import Dict, Final, List, Literal, Match, Optional, Pattern, Union

import discord
from red_commons.logging import RedTraceLogger, getLogger
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list
from redbot.core.utils.views import SimpleMenu

log: RedTraceLogger = getLogger("red.seinacogs.antilinks")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

LINKS: Pattern[str] = re.compile(
    r"(\|\|)?(([\w]+:)?\/\/)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,63}(:[\d]+)?(\/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?(\|\|)?"  # type: ignore
)


class AntiLinks(commands.Cog):
    """
    A heavy-handed hammer for anything that looks like a link.
    """

    __author__: Final[List[str]] = ["inthedark.org", "aikaterna"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, identifier=69420, force_registration=True)
        default_guild: Dict[str, Union[Optional[int], List]] = {
            "report_channel": None,
            "role": [],
            "user": [],
            "watching": [],
        }
        self.config.register_guild(**default_guild)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.group(
        name="antilinks",
        aliases=["nolinks", "nolink", "antilink", "alset"],
    )
    async def _anti(self, ctx: commands.Context) -> None:
        """
        Configuration options.
        """

    @_anti.command(name="channel", aliases=["chan"])
    async def _channel(
        self,
        ctx: commands.Context,
        channel: Optional[discord.TextChannel] = None,
    ) -> None:
        """
        Set the message transfer channel.

        Leave the channel blank to turn it off.
        """
        if not channel:
            await self.config.guild(ctx.guild).report_channel.clear()
            await ctx.send("Message transfer channel turned off.")
            return
        await self.config.guild(ctx.guild).report_channel.set(channel.id)
        await ctx.send(f"Message transfer channel set to: {channel.mention}.")

    @_anti.group(name="whitelist")
    async def _whitelist(self, ctx: commands.Context) -> None:
        """
        Whitelist options.
        """

    @_whitelist.group(name="role", invoke_without_command=True)
    async def _whitelist_role(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        roles: commands.Greedy[discord.Role] = None,
    ) -> None:
        """
        Add or remove roles from the whitelist.
        """
        if ctx.invoked_subcommand is None:
            if roles is None:
                await ctx.send("`Roles` is a required argument.")
                return

            async with self.config.guild(ctx.guild).role() as role_list:
                for role in roles:
                    if add_or_remove.lower() == "add":
                        if not role.id in role_list:
                            role_list.append(role.id)
                    elif add_or_remove.lower() == "remove":
                        if role.id in role_list:
                            role_list.remove(role.id)

            ids = len(list(roles))
            await ctx.send(
                f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {ids} {'role' if ids == 1 else 'roles'}."
            )

    @commands.bot_has_permissions(embed_links=True)
    @_whitelist_role.command(name="list", aliases=["view"])
    async def _role_list(self, ctx: commands.Context) -> None:
        """
        List whitelisted roles.
        """
        guild_config = self.config.guild(ctx.guild)
        whitelisted_roles = await guild_config.role()

        if not whitelisted_roles:
            await ctx.send("There are no whitelisted roles in this server.")
            return

        whitelisted = [ctx.guild.get_role(role_id) for role_id in whitelisted_roles]
        whitelisted = [role for role in whitelisted if role is not None]
        whitelisted = sorted(whitelisted, key=lambda x: x.name)

        pages = []
        for index in range(0, len(whitelisted), 10):
            entries = whitelisted[index : index + 10]
            page_content = "\n".join(f"- {role.mention} ({role.id})" for role in entries)
            embed: discord.Embed = discord.Embed(
                title="Whitelisted Roles", description=page_content, color=await ctx.embed_color()
            )
            pages.append(embed)

        await SimpleMenu(pages).start(ctx)

    @_whitelist.group(name="user", invoke_without_command=True)
    async def _whitelist_user(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        members: commands.Greedy[discord.Member] = None,
    ) -> None:
        """
        Add or remove users from the whitelist.
        """
        if ctx.invoked_subcommand is None:
            if members is None:
                await ctx.send("`Members` is a required argument.")
                return

            async with self.config.guild(ctx.guild).user() as user_list:
                for member in members:
                    if add_or_remove.lower() == "add":
                        if not member.id in user_list:
                            user_list.append(member.id)
                    elif add_or_remove.lower() == "remove":
                        if member.id in user_list:
                            user_list.remove(member.id)

            ids = len(list(members))
            await ctx.send(
                f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {ids} {'member' if ids == 1 else 'members'}."
            )

    @commands.bot_has_permissions(embed_links=True)
    @_whitelist_user.command(name="list")
    async def _user_list(self, ctx: commands.Context) -> None:
        """
        List whitelisted users.
        """
        guild_config = self.config.guild(ctx.guild)
        whitelisted_users = await guild_config.user()

        if not whitelisted_users:
            await ctx.send("There are no whitelisted users in this server.")

        whitelisted = [await self.bot.get_or_fetch_user(user_id) for user_id in whitelisted_users]
        whitelisted = [user for user in whitelisted if user is not None]
        whitelisted = sorted(whitelisted, key=lambda x: x.name)

        pages = []
        for index in range(0, len(whitelisted), 10):
            entries = whitelisted[index : index + 10]
            page_content = "\n".join(f"- {user.mention} ({user.id})" for user in entries)
            embed: discord.Embed = discord.Embed(
                title="Whitelisted Users", description=page_content, color=await ctx.embed_color()
            )
            pages.append(embed)

        await SimpleMenu(pages).start(ctx)

    @_anti.group(name="watch", invoke_without_command=True)
    async def _watch(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        channels: commands.Greedy[discord.TextChannel] = None,
    ) -> None:
        """
        Add/remove/list channels to watch.

        - If added, links will be removed in these channels.
        """
        if ctx.invoked_subcommand is None:
            if channels is None:
                await ctx.send("`Channels` is a required argument.")
                return

            async with self.config.guild(ctx.guild).watching() as watching:
                for channel in channels:
                    if add_or_remove.lower() == "add":
                        if not channel.id in watching:
                            watching.append(channel.id)
                    elif add_or_remove.lower() == "remove":
                        if channel.id in watching:
                            watching.remove(channel.id)

            ids = len(list(channels))
            await ctx.send(
                f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} "
                f"{ids} {'channel' if ids == 1 else 'channels'} {'to' if add_or_remove.lower() == 'add' else 'from'} "
                "the channel watch list."
            )

    @commands.bot_has_permissions(embed_links=True)
    @_watch.command(name="list")
    async def _watch_list(self, ctx: commands.Context) -> None:
        """
        List the channels being watched.
        """
        guild_config = self.config.guild(ctx.guild)
        watch_list = await guild_config.watching()

        if not watch_list:
            await ctx.send("No channels being watched at this moment.")
            return

        channel_list = [ctx.guild.get_channel(channel_id) for channel_id in watch_list]
        channel_list = [channel for channel in channel_list if channel is not None]
        channel_list = sorted(channel_list, key=lambda x: x.name)

        pages = []
        for index in range(0, len(channel_list), 10):
            entries = channel_list[index : index + 10]
            page_content = "\n".join(f"{channel.mention} ({channel.id})" for channel in entries)
            embed: discord.Embed = discord.Embed(
                title="AntiLinks Watch List",
                description=page_content,
                color=await ctx.embed_color(),
            )
            pages.append(embed)

        await SimpleMenu(pages).start(ctx)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if isinstance(
            message.channel, (discord.abc.PrivateChannel, discord.ForumChannel, discord.Thread)
        ):
            return

        if message.author.bot:
            return

        data = await self.config.guild(message.guild).all()

        watch_channel_list = data["watching"]
        if not watch_channel_list:
            return

        if message.channel.id not in watch_channel_list:
            return

        if message.author.id in data["user"]:
            return

        allowed_roles = []

        for role in data["role"]:
            whitelist_role = discord.utils.get(message.author.roles, id=role)
            if whitelist_role:
                allowed_roles.append(whitelist_role)

        message_channel = self.bot.get_channel(data["report_channel"])

        if not allowed_roles:
            try:
                sentence = message.content.split()
                for word in sentence:
                    if self._match_url(word):
                        msg = "**Message Removed in** {} ({})\n".format(
                            message.channel.mention, message.channel.id
                        )
                        msg += "**Message sent by**: {} ({})\n".format(
                            message.author.name, message.author.id
                        )
                        msg += "**Message content**:\n- {}".format(message.content)
                        if message_channel:
                            ctx = await self.bot.get_context(message)
                            await ctx.maybe_send_embed(msg)
                        await message.delete()
            except Exception as e:
                if message_channel:
                    await message_channel.send(box(str(e), lang="py"))

    @staticmethod
    def _match_url(url: str) -> Optional[Match[str]]:
        return LINKS.match(url)
