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
from typing import Any, Dict, Final, List, Optional, Tuple, Union, final

import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list, humanize_number

__all__: Tuple[str, ...] = (
    "_default_add",
    "_default_remove",
)

_default_add: Final[
    str
] = """
{embed({
    "title": "Vote Added!",
    "url": "{poll(jump_url)}",
    "thumbnail": {"url": "{member(avatar)}"},
    "color": "{color}",
    "description": "**Question**: {poll}\n\n{member(mention)} just voted for {answer}.",
    "fields": [
        {
            "name": "Voted On:",
            "value": "<t:{time}> ( <t:{time}:R> )",
            "inline": false
        },
        {
            "name": "{answer(vote_count)} Voters On This Answer:",
            "value": "{answer(voters)}",
            "inline": false
        }
    ]
})}
"""

_default_remove: Final[
    str
] = """
{embed({
    "title": "Vote Removed!",
    "url": "{poll(jump_url)}",
    "thumbnail": {"url": "{member(avatar)}"},
    "color": "{color}",
    "description": "**Question**: {poll}\n\n{member(mention)} just removed their vote from {answer}.",
    "fields": [
        {
            "name": "Removed On:",
            "value": "<t:{time}> ( <t:{time}:R> )",
            "inline": false
        },
        {
            "name": "{answer(vote_count)} Voters On This Answer:",
            "value": "{answer(voters)}",
            "inline": false
        }
    ]
})}
"""

TAGSCRIPT_LIMIT: Final[int] = 10_000

blocks: List[tse.Block] = [tse.EmbedBlock(), tse.AssignmentBlock(), tse.LooseVariableGetterBlock()]
engine: tse.Interpreter = tse.Interpreter(blocks)


def process_tagscript(
    content: str, seed_variables: Dict[str, tse.Adapter] = {}
) -> Dict[str, Union[str, discord.Embed]]:
    output: tse.Response = engine.process(content, seed_variables)
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


class PollAdapter(tse.Adapter):
    def __init__(self, base: discord.Poll) -> None:
        self.object: discord.Poll = base
        created_at: Optional[datetime.datetime] = getattr(
            self.object, "created_at", getattr(self.object.message, "created_at", None)
        )
        expires_at: Optional[datetime.datetime] = getattr(self.object, "expires_at", None)
        answers: List[str] = [
            "`{0.id} :` {0.emoji} {0.text}".format(answer) for answer in self.object.answers
        ]
        self._attributes: Dict[str, Any] = {
            "created_at": created_at,
            "created_timestamp": int(created_at.timestamp()) if created_at else None,
            "expires_at": expires_at,
            "expires_timestamp": int(expires_at.timestamp()) if expires_at else None,
            "answers": "\n".join(answers)[:1024],
            "answers_count": len(answers),
            "question": self.object.question,
            "emoji": (
                question.emoji
                if isinstance((question := self.object.question), discord.PollMedia)
                else None
            ),
            "jump_url": message.jump_url if (message := self.object.message) else None,
            "total_votes": self.object.total_votes,
            "ended": self.object.is_finalised(),
        }

    def __repr__(self) -> str:
        return "<{} object={}>".format(type(self).__qualname__, self.object)

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.object.question
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # type: ignore
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = str(value) if value is not None else None  # type: ignore
        return tse.escape_content(return_value) if should_escape else return_value


class PollAnswerAdapter(tse.Adapter):
    def __init__(
        self, base: discord.PollAnswer, voters: List[Union[discord.User, discord.Member]]
    ) -> None:
        self.object: discord.PollAnswer = base
        self.voters: List[Union[discord.User, discord.Member]] = voters
        self._attributes: Dict[str, Any] = {
            "id": self.object.id,
            "emoji": getattr(self.object, "emoji", None),
            "answer": self.object.text,
            "vote_count": len(self.voters),
            "voters": (
                humanize_list([u.mention for u in self.voters])[:1024] if self.voters else None
            ),
        }

    def __repr__(self) -> str:
        return "<{} object={}>".format(type(self).__qualname__, self.object)

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.object.text
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # type: ignore
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = str(value) if value is not None else None  # type: ignore
        return tse.escape_content(return_value) if should_escape else return_value
