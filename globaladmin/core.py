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

import logging
from io import BytesIO
from typing import Any, Dict, Final, List, Literal, Type, TypeVar, Union

import discord
from discord import Object, User
from redbot.core import checks, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list, inline, pagify

from .objects import CogSettings
from .utils import get_user_confirmation

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

RTT = TypeVar("RTT", bound="RequestType")

log: logging.Logger = logging.getLogger("red.seina-cogs.globaladmin")


class GlobalAdmin(commands.Cog):
    """
    Set up authentication for admins for other cogs via tsutils
    """

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.bot: Red = bot

        self.settings: GlobalAdminSettings = GlobalAdminSettings(
            cog_name="globaladmin",
            bot=Red,
        )

    @classmethod
    async def initialize(cls, bot: Red) -> None:
        return await bot.wait_until_red_ready()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)

    async def red_get_data_for_user(self, *, user_id: int) -> Dict[str, BytesIO]:
        """
        Get a user's personal data.
        """
        data: Final[str] = f"No data is stored for user with ID {user_id}.\n"
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(
        self, *, requester: Type[RTT], user_id: int
    ) -> Dict[str, BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        data: Final[str] = f"No data is stored for user with ID {user_id}.\n"
        return {"user_data.txt": BytesIO(data.encode())}

    @commands.group(aliases=["ga", "gadmin"], invoke_without_command=True)
    @checks.is_owner()
    async def globaladmin(self, ctx: commands.Context) -> None:
        """
        Global Admin Commands
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help()

    @globaladmin.group(aliases=["auths"], invoke_without_command=True)
    async def perms(self, ctx: commands.Context):
        """
        Perm commands
        Cogs automatically register their perms with gadmin; you don't need to add them
        """
        if ctx.invoked_subcommand is None:
            return await ctx.send_help()

    def register_perm(self, perm_name: str, default: bool = False) -> None:
        self.settings.add_perm(perm_name, default)

    @perms.command()
    async def reset(self, ctx: commands.Context, perm_name: str) -> None:
        """
        Restore defaults for a perm for all users
        """
        if not await get_user_confirmation(
            ctx, "Are you sure you want to reset this perm to defaults?"
        ):
            return

        self.settings.refresh_perm(perm_name)

        await ctx.tick()

    @perms.command()
    async def unregister(self, ctx: commands.Context, perm_name: str) -> None:
        """
        Completely remove a perm from storage
        """
        if not await get_user_confirmation(ctx, "Are you sure you want to unregister this perm?"):
            return

        self.settings.refresh_perm(perm_name)
        self.settings.rm_perm(perm_name)

        await ctx.tick()

    @perms.command(name="list")
    async def perm_list(self, ctx: commands.Context) -> None:
        """
        List the avaliable perms
        """
        msg: str = "Perms:\n"
        mlen: int = max(len(k) for k in self.settings.get_perms().keys())

        for perm, default in self.settings.get_perms().items():
            msg += f' - {perm}{" " * (mlen - len(perm) + 3)}(default: {default})\n'
        for page in pagify(msg):
            await ctx.send(box(page))

    @globaladmin.command(aliases=["setperm", "setadmin", "addadmin", "addperm"])
    async def grant(
        self, ctx: commands.Context, user: discord.User, perm: str, value: bool = True
    ) -> None:
        """
        Grant a user a perm
        """
        if self.settings.add_user_perm(user.id, perm, value):
            await ctx.send(inline("Invalid perm name."))
            return

        await ctx.tick()

    @globaladmin.command()
    async def deny(
        self, ctx: commands.Context, user: discord.User, perm: str, value: bool = False
    ) -> None:
        """
        Deny a user a perm
        """
        if self.settings.add_user_perm(user.id, perm, value):
            await ctx.send(inline("Invalid perm name."))
            return

        await ctx.tick()

    @globaladmin.command()
    async def listusers(self, ctx: commands.Context, perm_name: str) -> None:
        """
        List all users with a perm
        """
        us = self.settings.get_users_with_perm(perm_name)
        us = [str(self.bot.get_user(u) or f"Unknown ({u})") for u in us]

        if not us:
            await ctx.send(inline("No users have this perm."))
        for page in pagify("\n".join(us)):
            await ctx.send(box(page))

    def auth_check(self, user: Union[Object, User], perm_name: str, default: bool = False) -> bool:
        return self.settings.get_perm(user.id, perm_name, default=default)


class GlobalAdminSettings(CogSettings):
    def make_default_settings(self) -> Dict[str, Dict]:
        return {
            "perms": {},
            "users": {},
        }

    def add_user_perm(
        self, user_id: int, perm: str, value: bool = True
    ) -> Union[Literal[-1], None]:
        if perm not in self.bot_settings["perms"]:
            return -1
        if user_id not in self.bot_settings["users"]:
            self.bot_settings["users"][user_id] = {}
        self.bot_settings["users"][user_id][perm] = value
        self.save_settings()

    def add_perm(self, perm: str, default: bool = False) -> None:
        self.bot_settings["perms"][perm] = default
        self.save_settings()

    def rm_perm(self, perm: str) -> None:
        if perm in self.bot_settings["perms"]:
            del self.bot_settings["perms"][perm]
        self.save_settings()

    def refresh_perm(self, perm: str) -> None:
        for user in self.bot_settings["users"]:
            if perm in self.bot_settings["users"][user]:
                del self.bot_settings["users"][user][perm]
        self.save_settings()

    def rm_user_perm(self, user_id: int, perm: str) -> Union[Literal[-1], None]:
        if perm not in self.bot_settings["perms"]:
            return -1
        if user_id not in self.bot_settings["users"]:
            return
        if perm not in self.bot_settings["users"][user_id]:
            return
        del self.bot_settings["users"][user_id][perm]
        self.save_settings()

    def get_perm(self, user_id: int, perm: str, default: bool = False):
        defaults: dict = {}
        defaults |= self.bot_settings["perms"]
        defaults |= self.bot_settings["users"].get(user_id, {})
        return defaults.get(perm, default)

    def get_perms(self):
        return self.bot_settings["perms"]

    def get_users_with_perm(self, perm: str) -> List:
        return [
            user for user in self.bot_settings["users"] if perm in self.bot_settings["users"][user]
        ]
