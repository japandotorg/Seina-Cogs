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

from importlib import reload
from typing import Any, Dict, Final, List, Tuple, final

import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.errors import CogLoadError
from redbot.core.utils.chat_formatting import humanize_number

__all__: Tuple[str, ...] = (
    "custom_message",
    "TAGSCRIPT_LIMIT",
    "blocks",
    "tagscript_engine",
    "_process_tagscript",
    "validate_tagscriptengine",
    "TagError",
    "TagCharacterLimitReached",
    "TagscriptConverter",
)


custom_message: Final[
    str
] = """
{embed(description):
{author(mention)} is currently AFK ({time}) 
**Message:** 
{reason}
}
{embed(color):{color}}
{embed(thumbnail):{author(avatar)}}
"""

TAGSCRIPT_LIMIT: Final[int] = 10_000

PIP: Final[str] = "pip3"

blocks: List[tse.Block] = [
    tse.LooseVariableGetterBlock(),
    tse.AssignmentBlock(),
    tse.EmbedBlock(),
    tse.IfBlock(),
]

tagscript_engine: tse.Interpreter = tse.Interpreter(blocks)


def _process_tagscript(
    content: str, seed_variables: Dict[str, tse.Adapter] = {}
) -> Dict[str, Any]:
    output: tse.Response = tagscript_engine.process(content, seed_variables)
    kwargs: Dict[str, Any] = {}
    if output.body:
        kwargs["content"] = discord.utils.escape_mentions(output.body[:2000])
    if embed := output.actions.get("embed"):
        kwargs["embed"] = embed

    return kwargs


async def validate_tagscriptengine(bot: Red, tse_version: str, *, reloaded: bool = False) -> None:
    try:
        import TagScriptEngine as tse
    except ImportError as exc:
        raise CogLoadError(
            "The AFK cog failed to install TagScriptEngine. Reinstall the cog and restart your "
            "bot. If it continues to fail to load, contact the cog author."
        ) from exc

    commands = [
        f"`{PIP} uninstall -y TagScript`",
        f"`{PIP} uninstall -y TagScriptEngine`",
        f"`{PIP} uninstall -y AdvancedTagScriptEngine`",
        f"`{PIP} install AdvancedTagScript=={tse_version}`",
    ]
    commands = "\n".join(commands)

    message = (
        "The AFK cog attempted to install TagScriptEngine, but the version installed "
        "is outdated. Shut down your bot, then in shell in your venv, run the following "
        f"commands:\n{commands}\nAfter running these commands, restart your bot and reload "
        "Tags. If it continues to fail to load, contact the cog author."
    )

    if not hasattr(tse, "VersionInfo"):
        if not reloaded:
            reload(tse)
            await validate_tagscriptengine(bot, tse_version, reloaded=True)
            return

        await bot.send_to_owners(message)
        raise CogLoadError(message)

    if tse.version_info < tse.VersionInfo.from_str(tse_version):
        await bot.send_to_owners(message)
        raise CogLoadError(message)


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
class TagscriptConverter(commands.Converter[str]):
    async def convert(self, ctx: commands.Context, argument: str) -> str:
        try:
            await ctx.cog.validate_tagscript(argument)  # type: ignore
        except TagError as e:
            raise commands.BadArgument(str(e))
        return argument
