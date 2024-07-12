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
from typing import Any, Dict, Final, List, Union, cast, final

import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, humanize_number


message: Final[
    str
] = """
{embed(description):You're not allowed to send messages in {bot(mention)}'s dms.}
{embed(color):{color}}
"""

command_message: Final[
    str
] = """
{embed(description):You're not allowed to use the {command(name)} command in {bot(mention)}'s dms.}
{embed(color):{color}}
"""

TAGSCRIPT_LIMIT: Final[int] = 10_000

blocks: List[tse.Block] = [tse.EmbedBlock(), tse.AssignmentBlock(), tse.LooseVariableGetterBlock()]
engine: tse.AsyncInterpreter = tse.AsyncInterpreter(blocks)


async def process_tagscript(
    content: str, seed_variables: Dict[str, tse.Adapter] = {}
) -> Dict[str, Union[str, discord.Embed]]:
    output: tse.Response = await engine.process(content, seed_variables)
    kwargs: Dict[str, Union[str, discord.Embed]] = {}
    if output.body:
        kwargs["content"] = output.body[:2000]
    if embed := output.actions.get("embed"):
        kwargs["embed"] = embed
    return kwargs


def validate_tagscript(tagscript: str) -> bool:
    length = len(tagscript)
    if length > TAGSCRIPT_LIMIT:
        raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
    return True


class TagError(Exception):
    """
    Base exception class.
    """


@final
class TagCharacterLimitReached(TagError):
    """Raised when the TagScript character limit is reached."""

    def __init__(self, limit: int, length: int):
        super().__init__(
            f"TagScript cannot be longer than {humanize_number(limit)} (**{humanize_number(length)}**)."
        )


@final
class TagScriptConverter(commands.Converter[str]):
    async def convert(self, ctx: commands.Context, argument: str) -> str:
        try:
            validate_tagscript(argument)
        except TagError as error:
            raise commands.BadArgument(str(error))
        return argument


class UserAdapter(tse.Adapter):
    def __init__(self, base: discord.User) -> None:
        self.object: discord.User = base
        created_at: datetime.datetime = getattr(
            base, "created_at", None
        ) or discord.utils.snowflake_time(base.id)
        self._attributes: Dict[str, Any] = {
            "id": self.object.id,
            "created_at": created_at,
            "timestamp": int(created_at.timestamp()),
            "name": getattr(base, "name", str(base)),
            "nick": self.object.display_name,
            "avatar": self.object.display_avatar.url,
            "mention": self.object.mention,
        }

    def __repr__(self) -> str:
        return "<{} object={}>".format(type(self).__qualname__, self.object)

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.object.name
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # type: ignore
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = str(value) if value is not None else None  # type: ignore
        return tse.escape_content(return_value) if should_escape else return_value


class DMChannelAdapter(tse.Adapter):
    def __init__(self, base: discord.DMChannel) -> None:
        self.object: discord.DMChannel = base
        created_at: datetime.datetime = getattr(
            base, "created_at", None
        ) or discord.utils.snowflake_time(base.id)
        self._attributes: Dict[str, Any] = {
            "id": self.object.id,
            "created_at": created_at,
            "jump_url": self.object.jump_url,
        }

    def __repr__(self) -> str:
        return "<{} object={}>".format(type(self).__qualname__, self.object)

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.object.jump_url
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # type: ignore
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = str(value) if value is not None else None  # type: ignore
        return tse.escape_content(return_value) if should_escape else return_value


class CommandAdapter(tse.Adapter):
    def __init__(self, base: commands.Command) -> None:
        self.object: commands.Command = base
        self._attributes: Dict[str, Any] = {
            "name": self.object.name,
            "cog_name": getattr(self.object, "cog_name", None),
            "description": getattr(self.object, "description", None),
            "aliases": humanize_list(getattr(self.object, "aliases", [])),
            "qualified_name": self.object.qualified_name,
        }

    def __repr__(self) -> str:
        return "<{} object={}>".format(type(self).__qualname__, self.object)

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.object.qualified_name
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # type: ignore
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = str(value) if value is not None else None  # type: ignore
        return tse.escape_content(return_value) if should_escape else return_value


class BotAdapter(tse.Adapter):
    def __init__(self, base: Red) -> None:
        self.object: Red = base
        self.user: discord.ClientUser = cast(discord.ClientUser, self.object.user)
        created_at: datetime.datetime = getattr(
            self.user, "created_at", None
        ) or discord.utils.snowflake_time(self.user.id)
        self._attributes: Dict[str, Any] = {
            "id": self.user.id,
            "name": self.user.name,
            "nick": self.user.display_name,
            "mention": self.user.mention,
            "avatar": self.user.display_avatar.url,
            "created_at": created_at,
            "verified": self.user.verified,
        }

    def __repr__(self) -> str:
        return "<{} object={}>".format(type(self).__qualname__, self.object)

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.user.name
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # type: ignore
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = str(value) if value is not None else None  # type: ignore
        return tse.escape_content(return_value) if should_escape else return_value
