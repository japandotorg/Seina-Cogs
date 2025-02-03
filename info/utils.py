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

from typing import Dict, Final, List, Optional

import discord
from redbot.core import app_commands
from redbot.core.bot import Red

SEINA: Final[int] = 759180080328081450  # to auto add emojis to my bot(s)


def guild_only_and_has_embed_links(interaction: discord.Interaction[Red]) -> bool:
    if not interaction.guild:
        raise app_commands.NoPrivateMessage()
    if not interaction.app_permissions.embed_links:
        raise app_commands.BotMissingPermissions(["embed_links"])
    if not interaction.user.guild_permissions.embed_links:  # type: ignore
        raise app_commands.MissingPermissions(["embed_links"])
    return True


def get_perms(perms: discord.Permissions) -> List[str]:
    if perms.administrator:
        return ["Administrator"]
    gp: Dict[str, bool] = dict(
        {x for x in perms if x[1] is True} - set(discord.Permissions(521942715969))
    )
    return [p.replace("_", " ").title() for p in gp]


def get_roles(member: discord.Member) -> Optional[List[str]]:
    roles: List[discord.Role] = list(reversed(member.roles))[:-1]
    if roles:
        return [x.mention for x in roles]


def truncate(text: str, *, max: int = 2000):
    if len(text) <= max:
        return text
    truncated: str = text[: max - 3]
    return truncated + "..."
