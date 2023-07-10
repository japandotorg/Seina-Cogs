"""
MIT License

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

# The idea of this whole cog is taken from https://github.com/fixator10/Fixator10-Cogs/tree/V3/personalroles

import asyncio
import io
from textwrap import shorten
from typing import Dict, Final, List, Literal, Optional, Union

import discord
from discord.ext.commands._types import Check
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import box, humanize_list, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.mod import get_audit_reason
from redbot.core.utils.predicates import MessagePredicate
from tabulate import tabulate

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


def has_assigned_channel() -> Check[commands.Context]:
    async def _predicate(ctx: commands.Context):
        if not ctx.guild:
            return False
        channel_id = await ctx.cog.config.member(ctx.author).channel()
        channel = ctx.guild.get_channel(channel_id)
        return channel is not None

    return commands.check(_predicate)


class PositionConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        try:
            position = int(argument)
        except ValueError:
            raise commands.BadArgument("The position must be an integer.")
        max_guild_text_channels_position = len(
            [c for c in ctx.guild.channels if isinstance(c, discord.TextChannel)]
        )
        if position <= 0 or position >= max_guild_text_channels_position + 1:
            raise commands.BadArgument(
                f"The indicated position must be between 1 and {max_guild_text_channels_position}."
            )
        position -= 1
        return position


class PersonalChannels(commands.Cog):
    """
    Assign and edit personal channels.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=69420, force_registration=True)
        default_member: Dict[str, Union[Optional[int], List[int]]] = {
            "channel": None,
            "permission": None,
            "friends": [],
        }
        default_guild: Dict[str, Union[List[int], Optional[int]]] = {
            "blacklist": [],
            "category": None,
        }
        self.config.register_member(**default_member)
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

    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Optional[Union[Dict, Dict[str, io.BytesIO]]]:
        data = await self.config.all_members()
        async for guild_id, members in AsyncIter(data.items()):
            for user_id in members:
                if config := await self.config.member_from_ids(guild_id, user_id).all():
                    return config
                else:
                    data = "No data is stored for user with ID {}.\n".format(user_id)
                    return {"user_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        data = await self.config.all_members()
        async for guild_id, members in AsyncIter(data.items()):
            if user_id in members:
                await self.config.member_from_ids(guild_id, user_id).clear()

    def get_category(self, category_id: int) -> discord.CategoryChannel:
        category = self.bot.get_channel(category_id)
        return category

    async def check_text_channels(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> bool:
        if not channel.permissions_for(ctx.me).manage_channels:
            raise commands.UserFeedbackCheckFailure(
                f"I can not edit the text channel {channel.mention} ({channel.id}) because I do not have the `manage_channel` permission."
            )
        return True

    @commands.guild_only()
    @commands.group(name="mychannel", aliases=["mychan"])
    async def _my_channel(self, ctx: commands.Context):
        """
        Control of personal channels.
        """

    @_my_channel.command()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def assign(
        self, ctx: commands.Context, user: discord.Member, *, channel: discord.TextChannel
    ):
        """
        Assign a personal text channel to someone.
        """
        await self.config.member(user).channel.set(channel.id)
        await ctx.send(
            f"Assigned {user.name} ({user.id}) to channel {channel.name} ({channel.id})."
        )

    @_my_channel.command()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    async def unassign(
        self, ctx: commands.Context, *, user: Union[discord.Member, discord.User, int]
    ):
        """
        Unassign personal text channel from someone.
        """
        if isinstance(user, discord.Member):
            await self.config.member(user).channel.clear()
        elif isinstance(user, int):
            await self.config.member_from_ids(ctx.guild.id, user).channel.clear()
            if _user := self.bot.get_user(user):
                user = _user
            else:
                user = discord.Object(user)  # type: ignore
                user.name = "[Unknown or Deleted User]"  # type: ignore
        await ctx.send(f"Unassigned {user.name} ({user.id}) from their personal channel.")

    @_my_channel.command(name="list")
    @commands.admin_or_permissions(manage_guild=True)
    async def _list(self, ctx: commands.Context):
        """Assigned channels list."""
        members_data = await self.config.all_members(ctx.guild)
        assigned_channels = []
        for member, data in members_data.items():
            if not data["channel"]:
                continue
            dic = {
                "User": ctx.guild.get_member(member) or f"[X] {member}",
                "Channel": shorten(
                    str(ctx.guild.get_channel(data["channel"]) or "[X] {}".format(data["channel"]))
                    + f" ({data['channel']})",
                    32,
                    placeholder="…",
                ),
            }
            assigned_channels.append(dic)
        pages = list(pagify(tabulate(assigned_channels, headers="keys", tablefmt="orgtbl")))
        pages = [box(page) for page in pages]
        if pages:
            await menu(ctx, pages, DEFAULT_CONTROLS)
        else:
            await ctx.send("There is no assigned personal channels in this server.")

    @_my_channel.command(name="category")
    @commands.admin_or_permissions(manage_guild=True)
    async def _category(
        self, ctx: commands.Context, category: Optional[discord.CategoryChannel] = None
    ):
        """
        Configure the category every personal text channel should be under.
        """
        if category is None:
            await self.config.guild(ctx.guild).category.clear()
            await ctx.send(f"I have cleared the personal text channel category.")
            return
        await self.config.guild(ctx.guild).category.set(category.id)
        await ctx.send(
            f"I have set {category.name} ({category.id}) as the personal text channel category."
        )

    @_my_channel.command(name="create")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_guild_permissions(manage_channels=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def _create(
        self,
        ctx: commands.Context,
        user: discord.Member,
        perms: commands.Range[int, 1, 30],
        *,
        name: commands.Range[str, 1, 32],
    ):
        """
        Create a personal channel and assign it to the user.

        - `<perms>`: give the user permissions on how many users they want to add in their channel.
        """
        category_id = await self.config.guild(ctx.guild).category()
        if category_id is None:
            await ctx.send(f"The category id is not setup in this server!")
            self._create.reset_cooldown(ctx)
            return
        if (await self.config.member(user).channel()) is not None:
            await ctx.send(f"{user.display_name} already has a personal channel.")
            self._create.reset_cooldown(ctx)
            return
        if name.casefold() in await self.config.guild(ctx.guild).blacklist():
            await ctx.send("This channel name is blacklisted.")
            self._create.reset_cooldown(ctx)
            return
        category = self.get_category(category_id)
        overwrites: Dict[Union[discord.Role, discord.Member], discord.PermissionOverwrite] = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(
                read_messages=True,
            ),
            user: discord.PermissionOverwrite(
                read_messages=True,
                attach_files=True,
                embed_links=True,
                external_emojis=True,
                external_stickers=True,
                add_reactions=True,
                use_application_commands=True,
            ),
        }
        try:
            channel = await ctx.guild.create_text_channel(
                name=name,
                category=category,
                overwrites=overwrites,
                reason=get_audit_reason(
                    ctx.author, f"Created personal channel for {user.display_name}."
                ),
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                "Unable to create channel.\n{}".format(box(str(e), lang="py"))
            )
        else:
            await self.config.member(user).channel.set(channel.id)
            await self.config.member(user).permission.set(int(perms))
            await ctx.send(
                f"Assigned {user.name} ({user.id}) to channel {channel.name} ({channel.id})."
            )

    @_my_channel.command(name="perms")
    @commands.admin_or_permissions(manage_guild=True)
    async def _perms(
        self,
        ctx: commands.Context,
        user: discord.Member,
        perms: commands.Range[int, 1, 30] = None,
    ):
        """
        Give users permissions on how many users they can to add in their channel.

        Run this command without the `perms` argument to clear the permission config.
        """
        if perms is None:
            await ctx.send(f"Cleared the permission config for {user.display_name}")
            return
        await self.config.member(user).permission.set(int(perms))
        await ctx.send(f"{user.display_name} can now add {int(perms)} friends in their channel.")

    @_my_channel.command(name="position")
    @commands.admin_or_permissions(manage_guild=True)
    async def _position(
        self, ctx: commands.Context, user: discord.Member, *, position: PositionConverter
    ):
        """
        Edit the channel position for someone's personal channel.
        """
        channel = await self.config.member(ctx.author).channel()
        if channel is None:
            await ctx.send(f"{user.display_name} does not have a personal channel.")
            return
        channel = ctx.guild.get_channel(channel)
        await self.check_text_channels(ctx, channel)
        try:
            await channel.edit(
                position=position,
                reason=get_audit_reason(
                    ctx.author, f"Changed {user.display_name}'s personal channel position."
                ),
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                "Unable to edit channel name.\n{}".format(box(str(e), lang="py"))
            )
        else:
            await ctx.send(
                f"Changed {user.display_name}'s personal channel to position {int(position) + 1}."
            )

    @has_assigned_channel()
    @_my_channel.command("friends")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _friends(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        user: Optional[discord.Member] = None,
    ):
        """
        Add or remove friends from your channel.

        `<add_or_remove>` should be either `add` to add channels or `remove` to remove friends.
        """
        if user is None:
            await ctx.send("`User` is a required argument.")
            return

        friends: List[int] = await self.config.member(ctx.author).friends()
        perms: int = await self.config.member(ctx.author).permission()

        if add_or_remove.lower() == "add" and friends is None:
            await ctx.send("You're not allowed to add friends in your personal channel.")
            return

        if add_or_remove.lower() == "add" and len(friends) >= perms:
            await ctx.send(
                "You are at maximum capacity, you cannot add any more friends to your channel."
            )
            self._friends.reset_cooldown(ctx)
            return

        channel_id = await self.config.member(ctx.author).channel()
        channel = ctx.guild.get_channel(channel_id)

        async with self.config.member(ctx.author).friends() as friends:
            if add_or_remove.lower() == "add":
                if user.id in friends:
                    await ctx.send(f"{user.display_name} is already in your friend list.")
                    return
                if not user.id in friends:
                    try:
                        await self.bot.http.edit_channel_permissions(
                            channel_id=channel.id,
                            target=user.id,
                            allow="139586749504",
                            deny="0",
                            type=1,
                            reason=get_audit_reason(
                                ctx.author, "Added user to their personal channel."
                            ),
                        )
                    except discord.HTTPException as e:
                        raise commands.UserFeedbackCheckFailure(
                            "Unable to create channel.\n{}".format(box(str(e), lang="py"))
                        )
                    else:
                        friends.append(user.id)

            elif add_or_remove.lower() == "remove":
                if not user.id in friends:
                    await ctx.send(f"{user.display_name} is not in your friend list.")
                    return
                elif user.id in friends:
                    try:
                        await channel.set_permissions(
                            user,
                            overwrite=None,
                            reason=get_audit_reason(
                                ctx.author, "Removed user from their personal channel."
                            ),
                        )
                    except discord.HTTPException as e:
                        raise commands.UserFeedbackCheckFailure(
                            "Unable to create channel.\n{}".format(box(str(e), lang="py"))
                        )
                    else:
                        friends.remove(user.id)

        await ctx.send(
            f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} "
            f"{user.display_name} {'to' if add_or_remove.lower() == 'add' else 'from'} your friend list."
        )

    @has_assigned_channel()
    @_my_channel.command(name="name")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _name(self, ctx: commands.Context, *, name: commands.Range[str, 1, 32]):
        """
        Change name of personal channel.

        You cant use blacklisted names.
        """
        channel = await self.config.member(ctx.author).channel()
        channel = ctx.guild.get_channel(channel)
        await self.check_text_channels(ctx, channel)
        if name.casefold() in await self.config.guild(ctx.guild).blacklist():
            await ctx.send("This channel name is blacklisted.")
            self._name.reset_cooldown(ctx)
            return
        try:
            await channel.edit(name=name, reason=get_audit_reason(ctx.author, "Personal Channel"))
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                "Unable to edit channel name.\n{}".format(box(str(e), lang="py"))
            )
        else:
            await ctx.send(
                f"Changed name of {ctx.author.display_name}'s personal channel to name {name}."
            )

    @has_assigned_channel()
    @_my_channel.command(name="topic")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _topic(self, ctx: commands.Context, *, topic: str):
        """
        Change the topic of personal channel.

        You can't use blacklisted words.
        """
        channel = await self.config.member(ctx.author).channel()
        channel = ctx.guild.get_channel(channel)
        await self.check_text_channels(ctx, channel)
        if topic.casefold() in await self.config.guild(ctx.guild).blacklist():
            await ctx.send("This channel topic is blacklisted.")
            self._topic.reset_cooldown(ctx)
            return
        try:
            await channel.edit(
                topic=topic, reason=get_audit_reason(ctx.author, "Personal Channel")
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                "Unable to edit channel topic.\n{}".format(box(str(e), lang="py"))
            )
        else:
            await ctx.send(
                f"Changed topic of {ctx.author.display_name}'s personal channel to {topic}."
            )

    @has_assigned_channel()
    @_my_channel.command(name="nsfw", hidden=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _nsfw(self, ctx: commands.Context, nsfw: Optional[bool] = None):
        """
        Toggle nsfw in the personal channel.
        """
        channel = await self.config.member(ctx.author).channel()
        channel = ctx.guild.get_channel(channel)
        await self.check_text_channels(ctx, channel)
        if nsfw is None:
            nsfw = not channel.nsfw
        try:
            await channel.edit(
                nsfw=nsfw,
                reason=get_audit_reason(ctx.channel, "Edited nsfw toggle of personal channel."),
            )
        except discord.HTTPException as e:
            raise commands.UserFeedbackCheckFailure(
                "Unable to toggle channel nsfw.\n{}".format(box(str(e), lang="py"))
            )
        else:
            await ctx.send(
                f"Changed nsfw toggle of {ctx.author.display_name}'s personal channel to {nsfw}"
            )

    @has_assigned_channel()
    @_my_channel.command(name="delete")
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _delete(self, ctx: commands.Context):
        """
        Delete your personal channel.
        """
        channel = await self.config.member(ctx.author).channel()
        channel = ctx.guild.get_channel(channel)
        await self.check_text_channels(ctx, channel)
        await ctx.send(
            f"Are you sure you want to delete you personal channel? Type `yes` to confirm otherwise type `no`."
        )
        try:
            pred = MessagePredicate.yes_or_no(ctx, user=ctx.author)
            await ctx.bot.wait_for("message", check=pred, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Exiting operation.")
            return
        if pred.result:
            try:
                await channel.delete(
                    reason=get_audit_reason(ctx.author, "Deleted their person channel.")
                )
            except discord.HTTPException as e:
                raise commands.UserFeedbackCheckFailure(
                    "Unable to delete channel.\n{}".format(box(str(e), lang="py"))
                )
            else:
                await self.config.member_from_ids(ctx.guild.id, ctx.author.id).clear()
        else:
            await ctx.send("Cancelling.")

    @_my_channel.group(name="blacklist", aliases=["blocklist"])
    @commands.admin_or_permissions(manage_guild=True)
    async def _blacklist(self, ctx: commands.Context):
        """
        manage blacklisted names.
        """

    @_blacklist.command(name="add")
    async def _add(self, ctx: commands.Context, *, channel_name: str):
        """
        Add channel name to blacklist.

        Members will not be able to change name to blacklisted names.
        """
        channel_name = channel_name.casefold()
        async with self.config.guild(ctx.guild).blacklist() as blacklist:
            if channel_name in blacklist:
                await ctx.send("`{}` is already in the blacklist.".format(channel_name))
            else:
                blacklist.append(channel_name)
                await ctx.send("Added `{}` to blacklist channels list.".format(channel_name))

    @_blacklist.command(name="remove")
    async def _remove(self, ctx: commands.Context, *, channel_name: str):
        """
        Remove channel name from blacklist.
        """
        channel_name = channel_name.casefold()
        async with self.config.guild(ctx.guild).blacklist() as blacklist:
            if channel_name not in blacklist:
                await ctx.send("`{}` is not blacklisted.".format(channel_name))
            else:
                blacklist.remove(channel_name)
                await ctx.send("Removed `{}` from blacklisted channels list.".format(channel_name))

    @_blacklist.command(name="list")
    async def _blacklist_list(self, ctx: commands.Context):
        """
        List of blacklisted channel names.
        """
        blacklist = await self.config.guild(ctx.guild).blacklist()
        pages = [box(page) for page in pagify("\n".join(blacklist))]
        if pages:
            await menu(ctx, pages, DEFAULT_CONTROLS)
        else:
            await ctx.send("There is no blacklisted channel name.")
