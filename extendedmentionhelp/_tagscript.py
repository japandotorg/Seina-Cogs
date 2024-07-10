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

from typing import Dict, Final, List, Union, final

import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_number

message: Final[
    str
] = """
{embed({
    "title": "Need Help?",
    "url": "{invite}",
    "color": "{color}",
    "fields": [
        {
            "name": "**Use the following to get help:**",
            "value": "> `{prefix}help`",
            "inline": false
        },
        {
            "name": "**My prefixes in this server are:**",
            "value": "> {prefixes}",
            "inline": false
        }
    ]
})}
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
