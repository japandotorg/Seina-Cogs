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

import io
import re
from typing import Any, Dict, Final, List, Literal, Match, Optional, Union

import discord
from red_commons.logging import RedTraceLogger, getLogger
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list

log: RedTraceLogger = getLogger("red.seinacogs.antilinks")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

LINKS = re.compile(
    "(\|\|)?(([\w]+:)?\/\/)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,63}(:[\d]+)?(\/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?(\|\|)?"  # type: ignore
)


class AntiLinks(commands.Cog):
    """
    A heavy-handed hammer for anything that looks like a link.
    """

    __author__: Final[List[str]] = ["inthedark.org", "aikaterna"]
    __version__: Final[str] = "0.1.0"

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

    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, io.BytesIO]:
        """
        Nothing to delete
        """
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"User_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, io.BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Optional[int] = kwargs.get("user_id")
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

    @commands.guild_only()
    @commands.mod_or_permissions(administrator=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.group(
        name="antilinks", aliases=["nolinks", "nolink", "antilink", "alset"],
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

    @_whitelist.group(name="role")
    async def _whitelist_role(self, ctx: commands.Context) -> None:
        """
        Whitelist roles.
        """

    @_whitelist_role.command(name="add", aliases=["+", "create"])
    async def _role_add(self, ctx: commands.Context, *, role_name: discord.Role) -> None:
        """
        Add a role to the whitelist.
        """
        role_list = await self.config.guild(ctx.guild).role()
        if role_name.id not in role_list:
            role_list.append(role_name.id)
        else:
            await ctx.send("Role already whitelisted.")
            return
        await self.config.guild(ctx.guild).role.set(role_list)
        await ctx.send(f"{role_name.name} appended to the role whitelist.")

    @_whitelist_role.command(name="remove", aliases=["-", "delete"])
    async def _role_remove(self, ctx: commands.Context, *, role_name: discord.Role) -> None:
        """
        Remove a role from the whitelist.
        """
        role_list = await self.config.guild(ctx.guild).role()
        if role_name.id in role_list:
            role_list.remove(role_name.id)
        else:
            await ctx.send("Role not whitelisted.")
            return
        await self.config.guild(ctx.guild).role.set(role_list)
        await ctx.send(f"{role_name.name} removed from the role whitelist.")

    @_whitelist_role.command(name="list", aliases=["view"])
    async def _role_list(self, ctx: commands.Context) -> None:
        """
        List whitelisted roles.
        """
        role_list = await self.config.guild(ctx.guild).role()
        role_msg = "Whitelisted Roles:\n"
        if not role_list:
            role_msg += "No roles."
        for role in role_list:
            role_obj = discord.utils.get(ctx.guild.roles, id=role)
            role_msg += f"- {role_obj.name}\n"
        await ctx.send(box(role_msg, lang="md"))

    @_whitelist.group(name="user")
    async def _whitelist_user(self, ctx: commands.Context) -> None:
        """
        Whitelist users.
        """

    @_whitelist_user.command(name="add", aliases=["+", "create"])
    async def _user_add(self, ctx: commands.Context, *, user: discord.Member) -> None:
        """
        Add a user to the whitelist.
        """
        user_list = await self.config.guild(ctx.guild).user()
        if user.id not in user_list:
            user_list.append(user.id)
        else:
            await ctx.send("User already whitelisted.")
            return
        await self.config.guild(ctx.guild).user.set(user_list)
        await ctx.send(f"{user.display_name} appended to the user whitelist.")

    @_whitelist_user.command(name="remove", aliases=["-", "delete"])
    async def _user_remove(self, ctx: commands.Context, user: discord.Member) -> None:
        """
        Remove a user from the whitelist
        """
        user_list = await self.config.guild(ctx.guild).user()
        if user.id in user_list:
            user_list.remove(user.id)
        else:
            await ctx.send("User not whitelisted.")
            return
        await self.config.guild(ctx.guild).user.set(user_list)
        await ctx.send(f"{user.display_name} removed from the user whitelist.")

    @_whitelist_user.command(name="list")
    async def _user_list(self, ctx: commands.Context) -> None:
        """
        List whitelisted users.
        """
        user_list = await self.config.guild(ctx.guild).user()
        user_msg = "Whitelisted Users:\n"
        if not user_list:
            user_msg += "No users."
        for user in user_list:
            user_obj = discord.utils.get(ctx.guild.members, id=user)
            user_msg += f"- {user_obj.display_name}\n"
        await ctx.send(box(user_msg, lang="md"))

    @_anti.group(name="watch")
    async def _watch(self, ctx: commands.Context) -> None:
        """
        Add/remove/list channels to watch.

        - If added, links will be removed in these channels.
        """

    @_watch.command(name="add", aliases=["+", "create"])
    async def _watch_add(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        Add a channel to watch.
        """
        channel_list = await self.config.guild(ctx.guild).watching()
        if channel.id not in channel_list:
            channel_list.append(channel.id)
        else:
            await ctx.send("Already watching the channel.")
            return
        await self.config.guild(ctx.guild).watching.set(channel_list)
        await ctx.send(f"{channel.mention} will have links removed.")

    @_watch.command(name="remove", aliases=["-", "delete"])
    async def _watch_remove(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        Remove a channel from watch.
        """
        channel_list = await self.config.guild(ctx.guild).watching()
        if channel.id in channel_list:
            channel_list.remove(channel.id)
        else:
            await ctx.send("Channel is not being watched.")
            return
        await self.config.guild(ctx.guild).watching.set(channel_list)
        await ctx.send(f"{channel.mention} will not have links removed.")

    @_watch.command(name="list")
    async def _watch_list(self, ctx: commands.Context) -> None:
        """
        List the channels being watched.
        """
        channel_list = await self.config.guild(ctx.guild).watching()
        msg = "Links will be removed in:\n"
        if not channel_list:
            msg += "No channels."
        else:
            remove_list = []
            for channel in channel_list:
                channel_obj = self.bot.get_channel(channel)
                if not channel_obj:
                    remove_list.append(channel)
                else:
                    msg += f"- {channel_obj.mention}\n"
            if remove_list:
                new_list = [x for x in channel_list if x not in remove_list]
                await self.config.guild(ctx.guild).watching.set(new_list)
                if len(remove_list) == len(channel_list):
                    msg += "No channels."
        await ctx.send(box(msg, lang="md"))

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
                            embed: discord.Embed = discord.Embed(
                                description=msg,
                                color=await ctx.embed_color(),
                            )
                            await message_channel.send(embed=embed)
                        await message.delete()
            except Exception as e:
                if message_channel:
                    await message_channel.send(box(str(e), lang="py"))

    @staticmethod
    def _match_url(url: str) -> Optional[Match[str]]:
        return LINKS.match(url)
