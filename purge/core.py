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

import asyncio
import logging
import re
from typing import Any, Callable, Coroutine, Dict, Final, List, Optional, Union

import arrow
import discord
from redbot.cogs.cleanup.cleanup import Cleanup as CleanupCog
from redbot.core import app_commands, commands, modlog
from redbot.core.bot import Red
from redbot.core.utils import mod
from redbot.core.utils.chat_formatting import humanize_list, humanize_number

from .converters import PurgeFlags, RawMessageIdsConverter
from .utils import (
    CUSTOM_EMOJI_RE,
    LINKS_RE,
    _cleanup,
    _create_case,
    get_message_from_reference,
    get_messages_for_deletion,
    has_hybrid_permissions,
)

log: logging.Logger = logging.getLogger("red.seina.purge")


class Purge(commands.Cog):
    __doc__ = CleanupCog.__doc__

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot

        self.task: asyncio.Task[Any] = self._create_task(self._initialize())

    @staticmethod
    def _task_done_callback(task: asyncio.Task) -> None:
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as error:
            log.exception("Task failed.", exc_info=error)

    @staticmethod
    async def _register_casetype() -> None:
        purge_case: Dict[str, Union[str, bool]] = {
            "name": "purge",
            "default_setting": True,
            "image": "🧹",
            "case_str": "Purge",
        }
        try:
            await modlog.register_casetype(**purge_case)  # type: ignore
        except RuntimeError:
            pass

    def _create_task(
        self, coroutine: Coroutine, *, name: Optional[str] = None
    ) -> asyncio.Task[Any]:
        task = asyncio.create_task(coroutine, name=name)
        task.add_done_callback(self._task_done_callback)
        return task

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Version: **{self.__version__}**",
            f"Author: **{humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    async def _initialize(self) -> None:
        await self.bot.wait_until_red_ready()
        await self._register_casetype()

    async def cog_unload(self) -> None:
        self.task.cancel()
        await super().cog_unload()

    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @has_hybrid_permissions(manage_messages=True, read_message_history=True)
    @app_commands.describe(number="The number of messages you want to delete.")
    @commands.hybrid_group(name="purge", aliases=["clean", "cleanup"], invoke_without_command=True)
    async def _purge(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes messages that meet a criteria.

        Messages older than 14 days cannot be deleted.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Example:**
        - `[p]purge 10`
        - `[p] purge 2000`
        """
        if ctx.invoked_subcommand is None:

            def check(message: discord.Message) -> bool:
                return message.created_at > arrow.utcnow().shift(days=-14).datetime

            await _cleanup(ctx, number, check)

    @_purge.command(name="embeds", aliases=["embed"])  # type: ignore
    async def _embeds(self, ctx: commands.GuildContext, number: commands.Range[int, 1, 2000]):
        """
        Removes messages that have embeds in them.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge embeds 10`
        - `[p]purge embeds 2000`
        """
        await _cleanup(ctx, number, lambda e: len(e.embeds))

    @_purge.command(name="regex")  # type: ignore
    async def _regex(
        self,
        ctx: commands.GuildContext,
        pattern: Optional[str],
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes messages that matches the regex pattern.

        **Arguments:**
        - `<pattern>`: The regex pattern to match.
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge regex (?i)(h(?:appy)`
        - `[p]purge regex (?i)(h(?:appy) 10`
        """

        def check(message: discord.Message) -> bool:
            ret = (
                bool(re.match(rf"{pattern}", message.content))
                and message.created_at > arrow.utcnow().shift(days=-14).datetime
            )
            return ret

        await _cleanup(ctx, number, check)

    @_purge.command(name="files", aliases=["file"])  # type: ignore
    async def _files(self, ctx: commands.GuildContext, number: commands.Range[int, 1, 2000]):
        """
        Removes messages that have attachments in them.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge files`
        - `[p]purge files 2000`
        """
        await _cleanup(ctx, number, lambda e: len(e.attachments))

    @_purge.command(name="images", aliases=["image"])  # type: ignore
    async def _images(self, ctx: commands.GuildContext, number: commands.Range[int, 1, 2000]):
        """
        Removes messages that have embeds or attachments.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge images`
        - `[p]purge images 2000`
        """
        await _cleanup(ctx, number, lambda e: len(e.embeds) or len(e.attachments))

    @_purge.command(name="user", aliases=["member"])  # type: ignore
    async def _user(
        self,
        ctx: commands.GuildContext,
        member: discord.Member,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes all messages by the member.

        **Arguments:**
        - `<member>`: The user to delete messages for.
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge user @member`
        - `[p]purge user @member 2000`
        """
        await _cleanup(ctx, number, lambda e: e.author == member)

    @_purge.command(name="contains", aliases=["contain"])  # type: ignore
    async def _contains(self, ctx: commands.GuildContext, *, text: str):
        """
        Removes all messages containing a text.
        The text must be at least 3 characters long.

        **Arguments:**
        - `<text>`: the text to be removed.

        **Examples:**
        - `[p]purge contains hi`
        - `[p]purge contains bye`
        """
        if len(text) < 3:
            await ctx.send(
                "The text length must be at least 3 characters long.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        else:
            await _cleanup(ctx, 100, lambda e: text in e.content)

    @_purge.command(name="bot", aliases=["bots"])  # type: ignore
    async def _bot(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
        prefix: Optional[str] = None,
    ):
        """
        Removes bot messages, optionally takes a prefix argument.

        **Arguments:**
        - `<prefix>`: The bot's prefix you want to remove.
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge bot`
        - `[p]purge bot 2000 ?`
        """

        def predicate(message: discord.Message) -> Union[Optional[bool], str]:
            return (
                (message.webhook_id is None and message.author.bot)
                or (prefix and message.content.startswith(prefix))
            ) and message.created_at > arrow.utcnow().shift(days=-14).datetime

        await _cleanup(ctx, number, predicate)

    @_purge.command(name="emoji", aliases=["emojis"])  # type: ignore
    async def _emoji(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes all messages containing custom emoji.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge emoji`
        - `[p]purge emoji 200`
        """

        def predicate(message: discord.Message) -> bool:
            return bool(
                CUSTOM_EMOJI_RE.search(message.content)
                and message.created_at > arrow.utcnow().shift(days=-14).datetime
            )

        await _cleanup(ctx, number, predicate)

    @_purge.command(name="reactions", aliases=["reaction"])  # type: ignore
    async def _reactions(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes all reactions from messages that have them.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge reactions`
        - `[p]purge reactions 200`
        """
        total_reactions: int = 0
        async for message in ctx.history(limit=number, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(
            f"Successfully removed {total_reactions} reactions.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_purge.command(name="self")  # type: ignore
    async def _self(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes your messages from the channel.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge self`
        - `[p]purge self 2000`
        """
        await _cleanup(ctx, number, lambda e: e.author == ctx.author)

    @_purge.command(name="mine")  # type: ignore
    async def _mine(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes my messages from the channel.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge mine`
        - `[p]purge mine 2000`
        """
        await _cleanup(ctx, number, lambda e: e.author == ctx.guild.me)

    @_purge.command(name="links", aliases=["link"])  # type: ignore
    async def _links(
        self,
        ctx: commands.GuildContext,
        number: commands.Range[int, 1, 2000],
    ):
        """
        Removes all messages containing a link.

        **Arguments:**
        - `<number`: The number of messages you want to delete.

        **Examples:**
        - `[p]purge links`
        - `[p]purge links 2000`
        """
        await _cleanup(ctx, number, lambda m: LINKS_RE.search(m.content))

    @_purge.command(name="after")  # type: ignore
    async def _after(
        self,
        ctx: commands.GuildContext,
        message_id: Optional[RawMessageIdsConverter],
        delete_pinned: Optional[bool] = False,
    ):
        """
        Delete all messages after a specified message.

        To get a message id, enable developer mode in Discord's
        settings, 'appearance' tab. Then right click a message
        and copy its id.
        Replying to a message will cleanup all messages after it.

        **Arguments:**
        - `<message_id>` The id of the message to cleanup after. This message won't be deleted.
        - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
        """
        after: Optional[discord.Message] = None

        if message_id:
            try:
                after: Optional[discord.Message] = await ctx.channel.fetch_message(message_id)  # type: ignore
            except discord.NotFound:
                await ctx.send(
                    "Message not found.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
        elif reference := ctx.message.reference:
            after: Optional[discord.Message] = await get_message_from_reference(
                ctx.channel, reference
            )

        if after is None:
            await ctx.send(
                f"Could not find any messages to delete.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return

        to_delete: List[discord.Message] = await get_messages_for_deletion(
            channel=ctx.channel, number=None, after=after, delete_pinned=delete_pinned
        )

        reason: str = "{} ({}) deleted {} messages in channel #{}.".format(
            ctx.author,
            ctx.author.id,
            humanize_number(len(to_delete), override_locale="en_US"),
            ctx.channel.name,
        )

        await _create_case(
            self.bot,
            ctx.guild,
            type="purge",
            reason=reason,
            user=ctx.author,
        )
        await mod.mass_purge(to_delete, ctx.channel, reason=reason)
        await ctx.send(
            f"Successfully deleted {len(to_delete)} {'message' if len(to_delete) == 1 else 'messages'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_purge.command(name="before")  # type: ignore
    async def _before(
        self,
        ctx: commands.GuildContext,
        message_id: Optional[RawMessageIdsConverter],
        number: commands.Range[int, 1, 2000],
        delete_pinned: Optional[bool] = False,
    ):
        """
        Deletes X messages before the specified message.

        To get a message id, enable developer mode in Discord's
        settings, 'appearance' tab. Then right click a message
        and copy its id.
        Replying to a message will cleanup all messages before it.

        **Arguments:**
        - `<message_id>` The id of the message to cleanup before. This message won't be deleted.
        - `<number>` The max number of messages to cleanup. Must be a positive integer.
        - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False
        """
        before: Optional[discord.Message] = None

        if message_id:
            try:
                before: Optional[discord.Message] = await ctx.channel.fetch_message(message_id)  # type: ignore
            except discord.NotFound:
                await ctx.send(
                    "Message not found.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                return
        elif reference := ctx.message.reference:
            before: Optional[discord.Message] = await get_message_from_reference(
                ctx.channel, reference
            )

        if before is None:
            await ctx.send(
                f"Could not find any messages to delete.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return

        to_delete: List[discord.Message] = await get_messages_for_deletion(
            channel=ctx.channel, number=number, before=before, delete_pinned=delete_pinned
        )
        to_delete.append(ctx.message)

        reason: str = "{} ({}) deleted {} messages in channel #{}.".format(
            ctx.author,
            ctx.author.id,
            humanize_number(len(to_delete), override_locale="en_US"),
            ctx.channel.name,
        )

        await _create_case(
            self.bot,
            ctx.guild,
            type="purge",
            reason=reason,
            user=ctx.author,
        )
        await mod.mass_purge(to_delete, ctx.channel, reason=reason)
        await ctx.send(
            f"Successfully deleted {len(to_delete)} {'message' if len(to_delete) == 1 else 'messages'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_purge.command(name="between")  # type: ignore
    async def _between(
        self,
        ctx: commands.GuildContext,
        one: RawMessageIdsConverter,
        two: RawMessageIdsConverter,
        delete_pinned: Optional[bool] = None,
    ):
        """
        Delete the messages between Message One and Message Two, providing the messages IDs.

        The first message ID should be the older message and the second one the newer.

        **Arguments:**
        - `<one>` The id of the message to cleanup after. This message won't be deleted.
        - `<two>` The id of the message to cleanup before. This message won't be deleted.
        - `<delete_pinned>` Whether to delete pinned messages or not. Defaults to False.

        **Example:**
        - `[p]cleanup between 123456789123456789 987654321987654321`
        """
        try:
            message_one: Optional[discord.Message] = await ctx.channel.fetch_message(one)  # type: ignore
        except discord.NotFound:
            await ctx.send(
                f"Could not find a message with the ID of {one}.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        try:
            message_two: Optional[discord.Message] = await ctx.channel.fetch_message(two)  # type: ignore
        except discord.NotFound:
            await ctx.send(
                f"Could not find a message with the ID of {two}.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        to_delete: List[discord.Message] = await get_messages_for_deletion(
            channel=ctx.channel, before=message_two, after=message_one, delete_pinned=delete_pinned
        )
        to_delete.append(ctx.message)
        reason: str = "{} ({}) deleted {} messages in channel #{}.".format(
            ctx.author,
            ctx.author.id,
            humanize_number(len(to_delete), override_locale="en_US"),
            ctx.channel.name,
        )

        await _create_case(
            self.bot,
            ctx.guild,
            type="purge",
            reason=reason,
            user=ctx.author,
        )
        await mod.mass_purge(to_delete, ctx.channel, reason=reason)
        await ctx.send(
            f"Successfully deleted {len(to_delete)} {'message' if len(to_delete) == 1 else 'messages'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_purge.command(name="duplicates", aliases=["duplicate", "spam"])  # type: ignore
    async def _duplicates(self, ctx: commands.GuildContext, number: commands.Range[int, 1, 2000]):
        """
        Deletes duplicate messages in the channel from the last X messages and keeps only one copy.

        **Arguments:**
        - `<number>` The number of messages to check for duplicates. Must be a positive integer.
        """
        messages: List[discord.Message] = []
        spam: List[discord.Message] = []

        def check(m: discord.Message):
            if m.attachments:
                return False
            content = (
                m.author.id,
                m.content,
                [embed.to_dict() for embed in m.embeds],
                [sticker.id for sticker in m.stickers],
            )  # type: ignore
            if content in messages:
                spam.append(m)
                return True
            else:
                messages.append(content)  # type: ignore
                return False

        to_delete: List[discord.Message] = await get_messages_for_deletion(
            channel=ctx.channel, limit=number, check=check, before=ctx.message
        )
        to_delete.append(ctx.message)

        await _create_case(
            self.bot,
            ctx.guild,
            type="purge",
            reason="Duplicate message purge.",
            user=ctx.author,
        )
        await mod.mass_purge(to_delete, ctx.channel, reason="Duplicate message purge.")
        await ctx.send(
            f"Successfully deleted {len(to_delete)} {'message' if len(to_delete) == 1 else 'messages'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_purge.command(name="custom")  # type: ignore
    async def _custom(
        self,
        ctx: commands.GuildContext,
        number: Optional[commands.Range[int, 1, 2000]] = None,
        *,
        flags: PurgeFlags,
    ):
        """
        Remove messages that meet a criteria from the flags.

        The following flags are valid.

        `user:` Remove messages from the given user.
        `contains:` Remove messages that contain a substring.
        `prefix:` Remove messages that start with a string.
        `suffix:` Remove messages that end with a string.
        `after:` Search for messages that come after this message ID.
        `before:` Search for messages that come before this message ID.
        `bot: yes` Remove messages from bots. (not webhooks!)
        `webhooks: yes` Remove messages from webhooks.
        `embeds: yes` Remove messages that have embeds.
        `files: yes` Remove messages that have attachments.
        `emoji: yes` Remove messages that have custom emoji.
        `reactions: yes` Remove messages that have reactions.
        `require: any or all` Whether any or all flags should be met before deleting messages.
        """
        predicates: List[Callable[[discord.Message], Any]] = []

        if flags.bot:
            if flags.webhooks:
                predicates.append(lambda m: m.author.bot)
            else:
                predicates.append(
                    lambda m: (m.webhook_id is None or m.interaction is not None) and m.author.bot
                )
        elif flags.webhooks:
            predicates.append(lambda m: m.webhook_id is not None)

        if flags.embeds:
            predicates.append(lambda m: len(m.embeds))

        if flags.files:
            predicates.append(lambda m: len(m.attachments))

        if flags.reactions:
            predicates.append(lambda m: len(m.reactions))

        if flags.emoji:
            predicates.append(lambda m: CUSTOM_EMOJI_RE.search(m.content))

        if flags.user:
            predicates.append(lambda m: m.author == flags.user)

        if flags.contains:
            predicates.append(lambda m: flags.contains in m.content)  # type: ignore

        if flags.prefix:
            predicates.append(lambda m: m.content.startswith(flags.prefix))  # type: ignore

        if flags.suffix:
            predicates.append(lambda m: m.content.endswith(flags.suffix))  # type: ignore

        op = all if flags.require == "all" else any

        def predicate(m: discord.Message) -> bool:
            r = op(p(m) for p in predicates)
            return r

        if flags.after:
            if number is None:
                number = 2000

        if number is None:
            number = 100

        before = flags.before if flags.before else None
        after = flags.after if flags.after else None

        await _cleanup(ctx, number, predicate, before=before, after=after)
