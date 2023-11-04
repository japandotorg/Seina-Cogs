"""
GNU General Public License Version 3.0

Copyright (c) 2018-2023 Sitryk
Copyright (c) 2023-present japandotorg
"""


import logging
import textwrap
import traceback
from typing import Any, Dict, Final, List, Optional

import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils import chat_formatting as cf

from .abc import CompositeMetaClass
from .commands import CommandsMixin
from .utils import async_compile, get_syntax_error

log: logging.Logger = logging.getLogger("red.seina.errorhandler")

DEFAULT_REPLY: Final[
    str
] = "await ctx.send(f\"`Error in command '{ctx.command.qualified_name}'. Check your console or logs for details.`\")"


class ErrorHandler(
    commands.Cog,
    CommandsMixin,
    metaclass=CompositeMetaClass,
):
    """
    Adds ability to replace the output of the bots error handler when CommandInvokeError
    is raised, all other errors get handled by the old handler.
    """

    __author__: Final[List[str]] = ["inthedark.org", "sitryk"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        default_global: Dict[str, str] = {
            "message": DEFAULT_REPLY,
        }
        self.config.register_global(**default_global)

        self._old_handler: Any = self.bot.on_command_error
        self._eval_string: Optional[str] = None

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{cf.humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    def cog_unload(self) -> None:
        self.bot.on_command_error = self._old_handler

    async def on_command_error(
        self, ctx: commands.Context, error: Exception, unhandled_by_cog: bool = False
    ) -> None:
        if isinstance(error, commands.CommandInvokeError):
            command = ctx.command
            log.exception(
                f"Exception in command '{command.qualified_name}'", exc_info=error.original
            )
            exception_log = f"Exception in command '{command.qualified_name}'\n"
            exception_log += "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            ctx.bot._last_exception = exception_log  # type: ignore

            cog: "ErrorHandler" = ctx.bot.get_cog("ErrorHandler")  # type: ignore
            if cog._eval_string is None:
                cog._eval_string = await cog.config.message()

            environment: Dict[str, Any] = {
                "ctx": ctx,
                "error": error,
                "discord": discord,
                "cf": cf,
            }

            to_compile: str = "async def func():\n%s" % textwrap.indent(cog._eval_string, "  ")

            try:
                compiled = async_compile(to_compile, "<string>", "exec")
                exec(compiled, environment)
            except SyntaxError as e:
                await ctx.send(get_syntax_error(e))
                return

            func = environment["func"]
            await func()
            return
        await self._old_handler(ctx, error, unhandled_by_cog)
