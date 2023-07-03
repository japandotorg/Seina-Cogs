"""
MIT License

Copyright (c) 2022-present japandotorg

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

import logging
from io import BytesIO
from typing import Any, Dict, Final, List, Literal, Optional, Tuple, Union

import discord
from discord.ext import tasks
from redbot.core import Config, commands  # type: ignore
from redbot.core.bot import Red  # type: ignore

BaseCog: commands.Cog = getattr(commands, "Cog", object)

log: logging.Logger = logging.getLogger("red.seinacogs.rainbowrole")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

COLORS: List[Tuple[int, int, int]] = [
    (255, 62, 62),
    (255, 147, 62),
    (255, 215, 62),
    (133, 255, 62),
    (56, 255, 202),
    (56, 167, 255),
    (173, 56, 255),
    (243, 56, 255),
]


class RainbowRole(BaseCog):  # type: ignore
    """
    Create and manage a Rainbow Role in your server.
    """

    __version__: Final[str] = "0.1.1"
    __author__: Final[List[str]] = [("inthedark.org")]

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self, identifier=759180080328081450, force_registration=True
        )
        self.log: logging.LoggerAdapter[logging.Logger] = logging.LoggerAdapter(
            log, {"version": self.__version__}
        )

        default_guild: Dict[str, Any] = {
            "rainbow_role": None,
            "toggled": False,
        }

        self.config.register_guild(**default_guild)

        self.color: int = 0
        self.change_color.start()

    async def red_get_data_for_user(self, *, user_id: int) -> Dict[str, BytesIO]:
        """
        Nothing to get.
        """
        data: Any = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, BytesIO]:
        """
        Nothing to delete.
        """
        data: Any = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"Author: **{self.__author__}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @tasks.loop(seconds=90.0)
    async def change_color(self) -> None:
        """
        The task that is responsible for the color change every x seconds.
        """
        for guild in self.bot.guilds:
            toggle: bool = await self.config.guild(guild).toggle()
            if not toggle:
                return

            rainbow_role = await self.config.guild(guild).rainbow_role()
            if rainbow_role:
                try:
                    await rainbow_role.edit(
                        reason="Automatic rainbow role color change.",
                        color=discord.Colour.from_rgb(
                            COLORS[self.color][0],
                            COLORS[self.color][1],
                            COLORS[self.color][2],
                        ),
                    )
                except (discord.Forbidden, discord.HTTPException, Exception):
                    self.log.exception("Oops! Something went wrong.", exc_info=True)

        self.color: int = self.color + 1 if self.color + 1 <= 7 else 0

    @change_color.before_loop
    async def before_color_change(self) -> None:
        await self.bot.wait_until_red_ready()

    async def cog_load(self) -> None:
        pass

    async def cog_unload(self) -> None:
        self.bot.loop.create_task(self.change_color.stop())

    @commands.group(name="rainbowset", invoke_without_command=True)
    @commands.guildowner_or_permissions(administrator=True)
    async def _rainbow_set(self, ctx: commands.Context) -> None:
        """Group commands for the rainbow role settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help("set")

    @_rainbow_set.command()
    @commands.guildowner_or_permissions(administrator=True)
    async def toggle(self, ctx: commands.Context, true_or_false: Optional[bool] = None) -> None:
        """
        Toggle the rainbow role task.
        """
        if true_or_false is None:
            await ctx.send("The `true_or_false` option is a required argument.")

        await self.config.guild(ctx.guild).toggle(true_or_false)
        await ctx.tick()

    @_rainbow_set.command()
    @commands.guildowner_or_permissions(administrator=True)
    async def role(
        self,
        ctx: commands.Context,
        role: Optional[Union[discord.Role, int]] = None,
    ) -> None:
        """
        Set your rainbow role using this command.
        """
        role = ctx.guild.get_role(getattr(role, "id", role))
        await self.config.guild(ctx.guild).rainbow_role.set(role.id)  # type: ignore
        await ctx.tick()
        await ctx.send(f"Rainbow role set to `{role}`")
