"""
MIT License

Copyright (c) 2024-present japandotorg

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
import html
import re
import traceback
from typing import List, Protocol, Self, Union

import discord
import pytz
from chat_exporter.construct.assets.component import Component
from chat_exporter.construct.message import gather_messages
from chat_exporter.ext.cache import clear_cache
from chat_exporter.ext.discord_utils import DiscordUtils
from chat_exporter.ext.html_generator import (
    PARSE_MODE_NONE,
    channel_subject,
    channel_topic,
    fancy_time,
    fill_out,
    meta_data_temp,
    total,
)


class DAOProtocol(Protocol):
    html: str

    def __init__(
        self,
        channel: discord.TextChannel,
        messages: List[discord.Message],
        pytz_timezone: str,
        military_time: bool,
        fancy_times: bool,
    ) -> None: ...

    async def build_transcript(self) -> Self: ...

    async def export_transcript(self, message_html: str, meta_data: str) -> None: ...


class TranscriptDAO(DAOProtocol):
    html: str

    def __init__(
        self,
        channel: discord.TextChannel,
        messages: List[discord.Message],
        pytz_timezone: str,
        military_time: bool,
        fancy_times: bool,
    ) -> None:
        self.channel: discord.TextChannel = channel
        self.messages: List[discord.Message] = messages
        self.military_time: bool = military_time
        self.fancy_times: bool = fancy_times
        self.pytz_timezone = pytz_timezone

        setattr(discord.Guild, "timezone", self.pytz_timezone)

    async def build_transcript(self) -> Self:
        message_html, meta_data = await gather_messages(
            self.messages,
            self.channel.guild,
            self.pytz_timezone,
            self.military_time,
        )
        await self.export_transcript(message_html, meta_data)
        clear_cache()
        Component.menu_div_id = 0
        return self

    async def export_transcript(self, message_html: str, meta_data: str) -> None:
        guild_icon: Union[discord.Asset, str] = (
            self.channel.guild.icon
            if (self.channel.guild.icon and len(self.channel.guild.icon) > 2)
            else DiscordUtils.default_avatar
        )
        guild_name: str = html.escape(self.channel.guild.name)
        timezone: Union[
            pytz.tzinfo.StaticTzInfo, pytz.tzinfo.BaseTzInfo, pytz.tzinfo.DstTzInfo
        ] = pytz.timezone(self.pytz_timezone)
        time_now: str = datetime.datetime.now(timezone).strftime("%e %B %Y at %T (%Z)")
        meta_data_html: str = ""
        for data in meta_data:
            creation_time: str = meta_data[int(data)][1].astimezone(timezone).strftime("%b %d, %Y")  # type: ignore
            joined_time: str = (
                meta_data[int(data)][5].astimezone(timezone).strftime("%b %d, %Y")  # type: ignore
                if meta_data[int(data)][5]
                else "Unknown"
            )
            pattern: str = r"^#\d{4}"
            discrim: str = str(meta_data[int(data)][0][-5:])
            user: str = str(meta_data[int(data)][0])
            meta_data_html += await fill_out(
                self.channel.guild,
                meta_data_temp,
                [
                    ("USER_ID", str(data), PARSE_MODE_NONE),
                    (
                        "USERNAME",
                        user[:-5] if re.match(pattern, discrim) else user,
                        PARSE_MODE_NONE,
                    ),
                    ("DISCRIMINATOR", discrim if re.match(pattern, discrim) else ""),
                    ("BOT", str(meta_data[int(data)][2]), PARSE_MODE_NONE),
                    ("CREATED_AT", str(creation_time), PARSE_MODE_NONE),
                    ("JOINED_AT", str(joined_time), PARSE_MODE_NONE),
                    ("GUILD_ICON", str(guild_icon), PARSE_MODE_NONE),
                    ("DISCORD_ICON", str(DiscordUtils.logo), PARSE_MODE_NONE),
                    ("MEMBER_ID", str(data), PARSE_MODE_NONE),
                    ("USER_AVATAR", str(meta_data[int(data)][3]), PARSE_MODE_NONE),
                    ("DISPLAY", str(meta_data[int(data)][6]), PARSE_MODE_NONE),
                    ("MESSAGE_COUNT", str(meta_data[int(data)][4])),
                ],
            )
        channel_creation_time: str = self.channel.created_at.astimezone(timezone).strftime(
            "%b %d, %Y (%T)"
        )
        raw_channel_topic: str = (
            self.channel.topic
            if isinstance(self.channel, discord.TextChannel) and self.channel.topic
            else ""
        )
        channel_topic_html: str = ""
        if raw_channel_topic:
            channel_topic_html: str = await fill_out(
                self.channel.guild,
                channel_topic,
                [("CHANNEL_TOPIC", html.escape(raw_channel_topic))],
            )
        subject: str = await fill_out(
            self.channel.guild,
            channel_subject,
            [("CHANNEL_NAME", self.channel.name), ("RAW_CHANNEL_TOPIC", str(raw_channel_topic))],
        )
        support = (
            "<div class='meta__support'>"
            "    <a href='https://patreon.com/japandotorg'>DONATE</a>"
            "</div>"
        )
        _fancy_time: str = ""
        if self.fancy_times:
            _fancy_time: str = await fill_out(
                self.channel.guild,
                fancy_time,
                [("TIMEZONE", str(self.pytz_timezone), PARSE_MODE_NONE)],
            )
        self.html: str = await fill_out(
            self.channel.guild,
            total,
            [
                ("SERVER_NAME", f"{guild_name}"),
                ("GUILD_ID", str(self.channel.guild.id), PARSE_MODE_NONE),
                ("SERVER_AVATAR_URL", str(guild_icon), PARSE_MODE_NONE),
                ("CHANNEL_NAME", f"{self.channel.name}"),
                ("MESSAGE_COUNT", str(len(self.messages))),
                ("MESSAGES", message_html, PARSE_MODE_NONE),
                ("META_DATA", meta_data_html, PARSE_MODE_NONE),
                ("DATE_TIME", str(time_now)),
                ("SUBJECT", subject, PARSE_MODE_NONE),
                ("CHANNEL_CREATED_AT", str(channel_creation_time), PARSE_MODE_NONE),
                ("CHANNEL_TOPIC", str(channel_topic_html), PARSE_MODE_NONE),
                ("CHANNEL_ID", str(self.channel.id), PARSE_MODE_NONE),
                ("MESSAGE_PARTICIPANTS", str(len(meta_data)), PARSE_MODE_NONE),
                ("FANCY_TIME", _fancy_time, PARSE_MODE_NONE),
                ("SD", support, PARSE_MODE_NONE),
            ],
        )


class Transcript(TranscriptDAO):
    async def export(self) -> Self:
        if not self.messages:
            self.messages: List[discord.Message] = [
                message async for message in self.channel.history()
            ]
        try:
            return await super().build_transcript()
        except Exception:
            self.html: str = "Whoops! Something went wrong..."
            traceback.print_exc()
            return self
