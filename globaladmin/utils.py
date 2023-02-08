"""
MIT License

Copyright (c) 2022-present japandotorg

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
from typing import Any, Literal, Optional, Union, Final

import discord
from discord import User
from redbot.core.bot import Red

SendableEmoji = Union[str, discord.Emoji]

YES_EMOJI: Final[str] = "\N{WHITE HEAVY CHECK MARK}"
NO_EMOJI: Final[str] = "\N{CROSS MARK}"


async def get_user_preference(
    bot: Red, user: User, pref: str, *, unloaded_default: Any = None
) -> Optional[Any]:
    if pref in {"timezone"}:
        raise ValueError("Invalid preference. Use the cog method to get this.")

    cog: Any = bot.get_cog("UserPreferences")
    if cog is None:
        return unloaded_default
    return await cog.config.user(user).get_raw(pref)


async def get_user_confirmation(
    ctx,
    text: str,
    yes_emoji: SendableEmoji = YES_EMOJI,
    no_emoji: SendableEmoji = NO_EMOJI,
    timeout: int = 10,
    force_delete: Optional[bool] = None,
    show_feedback: bool = False,
) -> Literal[True, False, None]:
    msg = await ctx.send(text)
    asyncio.create_task(msg.add_reaction(yes_emoji))
    asyncio.create_task(msg.add_reaction(no_emoji))

    def check(reaction, user):
        return (
            str(reaction.emoji) in [yes_emoji, no_emoji]
            and user.id == ctx.author.id
            and reaction.message.id == msg.id
        )

    ret = False
    try:
        r, u = await ctx.bot.wait_for("reaction_add", check=check, timeout=timeout)
        if r.emoji == yes_emoji:
            ret = True
    except asyncio.TimeoutError:
        ret = None

    do_delete = force_delete
    if do_delete is None:
        do_delete = await get_user_preference(
            ctx.bot, ctx.author, "delete_confirmation", unloaded_default=True
        )

    if do_delete:
        try:
            await msg.delete()
        except discord.Forbidden:
            pass

        if show_feedback:
            if ret is True:
                await ctx.react_quietly(yes_emoji)
            elif ret is False:
                await ctx.react_quietly(no_emoji)
    else:
        if ret is not True:
            await msg.remove_reaction(yes_emoji, ctx.me)
        if ret is not False:
            await msg.remove_reaction(no_emoji, ctx.me)

    return ret
