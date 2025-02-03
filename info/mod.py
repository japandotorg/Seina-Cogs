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
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER**
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/names.py

from typing import List, Optional, Tuple, cast

import discord
from redbot.cogs.mod.mod import Mod
from redbot.core.bot import Red
from redbot.core.utils.common_filters import escape_spoilers_and_mass_mentions


class ModUtils:
    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

    def handle_custom(self, user: discord.Member) -> Tuple[Optional[str], discord.ActivityType]:
        a = [c for c in user.activities if c.type == discord.ActivityType.custom]
        if not a:
            return None, discord.ActivityType.custom
        a = a[0]
        c_status = None
        if not a.name and not a.emoji:  # type: ignore
            return None, discord.ActivityType.custom
        elif a.name and a.emoji:  # type: ignore
            c_status = "**Custom:** {emoji} {name}".format(emoji=a.emoji, name=a.name)  # type: ignore
        elif a.emoji:  # type: ignore
            c_status = "**Custom:** {emoji}".format(emoji=a.emoji)  # type: ignore
        elif a.name:
            c_status = "**Custom:** {name}".format(name=a.name)
        return c_status, discord.ActivityType.custom

    def handle_playing(self, user: discord.Member) -> Tuple[Optional[str], discord.ActivityType]:
        p_acts = [c for c in user.activities if c.type == discord.ActivityType.playing]
        if not p_acts:
            return None, discord.ActivityType.playing
        p_act = p_acts[0]
        act = "**Playing:** {name}".format(name=p_act.name)
        return act, discord.ActivityType.playing

    def handle_streaming(self, user: discord.Member) -> Tuple[Optional[str], discord.ActivityType]:
        s_acts = [c for c in user.activities if c.type == discord.ActivityType.streaming]
        if not s_acts:
            return None, discord.ActivityType.streaming
        s_act = s_acts[0]
        if isinstance(s_act, discord.Streaming):
            act = "**Streaming:** [{name}{sep}{game}]({url})".format(
                name=discord.utils.escape_markdown(s_act.name),
                sep=" | " if s_act.game else "",
                game=discord.utils.escape_markdown(s_act.game) if s_act.game else "",
                url=s_act.url,
            )  # type: ignore
        else:
            act = "**Streaming:** {name}".format(name=s_act.name)
        return act, discord.ActivityType.streaming

    def handle_listening(self, user: discord.Member) -> Tuple[Optional[str], discord.ActivityType]:
        l_acts = [c for c in user.activities if c.type == discord.ActivityType.listening]
        if not l_acts:
            return None, discord.ActivityType.listening
        l_act = l_acts[0]
        if isinstance(l_act, discord.Spotify):
            act = "**Listening:** [{title}{sep}{artist}]({url})".format(
                title=discord.utils.escape_markdown(l_act.title),
                sep=" | " if l_act.artist else "",
                artist=discord.utils.escape_markdown(l_act.artist) if l_act.artist else "",
                url=f"https://open.spotify.com/track/{l_act.track_id}",
            )
        else:
            act = "Listening: {title}".format(title=l_act.name)
        return act, discord.ActivityType.listening

    def handle_watching(self, user: discord.Member) -> Tuple[Optional[str], discord.ActivityType]:
        w_acts = [c for c in user.activities if c.type == discord.ActivityType.watching]
        if not w_acts:
            return None, discord.ActivityType.watching
        w_act = w_acts[0]
        act = "**Watching:** {name}".format(name=w_act.name)
        return act, discord.ActivityType.watching

    def handle_competing(self, user: discord.Member) -> Tuple[Optional[str], discord.ActivityType]:
        w_acts = [c for c in user.activities if c.type == discord.ActivityType.competing]
        if not w_acts:
            return None, discord.ActivityType.competing
        w_act = w_acts[0]
        act = "**Competing in:** {competing}".format(competing=w_act.name)
        return act, discord.ActivityType.competing

    def get_status_string(self, user: discord.Member) -> str:
        string = ""
        for a in [
            self.handle_custom(user),
            self.handle_playing(user),
            self.handle_listening(user),
            self.handle_streaming(user),
            self.handle_watching(user),
            self.handle_competing(user),
        ]:
            status_string, status_type = a
            if status_string is None:
                continue
            string += f"{status_string}\n"
        return string

    async def get_names(
        self, user: discord.Member
    ) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        if not (cog := cast(Optional[Mod], self.bot.get_cog("Mod"))):
            return None, None
        usernames: List[str] = await cog.config.user(user).past_names()
        nicks: List[str] = await cog.config.member(user).past_nicks()
        usernames: List[str] = list(
            map(escape_spoilers_and_mass_mentions, filter(None, usernames))
        )
        nicks: List[str] = list(map(escape_spoilers_and_mass_mentions, filter(None, nicks)))
        return usernames, nicks
