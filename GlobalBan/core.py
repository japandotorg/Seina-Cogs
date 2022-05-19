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

import datetime
import logging
from io import BytesIO
from typing import Any

import discord
from redbot.core import Config, checks, commands, modlog
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list, inline, pagify

from .utils import auth_check, get_user_confirmation

log = logging.getLogger("red.seina-cogs.globalban")


class GlobalBan(commands.Cog):
    """
    Global Ban a user across multiple servers.
    """

    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.2"

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.config = Config.get_conf(self, identifier=66642069)
        self.config.register_global(banned={}, opted=[])
        self.config.register_guild(banlist=[])

        gadmin: Any = bot.get_cog("GlobalAdmin")
        if gadmin:
            gadmin.register_perm("globalban")

    @classmethod
    async def initialize(self, bot: Red):
        await bot.wait_until_red_ready()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)

    async def red_get_data_for_user(self, *, user_id):
        """
        Get a user's personal data.
        """
        data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """
        Delete a user's personal data.

        No personal data is stored in this cog.
        """
        return

    @commands.group(aliases=["gb", "gban"])
    async def globalban(self, ctx):
        """
        Global ban related commands.
        """

    @globalban.command()
    @checks.admin_or_permissions(administrator=True)
    async def optin(self, ctx):
        """
        Opt your server in to the Global Ban system.
        """
        async with self.config.opted() as opted:
            if ctx.guild.id in opted:
                await ctx.send("This guild is already opted in.")
                return
            if not await get_user_confirmation(
                ctx,
                "This will ban all users on the global ban list. Are you sure you want to opt in?",
            ):
                return
            opted.append(ctx.guild.id)
        await self.config.guild(ctx.guild).banlist.set(
            [be.user.id for be in await ctx.guild.bans()]
        )
        async with ctx.typing():
            await self.update_gbs()
        await ctx.tick()

    @globalban.command()
    @checks.admin_or_permissions(administrator=True)
    async def optout(self, ctx):
        """
        Opt your server out of the Global Ban system.
        """
        async with self.config.opted() as opted:
            if ctx.guild.id not in opted:
                await ctx.send("This guild is already opted out.")
                return
            if not await get_user_confirmation(
                ctx,
                "This will remove all bans that intersect"
                " with the global ban list. Are you sure"
                " you want to opt out?",
            ):
                return
            opted.remove(ctx.guild.id)
        async with ctx.typing():
            await self.remove_gbs_guild(ctx.guild.id)
        await ctx.tick()

    @globalban.command()
    @auth_check("globalban")
    async def ban(self, ctx, user_id: int, *, reason=""):
        """
        Globally Ban a user across all opted-in servers.
        """
        async with self.config.banned() as banned:
            banned[str(user_id)] = reason
        async with ctx.typing():
            await self.update_gbs()
        await ctx.tick()

    @globalban.command()
    @auth_check("globalban")
    async def editreason(self, ctx, user_id: int, *, reason=""):
        """Edit a user's ban reason."""
        async with self.config.banned() as banned:
            if str(user_id) not in banned:
                await ctx.send("This user is not banned.")
                return
            if reason == "" and not await get_user_confirmation(
                ctx, "Are you sure you want to remove the reason?"
            ):
                return
            banned[str(user_id)] = reason
        await ctx.tick()

    @globalban.command()
    @auth_check("globalban")
    @checks.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Globally Unban a user across all opted-in servers."""
        async with self.config.banned() as banned:
            if str(user_id) in banned:
                del banned[str(user_id)]
        async with ctx.typing():
            await self.remove_gbs_user(user_id)
        await ctx.tick()

    @globalban.command(name="list")
    @auth_check("globalban")
    async def _list(self, ctx):
        """Check who're on the global ban list."""
        o = "\n".join(k + "\t" + v for k, v in (await self.config.banned()).items())
        if not o:
            await ctx.send(inline("There are no banned users."))
            return
        for page in pagify(o):
            await ctx.send(box(page))

    async def update_gbs(self, ctx, **kwargs):
        for gid in await self.config.opted():
            guild = self.bot.get_guild(int(gid))

            if guild is None:
                continue

            for uid, reason in (await self.config.banned()).items():
                try:
                    if int(uid) in [b.user.id for b in await guild.bans()]:
                        async with self.config.guild(guild).banlist() as banlist:
                            if int(uid) not in banlist:
                                banlist.append(uid)
                        continue
                except (AttributeError, discord.Forbidden):
                    log.exception(f"Error with guild with id '{gid}'")
                    continue
                m = guild.get_member(int(uid))

                try:
                    if m is None:
                        try:
                            await guild.ban(
                                discord.Object(id=uid),
                                reason=f"Global ban initiated by {ctx.author} with reason: {reason}",
                                delete_message_days=0,
                            )
                        except discord.errors.NotFound:
                            pass
                    else:
                        await guild.ban(
                            m,
                            reason=f"Global ban initiated by {ctx.author} with reason: {reason}",
                            delete_message_days=0,
                        )
                        
                    await modlog.create_case(
                        bot=self.bot,
                        guild=guild,
                        created_at=datetime.datetime.now(datetime.timezone.utc),
                        action_type="globalban",
                        user=m,
                        reason=f"Global ban initiated by {ctx.author} with reason: {reason}",
                    )

                except discord.Forbidden:
                    log.warning(
                        "Failed to ban user with ID {} in guild {}".format(uid, guild.name)
                    )

    async def remove_gbs_guild(self, gid):
        guild = self.bot.get_guild(int(gid))

        for ban in await guild.bans():
            user = ban.user

            if (
                str(user.id) not in await self.config.banned()
                or user.id in await self.config.guild(guild).banlist()
            ):
                continue

            try:
                await guild.unban(user)
            except discord.Forbidden:
                pass

    async def remove_gbs_user(self, uid):
        for gid in await self.config.opted():
            guild = self.bot.get_guild(int(gid))

            if guild is None:
                continue

            if uid in await self.config.guild(guild).banlist():
                continue

            try:
                users = [b.user for b in await guild.bans() if b.user.id == int(uid)]
            except (AttributeError, discord.Forbidden):
                log.exception(f"Error with guild with id '{gid}'")
                continue

            if users:
                try:
                    await guild.unban(users[0])
                except discord.Forbidden:
                    pass
