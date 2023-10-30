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

from typing import Final, List, Dict, Union, final

import discord
from redbot.core.utils.chat_formatting import humanize_number

import TagScriptEngine as tse

TAGSCRIPT_LIMIT: Final[int] = 10_000

blocks: List[tse.Block] = [
    tse.LooseVariableGetterBlock(),
    tse.AssignmentBlock(),
    tse.EmbedBlock(),
]

tagscript_engine: tse.Interpreter = tse.Interpreter(blocks)

freeloader_message: str = "You have been banned with a {action} of {time} days in the server **{server(name)}**. Reason: **Freeloading**."


def process_tagscript(
    content: str, seed_variables: Dict[str, tse.Adapter] = {}
) -> Dict[str, Union[str, discord.Embed]]:
    output: tse.Response = tagscript_engine.process(content, seed_variables)
    kwargs: Dict[str, Union[str, discord.Embed]] = {}
    if output.body:
        kwargs["content"] = output.body[:2000]
    if embed := output.actions.get("embed"):
        kwargs["embed"] = embed
    return kwargs


class TagError(Exception):
    """Base exception class."""


@final
class TagCharacterLimitReached(TagError):
    """
    Raised when the Tagscript character limit is reached.
    """

    def __init__(self, limit: int, length: int):
        super().__init__(
            f"TagScript cannot be longer than {humanize_number(limit)} (**{humanize_number(length)}**)."
        )
