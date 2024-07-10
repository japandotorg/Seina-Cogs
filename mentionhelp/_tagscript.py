from typing import Dict, Final, List, Union, final

import TagScriptEngine as tse

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_number


message: Final[
    str
] = """
{embed()}
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
