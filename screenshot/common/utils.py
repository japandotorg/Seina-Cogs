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

# isort: off
import shlex
import hashlib
import logging
import argparse
import functools
import contextlib
from typing import TYPE_CHECKING, Callable, Dict, Literal, NoReturn, Optional, Tuple, Union, cast

import discord
from redbot.core.bot import Red
from redbot.core import commands

if TYPE_CHECKING:
    from ..core import Screenshot

try:
    import regex as re
except ModuleNotFoundError:
    import re as re
# isort: on


log: logging.Logger = logging.getLogger("red.seina.screenshot.core")


def counter(func: Callable[["Screenshot"], str]) -> Callable[["Screenshot"], str]:
    @functools.wraps(func)
    def wrapper(self: "Screenshot") -> str:
        string: str = func(self)
        return hashlib.sha1(string.encode("utf-8")).hexdigest()

    return wrapper


def normal_or_full(value: str) -> Literal["normal", "full"]:
    if value.lower() in ["normal", "n"]:
        return "normal"
    elif value.lower() in ["full", "f"]:
        return "full"
    raise commands.BadArgument("{} is not a recognised size.".format(value))


def light_or_dark(value: str) -> Literal["light", "dark"]:
    if value.lower() in ["light", "l"]:
        return "light"
    elif value.lower() in ["dark", "d"]:
        return "dark"
    raise commands.BadArgument("{} is not a valid mode.".format(value))


class NoExitParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise commands.BadArgument(message)


class Flags(commands.Converter[Tuple[bool, str]]):
    async def convert(self, _: commands.Context, argument: str) -> Tuple[bool, str]:
        argument: str = argument.replace("—", "--")
        parser: NoExitParser = NoExitParser(
            description="Screenshot argument parser.", add_help=False
        )
        parser.add_argument(
            "--full", nargs="?", dest="full", const="full", default="normal", type=normal_or_full
        )
        parser.add_argument("--mode", nargs="?", dest="mode", default="light", type=light_or_dark)
        try:
            vals: Dict[str, Union[bool, str]] = vars(parser.parse_args(shlex.split(argument)))
        except Exception as error:
            raise commands.BadArgument(str(error))
        return cast(bool, vals["full"]), cast(str, vals["mode"])


class URLConverter(commands.Converter[str]):
    async def convert(self, ctx: commands.Context, argument: str) -> str:
        if not re.match(r"https?://", argument):
            argument: str = "https://{}".format(argument)
        if not cast("Screenshot", ctx.cog).filter.is_valid_url(argument):
            await ctx.send(
                "That is not a valid url.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            raise commands.CheckFailure()
        return argument


class DeleteButton(discord.ui.Button["ScreenshotView"]):
    def __init__(self, *, emoji: str = "✖️", style=discord.ButtonStyle.red) -> None:
        super().__init__(emoji=emoji, style=style)

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        await interaction.response.defer()
        if isinstance((message := interaction.message), discord.Message):
            with contextlib.suppress(discord.HTTPException):
                await message.delete()


class SendToDMButton(discord.ui.Button["ScreenshotView"]):
    def __init__(
        self, file: discord.File, *, label: str = "Send To DMs", style=discord.ButtonStyle.green
    ) -> None:
        super().__init__(label=label, style=style)
        self.file: discord.File = file

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        await interaction.response.defer()
        try:
            await interaction.user.send(file=self.file)
        except discord.HTTPException:
            await interaction.followup.send("Failed to send you a dm.", ephemeral=True)


class ScreenshotView(discord.ui.View):
    def __init__(
        self, ctx: commands.Context, *, file: Optional[discord.File] = None, timeout: float = 120.0
    ) -> None:
        super().__init__(timeout=timeout)
        self.ctx: commands.Context = ctx

        self._message: discord.Message = discord.utils.MISSING

        if file:
            self.add_item(SendToDMButton(file))
        self.add_item(DeleteButton())

    async def on_timeout(self) -> None:
        for child in self.children:
            child: discord.ui.Item["ScreenshotView"]
            if hasattr(child, "disabled"):
                child.disabled = True  # type: ignore
        if self._message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        if (
            self.ctx.author.id == interaction.user.id
            or (
                isinstance(interaction.user, discord.Member)
                and interaction.user.guild_permissions.administrator
            )
            or await cast(Red, self.ctx.bot).is_owner(interaction.user)
        ):
            return True
        await interaction.response.send_message(
            content="You're not the author of this message.", ephemeral=True
        )
        return True
