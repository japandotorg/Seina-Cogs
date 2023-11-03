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

import logging
from datetime import datetime, timezone
from typing import Dict, Final, List, Literal, Optional, Union

import discord
import TagScriptEngine as tse
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, pagify
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from ._tagscript import (
    TAGSCRIPT_LIMIT,
    TagCharacterLimitReached,
    TagscriptConverter,
    _process_tagscript,
    custom_message,
)
from .views import AFKPaginator, AFKView

log: logging.Logger = logging.getLogger("red.seina.afk")


class AFK(commands.Cog):
    """
    A cog for being afk and responding when idiots ping you.
    """

    __author__: Final[str] = humanize_list(["inthedark.org"])
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=69_420_666, force_registration=True)
        default_member: Dict[str, Union[str, bool, int, List]] = {
            "afk_status": False,
            "afk_message": "",
            "afk_time": int(datetime.now().timestamp()),
            "pings": [],
            "blocked": [],
            "custom_message": custom_message,
        }
        default_guild: Dict[str, Union[List[int], str]] = {
            "ignored_channels": [],
            "nickname": "[AFK]",
            "toggle_nickname": False,
        }
        default_global: Dict[str, int] = {"delete_after": 10}
        self.config.register_member(**default_member)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{self.__author__}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def validate_tagscript(self, tagscript: str) -> bool:
        length = len(tagscript)
        if length > TAGSCRIPT_LIMIT:
            raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
        return True

    def _make_message(self, message: discord.Message) -> str:
        return (
            f"` - ` {message.author.mention} [pinged you in]({message.jump_url}) "
            f"{message.channel.mention} <t:{int(datetime.now(timezone.utc).timestamp())}:R>\n"  # type: ignore
            f"**Message Content**: {message.content}"
        )

    async def _ping_list(
        self,
        interaction: discord.Interaction[Red],
        data: Dict,
    ) -> None:
        pings = "\n".join(i for i in data["pings"])
        embeds = []
        pages = []
        for page in pagify(pings, delims=["\n"], page_length=4000):
            pages.append(page)
        for index, page in enumerate(pages, 1):
            embed: discord.Embed = discord.Embed(
                title=f"Pings you recieved while you were AFK {interaction.user.name}!",
                description=page,
                color=interaction.user.color,
            )
            embed.set_footer(text=f"Page: {index}/{len(pages)}")
            embeds.append(embed)
        ctx = await self.bot.get_context(interaction.message)
        await AFKPaginator(ctx, embeds, interaction, 60, use_select=True).start()

    async def _pinged_user(self, message: discord.Message, member: discord.Member) -> None:
        data = await self.config.member(member).all()  # type: ignore
        if message.author.id in data["blocked"]:
            return
        async with self.config.member(member).pings() as pings:
            pings.append(self._make_message(message))

    async def _update_nickname(self, member: discord.Member, *, force: bool = False) -> None:
        if not await self.config.guild(member.guild).toggle_nickname():
            return
        custom: str = await self.config.guild(member.guild).nickname()
        original: str = member.nick or member.display_name
        if force:
            if len(original) > 26:
                return
            forced: str = f"{custom}{original}"
        elif original.startswith(custom):
            forced: str = original[len(custom) :]
            if forced == (member.global_name or member.name):
                forced = None  # type: ignore
        else:
            return
        try:
            await member.edit(nick=forced)
        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.is_system():
            return

        if not message.guild:
            return

        if (
            message.author.bot
            or message.channel.id in await self.config.guild(message.guild).ignored_channels()
        ):
            return

        if not message.channel.permissions_for(message.guild.me).send_messages:
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        if not await self.bot.ignored_channel_or_guild(message):
            return
        if not await self.bot.allowed_by_whitelist_blacklist(message.author):
            return

        member_config = self.config.member(message.author)  # type: ignore
        afk_status = await member_config.afk_status()
        if afk_status:
            afk_time = await member_config.afk_time()
            data = await self.config.member(message.author)()  # type: ignore
            time_difference = datetime.now().timestamp() - afk_time
            if await self.config.guild(message.guild).toggle_nickname():
                if not message.guild.me.guild_permissions.manage_nicknames:
                    # If the bot doesn't have manage nicknames perms anymore, disable the feature.
                    await self.config.guild(message.guild).toggle_nickname.set(False)
                await self._update_nickname(message.author)  # type: ignore
                return
            ctx = await self.bot.get_context(message)
            _view = AFKView(ctx, self, data)
            _view._message = await message.channel.send(
                embed=discord.Embed(
                    title="Your AFK has been removed!",
                    color=message.author.color,
                ),
                reference=message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
                view=_view,
            )
            if time_difference > 10:
                await member_config.afk_status.clear()
                await member_config.afk_message.clear()
                await member_config.afk_time.clear()
                await member_config.pings.clear()
                return

        for member in message.mentions:
            afk_status = await self.config.member(member).afk_status()  # type: ignore
            if afk_status:
                if message.channel.permissions_for(member).view_channel is False:  # type: ignore
                    return
                afk_delete_after = await self.config.delete_after()
                afk_time = await self.config.member(member).afk_time()  # type: ignore
                afk_message = await self.config.member(member).afk_message()  # type: ignore
                afk_custom_message = await self.config.member(member).custom_message()  # type: ignore
                time = f"<t:{afk_time}:R>"
                await self._pinged_user(message, member)  # type: ignore
                kwargs = _process_tagscript(
                    afk_custom_message,
                    {
                        "server": tse.GuildAdapter(member.guild),  # type: ignore
                        "author": tse.MemberAdapter(member),  # type: ignore
                        "time": tse.StringAdapter(time),
                        "reason": tse.StringAdapter(afk_message),
                        "color": tse.StringAdapter(str(member.color)),
                    },
                )
                if not kwargs:
                    await self.config.member(member).custom_message.clear()  # type: ignore
                    kwargs = _process_tagscript(
                        custom_message,
                        {
                            "server": tse.GuildAdapter(member.guild),  # type: ignore
                            "author": tse.MemberAdapter(member),  # type: ignore
                            "time": tse.StringAdapter(time),
                            "reason": tse.StringAdapter(afk_message),
                            "color": tse.StringAdapter(str(member.color)),
                        },
                    )
                kwargs["allowed_mentions"] = discord.AllowedMentions.none()
                kwargs["delete_after"] = afk_delete_after
                kwargs["reference"] = message.to_reference(fail_if_not_exists=False)
                await message.channel.send(**kwargs)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        data = await self.config.all_members(guild=member.guild)
        if member.id in data:
            await self.config.member_from_ids(member.guild.id, member.id).clear()

    @commands.guild_only()
    @commands.group(name="afk", invoke_without_command=True)
    async def _afk(self, ctx: commands.Context, *, message: Optional[str] = None):
        """
        Set yourself as AFK with an optional message.
        """
        if ctx.invoked_subcommand is None:
            member_config = self.config.member(ctx.author)  # type: ignore
            afk_status = await member_config.afk_status()
            if not afk_status:
                await member_config.afk_time.set(int(datetime.now().timestamp()))
                await member_config.afk_status.set(True)
                if not message:
                    message = "AFK"
                await self._update_nickname(ctx.author, force=True)  # type: ignore
                await member_config.afk_message.set(message)
                await ctx.send(
                    embed=discord.Embed(
                        title="You're now AFK!",
                        description=f"**Message:**\n- {message}",
                        color=ctx.author.color,
                    ),
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
            else:
                await ctx.send(
                    "You are already AFK.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                )

    @_afk.command(name="reset")
    @commands.mod_or_permissions(administrator=True)
    async def _reset(self, ctx: commands.Context, member: discord.Member):
        """
        [Admin/Mod] Reset member's custom afk message.
        """
        await self.config.member(member).custom_message.clear()
        await ctx.tick()

    @_afk.command(name="custom")
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _custom(
        self, ctx: commands.Context, *, message: Optional[TagscriptConverter] = None
    ):
        """
        Change the message sent when someone pings you while you're afk.

        (Supports Tagscript)

        **Blocks:**
        - [Embed](https://seina-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#embed-block)
        - [If](https://seina-cogs.readthedocs.io/en/latest/tags/tse_blocks.html#if-block)
        - [Assignement](https://seina-cogs.readthedocs.io/en/latest/tags/tse_blocks.html#assignment-block)

        **Variable:**
        - `{server}` - [The server you're afk in](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#server-block)
        - `{author}` - [You (command author)](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#author-block)
        - `{time}` - The time you're afk from.
        - `{reason}` - The reason you're afk for.
        - `{color}` - Hoist color of people who ping you.

        **Example:**
        ```
        [p]afk custom {embed(description):
        {author(mention)} is currently AFK ({time})
        **Message:**
        {reason}
        }
        {embed(color):{color}}
        {embed(thumbnail):{author(avatar)}}
        ```
        """
        if message:
            await self.config.member(ctx.author).custom_message.set(message)  # type: ignore
            await ctx.send(
                "Sucessfully changed your afk message!",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        else:
            await self.config.member(ctx.author).custom_message.clear()  # type: ignore
            await ctx.send(
                "Reset your custom afk message.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )

    @commands.mod_or_permissions(administrator=True)
    @_afk.command(name="nickname", aliases=["nick"])
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _nickname(
        self, ctx: commands.Context, *, text: Optional[commands.Range[str, 3, 6]] = None
    ):
        """
        [Admin/Mod] change the afk nickname identifier of your server.
        """
        if not text:
            await self.config.guild(ctx.guild).nickname.clear()  # type: ignore
            await ctx.send(
                f"Cleared the afk nickname identifier to default.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await self.config.guild(ctx.guild).nickname.set(text)  # type: ignore
        await ctx.send(
            f"Changed the afk nickname identifer to {text}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.guild_only()
    @_afk.command(name="togglenick")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _togglenick(self, ctx: commands.Context):
        """
        [Admin/Mod] Toggle the afk nickname identifier of your server.
        """
        if not ctx.guild.me.guild_permissions.manage_nicknames:
            await ctx.send(
                "I don't have permissions to change nicknames.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        toggle = await self.config.guild(ctx.guild).toggle_nickname()
        await self.config.guild(ctx.guild).toggle_nickname.set(not toggle)  # type: ignore
        await ctx.send(
            f"{'Enabled' if not toggle else 'Disabled'} the afk nickname identifier.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_afk.command(name="block")
    @commands.cooldown(1, 30, commands.BucketType.member)
    async def _block(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        users: commands.Greedy[discord.Member] = None,  # type: ignore
    ) -> None:
        """
        Block of unblock users from triggering your ping list.

        `<add_or_remove>` should be either `add` to add or `remove` to remove users.
        """
        if users is None:
            await ctx.send("`Users` is a required argument.")
            return

        async with self.config.member(ctx.author).blocked() as blocked:  # type: ignore
            for user in users:
                if add_or_remove.lower() == "add":
                    if not user.id in blocked:
                        blocked.append(user.id)
                elif add_or_remove.lower() == "remove":
                    if user.id in blocked:
                        blocked.remove(user.id)
                else:
                    await ctx.send("Invalid option. (`add` or `remove`)")
                    return

        ids = len(list(users))
        await ctx.send(
            f"Successfully {'blocked' if add_or_remove.lower() == 'add' else 'unblocked'} {ids} {'user' if ids == 1 else 'users'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_afk.command(name="clear")
    @commands.mod_or_permissions(manage_guild=True)
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def _clear(self, ctx: commands.Context, member: discord.Member):
        """
        [Admin/Mod] Reset member's AFK.
        """
        afk_status = await self.config.member(member).afk_status()
        if afk_status:
            await self.config.member(member).clear()
        else:
            await ctx.send(
                f"{member.name} is not AFK!",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await ctx.send(
            f"Cleared {member.mention}'s AFK!",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_afk.command(name="ignore")
    @commands.admin_or_permissions(manage_guild=True)
    async def _ignore(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        channels: commands.Greedy[discord.TextChannel] = None,  # type: ignore
    ) -> None:
        """[Admin/Mod] Add or remove channels for your guild.

        `<add_or_remove>` should be either `add` to add channels or `remove` to remove channels.
        """
        if channels is None:
            await ctx.send("`Channels` is a required argument.")
            return

        async with self.config.guild(ctx.guild).ignored_channels() as c:  # type: ignore
            for channel in channels:
                if add_or_remove.lower() == "add":
                    if not channel.id in c:
                        c.append(channel.id)

                elif add_or_remove.lower() == "remove":
                    if channel.id in c:
                        c.remove(channel.id)

        ids = len(list(channels))

        await ctx.send(
            f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {ids} {'channel' if ids == 1 else 'channels'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_afk.group(name="list", invoke_without_command=True)
    async def _list(self, ctx: commands.Context):
        """
        List users who are AFK and their duration.
        """
        if ctx.invoked_subcommand is None:
            afk_members = []
            for member in ctx.guild.members:  # type: ignore
                member_config = self.config.member(member)
                afk_status = await member_config.afk_status()
                if afk_status:
                    afk_time = await member_config.afk_time()
                    afk_message = await member_config.afk_message()
                    afk_members.append((member, afk_time, afk_message))

            if not afk_members:
                await ctx.send("There are no AFK users in this server.")
                return

            afk_members = sorted(afk_members, key=lambda x: x[1])
            pages = []
            entries_per_page = 10

            for index in range(0, len(afk_members), entries_per_page):
                entries = afk_members[index : index + entries_per_page]
                embed: discord.Embed = discord.Embed(color=await ctx.embed_color())

                for i, (member, afk_time, message) in enumerate(entries, start=index + 1):
                    embed.add_field(
                        name=f"**{i}.** {member.name} ({member.id})",
                        value=f"- {message} - <t:{afk_time}:R>",
                        inline=False,
                    )

                pages.append(embed)

            await menu(ctx, pages, DEFAULT_CONTROLS)

    @_list.command(name="blocked", aliases=["block"])
    async def _blocked(self, ctx: commands.Context):
        """
        List your blocked users.
        """
        data = await self.config.member(ctx.author).all()  # type: ignore
        users = data["blocked"]
        blocked_users: List[str] = []
        for user in users:
            user = await self.bot.get_or_fetch_user(user)
            blocked_users.append(user.mention)
        embed: discord.Embed = discord.Embed(
            title=f"{ctx.author.name}'s blocklist!",
            description=humanize_list(blocked_users[:2000]),
            color=await ctx.embed_color(),
        )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_list.command(name="ignored", alias="ignore")
    @commands.admin_or_permissions(manage_guild=True)
    async def _ignored(self, ctx: commands.Context):
        """
        Lists the ignored channels for AFK.
        """
        guild_config = self.config.guild(ctx.guild)  # type: ignore
        ignored_list = await guild_config.ignored_channels()

        if not ignored_list:
            await ctx.send("There are no ignored channels in this server.")
            return

        ignored_channels = [ctx.guild.get_channel(channel_id) for channel_id in ignored_list]  # type: ignore
        ignored_channels = [channel for channel in ignored_channels if channel is not None]

        ignored_channels = sorted(ignored_channels, key=lambda x: x.name)

        entries_per_page = 10
        pages = []
        for index in range(0, len(ignored_channels), entries_per_page):
            entries = ignored_channels[index : index + entries_per_page]
            page_content = "\n".join(f"{channel.mention} ({channel.id})" for channel in entries)
            embed: discord.Embed = discord.Embed(
                title="Ignored Channels",
                description=page_content,
                color=await ctx.embed_color(),
            )
            pages.append(embed)

        await menu(ctx, pages, DEFAULT_CONTROLS)

    @commands.is_owner()
    @_afk.command(name="delete")
    async def _delete(self, ctx: commands.Context, amount: commands.Range[int, 0, 100]):
        """
        [Bot Owner] Change the `delete_after` for afk messages.
        """
        if amount == 0:
            await self.config.delete_after.set(None)
            await ctx.send(f"Disabled `delete_after`.")
            return
        await self.config.delete_after.set(amount)
        await ctx.send(
            f"Changed `delete_after` to {amount}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_afk.command(name="settings")
    @commands.bot_has_permissions(embed_links=True)
    @commands.admin_or_permissions(manage_guild=True)
    async def _settings(self, ctx: commands.Context):
        """
        Shows the settings for the server.
        """
        data = await self.config.guild(ctx.guild).all()  # type: ignore
        nickname = data["nickname"]
        toggle_nickname = data["toggle_nickname"]
        if toggle_nickname:
            toggle_nickname = "Enabled"
        else:
            toggle_nickname = "Disabled"
        ignored_channels = data["ignored_channels"]
        if not ignored_channels:
            ignored_channels = "None"
        else:
            ignored_channels = humanize_list(ignored_channels)
        msg = (
            f"**Nickname:** {nickname}\n"
            f"**Toggle Nickname:** {toggle_nickname}\n"
            f"**Ignored Channels:** {ignored_channels}"
        )
        embed: discord.Embed = discord.Embed(
            title="AFK Settings",
            description=msg,
            color=await ctx.embed_color(),
        )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
