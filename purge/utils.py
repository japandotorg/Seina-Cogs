"""
Mozilla Public License Version 2.0

Copyright (c) 2023-present japandotorg
"""

import datetime
import re
from collections import Counter
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, TypeVar, Union

import discord
from redbot.core import commands, modlog
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_number

T = TypeVar("T")

__all__: Tuple[str, ...] = (
    "_cleanup",
    "_create_case",
    "_check_permissions",
    "has_hybrid_permissions",
    "get_message_from_reference",
    "get_messages_for_deletion",
    "CUSTOM_EMOJI_RE",
    "LINKS_RE",
)

CUSTOM_EMOJI_RE: Pattern[str] = re.compile(r"<a?:[a-zA-Z0-9\_]+:([0-9]+)>")
LINKS_RE: Pattern[str] = re.compile(
    r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*",
    flags=re.IGNORECASE,
)


async def _create_case(
    bot: Red,
    guild: discord.Guild,
    type: str,
    reason: str,
    user: Union[discord.User, discord.Member],
    until: Optional[datetime.datetime] = None,
    moderator: Optional[Union[discord.Member, discord.ClientUser]] = None,
) -> Optional[modlog.Case]:
    try:
        case = await modlog.create_case(
            bot,
            guild,
            discord.utils.utcnow(),
            type,
            user,
            moderator=moderator if moderator is not None else user,
            reason=reason,
            until=until,
        )
    except RuntimeError:
        case = None

    return case


async def _cleanup(
    ctx: commands.GuildContext,
    limit: Optional[int],
    predicate: Callable[[discord.Message], Any],
    *,
    before: Optional[int] = None,
    after: Optional[int] = None,
    channel: Optional[  # type: ignore
        Union[discord.Thread, discord.TextChannel, discord.VoiceChannel, discord.StageChannel]
    ] = None,
) -> None:
    channel: Union[
        discord.Thread, discord.TextChannel, discord.VoiceChannel, discord.StageChannel
    ] = (channel if channel else ctx.channel)

    limit = max(1, min(limit or 1, 2000))

    passed_before: Union[discord.Message, discord.Object] = (
        ctx.message if before is None else discord.Object(id=before)
    )
    two_weeks_before: datetime.datetime = ctx.message.created_at - datetime.timedelta(weeks=2)
    two_weeks_before_snowflake: int = discord.utils.time_snowflake(two_weeks_before)

    if after:
        _after: int = max(two_weeks_before_snowflake, after)
        passed_after: Optional[discord.Object] = discord.Object(id=_after)
    else:
        passed_after: Optional[discord.Object] = None

    reason: str = "{} ({}) deleted {} messages in channel #{}.".format(
        ctx.author,
        ctx.author.id,
        humanize_number(limit, override_locale="en_US"),
        ctx.channel.name,
    )

    try:
        deleted: Union[List[discord.Message], int] = await channel.purge(
            limit=limit,
            before=passed_before,
            after=passed_after,
            check=predicate,
            reason=reason,
        )
    except discord.HTTPException as e:
        await ctx.send(
            f"Unable to {ctx.command.qualified_name}. Error: **{e}** (try a smaller search?)",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
        return
    else:
        await _create_case(
            ctx.bot,
            ctx.guild,
            type="purge",
            reason=reason,
            user=ctx.guild.me,
            moderator=ctx.author,
        )

    # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py#L1814
    spammers: Union[Counter[str], List[Tuple[str, int]]] = Counter(
        m.author.display_name for m in deleted
    )
    deleted: Union[List[discord.Message], int] = len(deleted)
    messages: List[str] = [
        f"{deleted} message{' was' if deleted == 1 else 's were'} removed.",
    ]
    if deleted:
        messages.append("")
        spammers: Union[Counter[str], List[Tuple[str, int]]] = sorted(
            spammers.items(), key=lambda t: t[1], reverse=True
        )
        messages.extend(f"**{name}**: {count}" for name, count in spammers)

    to_send: str = "\n".join(messages)

    if len(to_send) > 2000:
        await ctx.send(
            f"Successfully removed {deleted} messages.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            delete_after=10,
        )
    else:
        await ctx.send(
            to_send,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            delete_after=10,
        )

    await ctx.message.delete(delay=10)


# https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/cleanup/cleanup.py#L163
async def get_message_from_reference(
    channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
    ],
    reference: discord.MessageReference,
) -> Optional[discord.Message]:
    message: Optional[discord.Message] = None
    resolved: Optional[Union[discord.Message, discord.DeletedReferencedMessage]] = (
        reference.resolved
    )
    if resolved and isinstance(resolved, discord.Message):
        message: Optional[discord.Message] = resolved
    elif message := reference.cached_message:
        pass
    else:
        try:
            message: Optional[discord.Message] = await channel.fetch_message(reference.message_id)  # type: ignore
        except discord.NotFound:
            pass
    return message


# https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/cleanup/cleanup.py#L76
async def get_messages_for_deletion(
    *,
    channel: Union[
        discord.TextChannel,
        discord.VoiceChannel,
        discord.StageChannel,
        discord.Thread,
    ],
    number: Optional[int] = None,
    check: Callable[[discord.Message], bool] = lambda x: True,
    limit: Optional[int] = None,
    before: Optional[Union[discord.Message, datetime.datetime]] = None,
    after: Optional[Union[discord.Message, datetime.datetime]] = None,
    delete_pinned: Optional[bool] = False,
) -> List[discord.Message]:
    date: datetime.datetime = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=14, minutes=-5
    )

    def predicate(message: discord.Message) -> bool:
        return (
            check(message) and message.created_at > date and (delete_pinned or not message.pinned)
        )

    if after:
        if isinstance(after, discord.Message):
            after = after.created_at
        after = max(after, date)  # type: ignore

    collected: List[discord.Message] = []

    async for message in channel.history(
        limit=limit, before=before, after=after, oldest_first=False
    ):
        if message.created_at < date:
            break
        if predicate(message):
            collected.append(message)
            if number is not None and number <= len(collected):
                break

    return collected


async def _check_permissions(ctx: commands.GuildContext, perms: Dict[str, bool]):
    is_owner: bool = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved: discord.Permissions = ctx.author.guild_permissions
    return all(getattr(resolved, name, None) == value for name, value in perms.items())


# https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/utils/checks.py#L59
def has_hybrid_permissions(**perms: bool) -> Callable[[T], T]:
    async def predicate(ctx: commands.GuildContext) -> bool:
        return await _check_permissions(ctx, perms)

    def decorator(func: T) -> T:
        commands.permissions_check(predicate)(func)
        discord.app_commands.default_permissions(**perms)(func)
        return func

    return decorator
