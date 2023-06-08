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

from __future__ import annotations

import asyncio
import io
import logging
from typing import Any, Dict, Final, List, Literal, Optional

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list
from redbot.core.utils.predicates import MessagePredicate

log: logging.Logger = logging.getLogger("red.seina.massunban")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class MassUnban(commands.Cog):
    """
    Unban all users, or users with a specific ban reason.
    """

    __author__: Final[List[str]] = ["aikaterna", "inthedark.org#0666"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot

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
        user_id: int | None = kwargs.get("user_id")
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

    @commands.command()
    @commands.guild_only()
    @commands.guildowner()
    async def massunban(self, ctx: commands.Context, *, ban_reason: Optional[str] = None):
        """
        Mass unban everyone, or specific people.

        **Arguments**
        - [`ban_reason`] is what the bot looks for in the original ban reason to qualify a user for an unban. It is case-insensitive.

        When [botname] is used to ban a user, the ban reason looks like:
        `action requested by aikaterna (id 154497072148643840). reason: bad person`
        Using `[p]massunban bad person` will unban this user as "bad person" is contained in the original ban reason.
        Using `[p]massunban aikaterna` will unban every user banned by aikaterna, if [botname] was used to ban them in the first place.
        For users banned using the right-click ban option in Discord, the ban reason is only what the mod puts when it asks for a reason, so using the mod name to unban won't work.

        Every unban will show up in your modlog if mod logging is on for unbans. Check `[p]modlogset cases` to verify if mod log creation on unbans is on.
        This can mean that your bot will be ratelimited on sending messages if you unban lots of users as it will create a modlog entry for each unban.
        """
        try:
            banlist: List[discord.BanEntry] = [entry async for entry in ctx.guild.bans()]
        except discord.errors.Forbidden:
            msg = "I need the `Ban Members` permission to fetch the ban list for the guild."
            await ctx.send(msg)
            return
        except (discord.HTTPException, TypeError):
            log.exception("Something went wrong while fetching the ban list!", exc_info=True)
            return

        bancount: int = len(banlist)
        if bancount == 0:
            await ctx.send("No users are banned from this server.")
            return

        unban_count: int = 0
        if not ban_reason:
            warning_string = (
                "Are you sure you want to unban every banned person on this server?\n"
                f"**Please read** `{ctx.prefix}help massunban` **as this action can cause a LOT of modlog messages!**\n"
                "Type `Yes` to confirm, or `No` to cancel."
            )
            await ctx.send(warning_string)
            pred = MessagePredicate.yes_or_no(ctx)
            try:
                await self.bot.wait_for("message", check=pred, timeout=15)
                if pred.result is True:
                    async with ctx.typing():
                        for ban_entry in banlist:
                            await ctx.guild.unban(
                                ban_entry.user,
                                reason=f"Mass Unban requested by {str(ctx.author)} ({ctx.author.id})",
                            )
                            await asyncio.sleep(0.5)
                            unban_count += 1
                else:
                    return await ctx.send("Alright, I'm not unbanning everyone.")
            except asyncio.TimeoutError:
                return await ctx.send(
                    "Response timed out. Please run this command again if you wish to try again."
                )
        else:
            async with ctx.typing():
                for ban_entry in banlist:
                    if not ban_entry.reason:
                        continue
                    if ban_reason.lower() in ban_entry.reason.lower():
                        await ctx.guild.unban(
                            ban_entry.user,
                            reason=f"Mass Unban requested by {str(ctx.author)} ({ctx.author.id})",
                        )
                        await asyncio.sleep(0.5)
                        unban_count += 1

        await ctx.send(f"Done. Unbanned {unban_count} users.")
