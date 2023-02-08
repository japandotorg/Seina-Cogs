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
import pickle
from io import BytesIO
from typing import Any, Dict, Literal, TypeVar, Type, Final, List

from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.commands import Context
from redbot.core.utils.chat_formatting import humanize_list

from .preferences.timezone import TimezonePreference as TimezonePreference
from .preferences.util_mixin import UtilsPreference as UtilsPreference

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

RTT = TypeVar("RTT", bound="RequestType")

log: logging.Logger = logging.getLogger("red.seina-cogs.userpreferences")


class UserPreferences(TimezonePreference, UtilsPreference):
    """Stores user Preferences for users."""
    
    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, identifier=6969420666420)
        self.setup_mixins()
        
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
        """Get a user's personal data."""
        data = []

        if (tz := await self.config.user_by_id(user_id).timezone()) is not None:
            data.append(f"Timezone: `{pickle.loads(tz)}`")

        data = "\n".join(await self.get_mixin_user_data(user_id))
        if not data:
            data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester: Type[RTT], user_id: int) -> None:
        """Delete a user's personal data."""
        await self.delete_mixin_user_data(requester, user_id)

    @commands.group(aliases=["preference", "prefs", "pref"], invoke_without_command=True)
    async def preferences(self, ctx: Context) -> None:
        """Set user preferences"""
        if ctx.invokeed_subcommand is None:
            return await ctx.send_help()
