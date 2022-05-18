import codecs
import pickle
import re
from datetime import datetime, timedelta, timezone, tzinfo
from typing import Optional

import pytz
from discord import User
from redbot.core import Config

from .utils import CogMixin, mixin_group


class TimezonePreference(CogMixin):
    config: Config

    def setup_self(self):
        self.timezone.setup(self)
        self.config.register_user(timezone=None)

    async def red_get_data_for_user(self, *, user_id):
        if (tz := await self.config.user_by_id(user_id).timezone()) is not None:
            return f"Timezone: `{pickle.loads(tz)}`"

    async def red_delete_data_for_user(self, *, requester, user_id):
        await self.config.user_from_id(user_id).timezone.set(None)

    @mixin_group("preferences", aliases=["tz"], invoke_without_command=True)
    async def timezone(self, ctx, *, tzstr):
        """Set your timezone"""
        if (tz := self.tzstr_to_timezone(tzstr)) is None:
            return await ctx.send(f"Unable to find a timezone matching `{tzstr}`.")
        await self.config.user(ctx.author).timezone.set(self.encode_timezone(tz))
        await ctx.send(f"Your timezone has been set to `{tz.tzname(datetime(2141, 1, 1))}`.")

    @timezone.command(name="clear", aliases=["remove", "rm", "delete", "del"])
    async def tz_clear(self, ctx):
        """Clear your timezone"""
        await self.config.timezone.set(None)
        await ctx.send("Your stored timezone has been cleared.")

    def tzstr_to_timezone(self, tzstr: str) -> Optional[tzinfo]:
        tzstr = tzstr.upper().strip()
        if tzstr in ("EST", "EDT", "ET"):
            return pytz.timezone("America/New_York")
        if tzstr in ("MST", "MDT", "MT"):
            return pytz.timezone("America/North_Dakota/Center")
        if tzstr in ("PST", "PDT", "PT"):
            return pytz.timezone("America/Los_Angeles")
        if tzstr in ("CST", "CDT", "CT"):
            return pytz.timezone("America/Chicago")
        if tzstr in ("JP", "JST", "JT"):
            return pytz.timezone("Japan")
        if tzstr in ("NA", "US"):
            return timezone(timedelta(hours=-8))
        tz_lookup = dict(
            [
                (pytz.timezone(x).localize(datetime.now()).tzname(), pytz.timezone(x))
                for x in pytz.all_timezones
            ]
        )
        if tzstr in tz_lookup:
            return tz_lookup[tzstr]
        if match := re.match(r"^UTC([-+]\d+)$", tzstr):
            return timezone(timedelta(hours=int(match.group(1))))
        for tz in pytz.all_timezones:
            if tzstr in tz.upper().split("/"):
                return pytz.timezone(tz)
        for tz in pytz.all_timezones:
            if tzstr in tz.upper():
                return pytz.timezone(tz)

    def encode_timezone(self, tz: tzinfo) -> str:
        return codecs.encode(pickle.dumps(tz), "base64").decode("utf-8")

    def decode_timezone(self, data: str) -> tzinfo:
        return pickle.loads(codecs.decode(data.encode("utf-8"), "base64"))

    async def get_user_timezone(self, user: User) -> Optional[tzinfo]:
        if not (data := await self.config.user(user).timezone()):
            return
        return self.decode_timezone(data)
