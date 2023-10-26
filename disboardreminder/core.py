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
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import (
    Any,
    Coroutine,
    DefaultDict,
    Dict,
    Final,
    List,
    Literal,
    Match,
    Optional,
    Pattern,
    TypeAlias,
    Union,
)

import discord
import TagScriptEngine as tse
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils import AsyncIter
from redbot.core.utils.chat_formatting import box

from .converters import FuzzyRole

log: logging.Logger = logging.getLogger("red.seina.disboardreminder")

RequestType: TypeAlias = Literal["discord_deleted_user", "owner", "user", "user_strict"]

DISCORD_BOT_ID: Final[int] = 302050872383242240
LOCK_REASON: Final[str] = "DisboardReminder auto-lock"
MENTION_RE: Pattern[str] = re.compile(r"<@!?(\d{15,20})>")
BUMP_RE: Pattern[str] = re.compile(r"!d bump\b")

DEFAULT_GUILD_MESSAGE: Final[
    str
] = "It's been 2 hours since the last successful bump, could someone run </bump:947088344167366698>?"
DEFAULT_GUILD_THANKYOU_MESSAGE: Final[
    str
] = "{member(mention)} thank you for bumping! Make sure to leave a review at <https://disboard.org/server/{guild(id)}>."


class DisboardReminder(commands.Cog):
    """
    Set a reminder to bump on Disboard.
    """

    __version__: Final[str] = "1.3.7"
    __author__: Final[List[str]] = ["inthedark.org", "Phenom4n4n"]

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_420_666,
            force_registration=True,
        )
        default_guild: Dict[str, Union[Optional[int], str, bool]] = {
            "channel": None,
            "role": None,
            "message": DEFAULT_GUILD_MESSAGE,
            "ty_message": DEFAULT_GUILD_THANKYOU_MESSAGE,
            "next_bump": None,
            "lock": False,
            "clean": False,
        }
        self.config.register_guild(**default_guild)

        self.channel_cache: Dict[int, int] = {}
        self.bump_tasks: DefaultDict[int, Dict[str, asyncio.Task]] = defaultdict(dict)

        try:
            bot.add_dev_env_value("bprm", lambda x: self)
        except RuntimeError:
            pass

        blocks: List[tse.Block] = [
            tse.LooseVariableGetterBlock(),
            tse.AssignmentBlock(),
            tse.IfBlock(),
            tse.EmbedBlock(),
        ]
        self.tagscript_engine: tse.Interpreter = tse.Interpreter(blocks)

        self.bump_loop: asyncio.Task[Any] = self.create_task(self.bump_check_loop())
        self.initialize_task: asyncio.Task[Any] = self.create_task(self.initialize())

    async def cog_unload(self) -> None:
        try:
            self.__unload()
        except Exception as exc:
            log.exception(
                "An error occurred while unloading the cog. Version: %s",
                self.__version__,
                exc_info=exc,
            )

    def __unload(self) -> None:
        try:
            self.bot.remove_dev_env_value("bprm")
        except KeyError:
            pass
        if self.bump_loop:
            self.bump_loop.cancel()
        if self.initialize_task:
            self.initialize_task.cancel()
        for tasks in self.bump_tasks.values():
            for task in tasks.values():
                task.cancel()

    @staticmethod
    def task_done_callback(task: asyncio.Task) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as error:
            log.exception("Task failed.", exc_info=error)

    @staticmethod
    async def set_my_permissions(
        guild: discord.Guild, channel: discord.TextChannel, my_perms: discord.Permissions
    ) -> None:
        if not my_perms.send_messages:
            my_perms.update(send_messages=True)
            await channel.set_permissions(guild.me, overwrite=my_perms, reason=LOCK_REASON)  # type: ignore

    def create_task(
        self, coroutine: Coroutine, *, name: Optional[str] = None
    ) -> asyncio.Task[Any]:
        task = asyncio.create_task(coroutine, name=name)
        task.add_done_callback(self.task_done_callback)
        return task

    def process_tagscript(
        self, content: str, *, seed_variables: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        output = self.tagscript_engine.process(content, seed_variables)
        kwargs: Dict[str, Any] = {}
        if output.body:
            kwargs["content"] = output.body[:2000]
        if embed := output.actions.get("embed"):
            kwargs["embed"] = embed
        return kwargs

    async def initialize(self) -> None:
        async for guild_id, guild_data in AsyncIter(
            (await self.config.all_guilds()).items(), steps=100
        ):
            if guild_data["channel"]:
                self.channel_cache[guild_id] = guild_data["channel"]

    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        return

    async def bump_check_loop(self) -> None:
        await self.bot.wait_until_red_ready()
        while True:
            try:
                await self.bump_check_guilds()
            except Exception as error:
                log.exception("An error occurred in the bump restart loop.", exc_info=error)
            await asyncio.sleep(60)

    async def bump_check_guilds(self) -> None:
        async for guild_id, guild_data in AsyncIter(
            (await self.config.all_guilds()).items(), steps=100
        ):
            if not (guild := self.bot.get_guild(guild_id)):
                continue
            await self.bump_check_guild(guild, guild_data)

    async def bump_check_guild(
        self,
        guild: discord.Guild,
        guild_data: Dict[str, Any],
    ) -> None:
        end_time = guild_data["next_bump"]
        if not end_time:
            return
        now = discord.utils.utcnow().timestamp()
        remaining = end_time - now
        if remaining > 60:
            return
        task_name = f"bump_timer:{guild.id}-{end_time}"
        if task_name in self.bump_tasks[guild.id]:
            return
        task = self.create_task(self.bump_timer(guild, end_time), name=task_name)
        self.bump_tasks[guild.id][task_name] = task
        await asyncio.sleep(0.2)

    async def autolock_channel(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel,
        my_perms: discord.Permissions,
        *,
        lock: bool,
    ) -> None:
        await self.set_my_permissions(guild, channel, my_perms)

        current_perms = channel.overwrites_for(guild.default_role)
        check = False if lock else None
        if current_perms.send_messages is not check:
            await channel.set_permissions(
                guild.default_role,
                overwrite=current_perms,
                reason=LOCK_REASON,
            )

    async def bump_remind(self, guild: discord.Guild) -> None:
        guild = self.bot.get_guild(guild.id)  # type: ignore
        if not guild:
            return
        data = await self.config.guild(guild).all()
        channel = guild.get_channel(data["channel"])
        if not channel:
            return
        my_perms = channel.permissions_for(guild.me)
        if not my_perms.send_messages:
            await self.config.guild(guild).channel.clear()
            log.info(
                f"Cleared the bump reminder channel due to missing send messages permission in the {channel.name} ({channel.id})."
            )
            return

        if data["lock"] and my_perms.manage_roles:
            try:
                await self.autolock_channel(guild, channel, my_perms, lock=False)  # type: ignore
            except discord.Forbidden:
                await self.config.guild(guild).lock.clear()
                log.info(
                    f"Cleared auto locking bump reminder channel due to missing manage roles permission in {guild.name} ({guild.id})"
                )

        message = data["message"]
        allowed_mentions = self.bot.allowed_mentions
        if data["role"]:
            role = guild.get_role(data["role"])
            if role:
                message = f"{role.mention}: {message}"
                allowed_mentions = discord.AllowedMentions(roles=[role])

        kwargs = self.process_tagscript(message)
        if not kwargs:
            await self.config.guild(guild).message.clear()
            log.info(
                f"Cleared the bump reminder message to default due to fault in the tagscript."
            )
            kwargs = self.process_tagscript(DEFAULT_GUILD_MESSAGE)
        kwargs["allowed_mentions"] = allowed_mentions

        try:
            await channel.send(**kwargs)  # type: ignore
        except discord.Forbidden:
            await self.config.guild(guild).channel.clear()
        await self.config.guild(guild).next_bump.clear()

    async def bump_timer(self, guild: discord.Guild, timestamp: int) -> None:
        d = datetime.fromtimestamp(timestamp, timezone.utc)
        await discord.utils.sleep_until(d)
        await self.bump_remind(guild)

    def validate_cache(self, message: discord.Message) -> Optional[discord.TextChannel]:
        guild: discord.Guild = message.guild  # type: ignore
        if not guild:
            return
        if message.author.id != DISCORD_BOT_ID:
            return
        bump_chan_id = self.channel_cache.get(guild.id)
        if not bump_chan_id:
            return
        return guild.get_channel(bump_chan_id)  # type: ignore

    def validate_success(self, message: discord.Message) -> Optional[discord.Embed]:
        if not message.embeds:
            return
        embed = message.embeds[0]
        if ":thumbsup:" in embed.description:  # type: ignore
            return embed
        if message.webhook_id and "Bump done!" in embed.description:  # type: ignore
            return embed

    async def respond_to_bump(
        self,
        data: Dict[str, Any],
        bump_channel: discord.TextChannel,
        message: discord.Message,
        embed: discord.Embed,
    ) -> None:
        guild: discord.Guild = message.guild  # type: ignore
        my_perms = bump_channel.permissions_for(guild.me)
        next_bump = message.created_at.timestamp() + 7200
        await self.config.guild(guild).next_bump.set(next_bump)

        member_adapter = None
        match: Optional[Match[str]] = MENTION_RE.search(embed.description)  # type: ignore
        if match:
            member_id = int(match.group(1))
            user = await self.bot.get_or_fetch_member(guild, member_id)
            member_adapter = tse.MemberAdapter(user)
        elif my_perms.read_message_history:
            async for m in bump_channel.history(before=message, limit=10):
                if m.content and BUMP_RE.match(m.content):
                    member_adapter = tse.MemberAdapter(m.author)  # type: ignore
                    break
        if member_adapter is None:
            member_adapter = tse.StringAdapter("Unknown User")
        ty_message = data["ty_message"]
        if my_perms.send_messages:
            guild_adapter = tse.GuildAdapter(guild)
            seed: Dict[str, tse.Adapter] = {
                "member": member_adapter,
                "guild": guild_adapter,
                "server": guild_adapter,
            }
            kwargs: Dict[str, Any] = self.process_tagscript(ty_message, seed_variables=seed)
            if not kwargs:
                await self.config.guild(guild).ty_message.clear()
                log.info("Cleared bump reminder thankyou message due to fault in tagscript.")
                kwargs: Dict[str, Any] = self.process_tagscript(
                    DEFAULT_GUILD_THANKYOU_MESSAGE, seed_variables=seed
                )
            await bump_channel.send(**kwargs)
        else:
            await self.config.guild(guild).channel.clear()
            log.info(
                f"Cleared bump reminder channel in {guild.name} ({guild.id}) because of missing send messages permission in set channel."
            )
        if data["lock"] and my_perms.manage_roles:
            try:
                await self.autolock_channel(
                    guild,
                    bump_channel,
                    my_perms,
                    lock=True,
                )
            except discord.Forbidden:
                await self.config.guild(guild).lock.clear()
                log.info(
                    f"Disabled auto-locking bump reminder channel in {guild.name} ({guild.id}) because of missing manage role permissions."
                )

    @commands.Cog.listener("on_message_without_command")
    async def on_bump_message_event(self, message: discord.Message) -> None:
        bump_channel = self.validate_cache(message)
        if not bump_channel:
            return

        guild: discord.Guild = message.guild  # type: ignore
        channel: discord.TextChannel = message.channel  # type: ignore

        data = await self.config.guild(guild).all()
        if not data["channel"]:
            return

        clean = data["clean"]
        my_perms = channel.permissions_for(guild.me)

        if embed := self.validate_success(message):
            last_bump = data["next_bump"]
            if last_bump and last_bump - message.created_at.timestamp() > 0:
                return
            await self.respond_to_bump(data, bump_channel, message, embed)
        elif my_perms.manage_messages and clean and channel == bump_channel:
            await asyncio.sleep(2)
            try:
                await message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.group(name="bumpreminder", aliases=["bprm"])
    async def _bump_reminder(self, _: commands.Context):
        """
        Set a reminder to bump on Disboard.

        This sends a reminder to bump in a specified channel 2 hours after someone successfully bumps, thus making it more accurate than a repeating schedule.
        """

    @_bump_reminder.command(name="channel")  # type: ignore
    async def _bump_reminder_channel(
        self, ctx: commands.Context, channel: Optional[discord.TextChannel] = None
    ):
        """
        Set the channel to send bump reminders to.

        This also works as a toggle, so if no channel is provided, it will disable reminders for this server.
        """
        if not channel and ctx.guild.id in self.channel_cache:  # type: ignore
            del self.channel_cache[ctx.guild.id]  # type: ignore
            await self.config.guild(ctx.guild).channel.clear()  # type: ignore
            await ctx.send("Disabled bump reminders in this server.")
        elif channel:
            try:
                await channel.send(
                    "Set this channel as the reminder channel for bumps. "
                    "I will not send my first reminder until a successful bump is registered."
                )
            except discord.Forbidden:
                await ctx.send("I do not have permission to talk in that channel.")
            else:
                await self.config.guild(ctx.guild).channel.set(channel.id)  # type: ignore
                self.channel_cache[ctx.guild.id] = channel.id  # type: ignore
                await ctx.tick()
        else:
            raise commands.BadArgument

    @_bump_reminder.command(name="pingrole")  # type: ignore
    async def _bump_reminder_ping_role(
        self, ctx: commands.Context, role: Optional[FuzzyRole] = None
    ):
        """
        Set a role to ping for bump reminders.

        If no role is provided, it will clear the current role.
        """
        if not role:
            await self.config.guild(ctx.guild).role.clear()  # type: ignore
            await ctx.send("Cleared the role for bump reminders.")
        else:
            await self.config.guild(ctx.guild).role.set(role.id)  # type: ignore
            await ctx.send(f"Configured {role.name} to ping for bump reminders.")  # type: ignore

    @_bump_reminder.command(name="thankyou", aliases=["ty"])  # type: ignore
    async def _bump_reminder_thank_you(
        self, ctx: commands.Context, *, message: Optional[str] = None
    ):
        """
        Change the message used for 'Thank You' messages. Providing no message will reset to the default message.

        The thank you message supports TagScript blocks which can customize the message and even add an embed!
        [View the TagScript documentation here.](https://seina-cogs.readthedocs.io/en/latest/index.html)

        Variables:
        `{member}` - [The user who bumped](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#author-block)
        `{server}` - [This server](https://seina-cogs.readthedocs.io/en/latest/tags/default_variables.html#server-block)

        Blocks:
        `embed` - [Embed to be sent in the thank you message](https://seina-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#embed-block)

        **Examples:**
        > `[p]bprm ty Thanks {member} for bumping! You earned 10 brownie points from phen!`
        > `[p]bprm ty {embed(description):{member(mention)}, thank you for bumping! Make sure to vote for **{server}** on [our voting page](https://disboard.org/server/{guild(id)}).}`
        """
        if message:
            await self.config.guild(ctx.guild).ty_message.set(message)  # type: ignore
            await ctx.tick()
        else:
            await self.config.guild(ctx.guild).ty_message.clear()  # type: ignore
            await ctx.send("Reset this server's Thank You message.")

    @_bump_reminder.command(name="message")  # type: ignore
    async def _bump_reminder_message(
        self, ctx: commands.Context, *, message: Optional[str] = None
    ):
        """Change the message used for reminders. Providing no message will reset to the default message."""
        if message:
            await self.config.guild(ctx.guild).message.set(message)  # type: ignore
            await ctx.tick()
        else:
            await self.config.guild(ctx.guild).message.clear()  # type: ignore
            await ctx.send("Reset this server's reminder message.")

    @_bump_reminder.command(name="clean")  # type: ignore
    async def _bump_reminder_clean(
        self, ctx: commands.Context, true_or_false: Optional[bool] = None
    ):
        """
        Toggle whether [botname] should keep the bump channel "clean."

        [botname] will remove all failed invoke messages by Disboard.
        """
        target_state = (
            true_or_false
            if true_or_false is not None
            else not (await self.config.guild(ctx.guild).clean())  # type: ignore
        )
        await self.config.guild(ctx.guild).clean.set(target_state)  # type: ignore
        if target_state:
            await ctx.send("I will now clean the bump channel.")
        else:
            await ctx.send("I will no longer clean the bump channel.")

    @_bump_reminder.command(name="lock")  # type: ignore
    async def _bump_reminder_lock(
        self, ctx: commands.Context, true_or_false: Optional[bool] = None
    ):
        """Toggle whether the bot should automatically lock/unlock the bump channel."""
        target_state = (
            true_or_false
            if true_or_false is not None
            else not (await self.config.guild(ctx.guild).lock())  # type: ignore
        )
        await self.config.guild(ctx.guild).lock.set(target_state)  # type: ignore
        if target_state:
            await ctx.send("I will now auto-lock the bump channel.")
        else:
            await ctx.send("I will no longer auto-lock the bump channel.")

    @_bump_reminder.command(name="settings", aliases=["showsettings", "show", "ss"])  # type: ignore
    async def _bump_reminder_settings(self, ctx: commands.Context):
        """Show your Bump Reminder settings."""
        data = await self.config.guild(ctx.guild).all()  # type: ignore
        guild = ctx.guild

        if channel := guild.get_channel(data["channel"]):  # type: ignore
            channel = channel.mention
        else:
            channel = "None"
        if pingrole := guild.get_role(data["role"]):  # type: ignore
            pingrole = pingrole.mention
        else:
            pingrole = "None"

        description = [
            f"**Channel:** {channel}",
            f"**Ping Role:** {pingrole}",
            f"**Auto-lock:** {data['lock']}",
            f"**Clean Mode:** {data['clean']}",
        ]
        description = "\n".join(description)

        e: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            title="Bump Reminder Settings",
            description=description,
        )
        e.set_author(name=ctx.guild, icon_url=ctx.guild.icon.url)  # type: ignore

        for key, value in data.items():
            if isinstance(value, str):
                value = f"{box(discord.utils.escape_markdown(value), lang='json')}"
                e.add_field(name=key, value=value, inline=False)

        if data["next_bump"]:
            timestamp = datetime.fromtimestamp(data["next_bump"], timezone.utc)
            e.timestamp = timestamp
            e.set_footer(text="Next bump registered for")

        await ctx.send(embed=e)
