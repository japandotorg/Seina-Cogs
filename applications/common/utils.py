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

from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
    cast,
)

import discord
from redbot.core import app_commands, commands
from redbot.core.bot import Red

if TYPE_CHECKING:
    from ..core import Applications


T = TypeVar("T")


def has_guild_permissions(**perms: bool) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        commands.guild_only()(func)
        commands.admin_or_permissions(**perms)(func)
        app_commands.guild_only()(func)
        app_commands.default_permissions(**perms)(func)
        return func

    return decorator


async def name_auto_complete(
    interaction: discord.Interaction[Red], current: str
) -> List[app_commands.Choice[str]]:
    cog: "Applications" = cast(
        "Applications", interaction.client.get_cog("Applications")
    )  # type: ignore
    return [
        app_commands.Choice(name=name, value=name)
        for name in cog.cache[cast(discord.Guild, interaction.guild).id].keys()
        if current.lower() in name.lower()
    ][:25]


class GuildInteraction(discord.Interaction[Red]):
    if TYPE_CHECKING:
        guild_id: int
        guild: discord.Guild
        channel: discord.abc.GuildChannel
        user: discord.Member
        message: discord.Message


class Threads(TypedDict):
    toggle: bool
    custom: str


class Mentions(TypedDict):
    users: bool
    roles: bool
    everyone: bool


class Notifications(TypedDict):
    toggle: bool
    content: str
    mentions: Mentions
    channels: Sequence[int]
    

class VoterSettings(TypedDict):
    threshold: int
    up: str
    down: str
    null: str


class AppSettings(TypedDict):
    name: str
    description: str
    channel: int
    message: str
    color: str
    emoji: str
    open: bool
    cooldown: int
    dm: bool
    thread: Union[bool, Threads]
    notifications: Notifications
    voters: VoterSettings


class Roles(TypedDict):
    blacklist: List[int]
    whitelist: List[int]


class Tickets(TypedDict):
    category: Optional[int]
    message: str
    toggle: bool


class ChoiceButtonType(TypedDict):
    label: Optional[str]
    emoji: Optional[str]


class ChoiceButtons(TypedDict):
    yes: ChoiceButtonType
    no: ChoiceButtonType
    required: bool


class Buttons(TypedDict):
    label: Optional[str]
    emoji: str
    style: str
    choice: ChoiceButtons


class Post(TypedDict):
    id: int
    channel: int


class Voters(TypedDict):
    up: List[int]
    down: List[int]
    null: List[int]


class Response(TypedDict):
    id: str
    channel: int
    user: int
    answers: Dict[str, str]
    status: str
    time: float
    ticket: int
    voters: Voters


class TypedConfig(TypedDict):
    settings: AppSettings
    questions: Dict[str, str]
    roles: Roles
    tickets: Tickets
    buttons: Buttons
    posts: List[Post]
    responses: List[Response]
