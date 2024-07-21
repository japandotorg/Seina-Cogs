"""
MIT License

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

import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Union, cast

import discord
from redbot.core import commands
from typing_extensions import ParamSpec

from .constants import MAX_LEVEL, STARTING_EXP

P = ParamSpec("P")

log: logging.Logger = logging.getLogger("red.seina.battleroyale.utils")

__all__ = (
    "Emoji",
    "exceptions",
    "_get_attachments",
    "_cooldown",
)


def generate_max_exp_for_level(level: int, increase: int, start: int = STARTING_EXP) -> int:
    if level <= 0:
        raise ValueError("Level must be greater than 0.")
    exp: float = start
    for _ in range(1, level):
        exp *= 1 + increase / 100
    return int(exp)


def maybe_update_level(exp: int, max_exp: int, level: int) -> int:
    if level >= MAX_LEVEL:
        return level
    if exp >= max_exp:
        level += 1
    return level


def get_exp_percentage(exp: int, max_exp: int) -> float:
    if max_exp <= 0:
        raise ValueError("Max exp must be greater than 0.")
    percentage: float = (exp / max_exp) * 100
    return percentage


def exceptions(func: Callable[P, Any]) -> Callable[P, Any]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception:
            log.exception("Exception in function %s", func.__name__)
            raise

    return wrapper


def _get_attachments(ctx: commands.Context) -> List:
    content = []
    if ctx.message.attachments:
        attachments = list(ctx.message.attachments)
        content.extend(attachments)
    if (
        ctx.message.reference is not None
        and ctx.message.reference.resolved is not None
        and not isinstance(ctx.message.reference.resolved, discord.DeletedReferencedMessage)
    ):
        attachments = list(ctx.message.reference.resolved.attachments)
        content.extend(attachments)
    return content


class Emoji:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.name = data["name"]
        self.id = data.get("id", None)
        self.animated = data.get("animated", None)
        self.custom = self.id is not None

    @classmethod
    def from_data(cls, data: Union[str, Dict[str, Any]]):
        log.debug(data)
        if not data:
            return None
        if isinstance(data, str):
            return cls({"name": data})
        return cls(data)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "id": self.id}

    def as_emoji(self) -> str:
        if not self.custom:
            return self.name
        animated = "a" if self.animated else ""
        return f"<{animated}:{self.name}:{self.id}>"


def _cooldown(ctx: commands.Context) -> Optional[commands.Cooldown]:
    if ctx.author.id in ctx.bot.owner_ids:
        return None
    return commands.Cooldown(1, ctx.cog._cooldown)  # type: ignore


def guild_roughly_chunked(guild: discord.Guild) -> bool:
    return len(guild.members) / cast(int, guild.member_count) > 0.9


def truncate(text: str, *, max: int) -> str:
    if len(text) <= max:
        return text
    truncated: str = text[: max - 3]
    return truncated + "..."
