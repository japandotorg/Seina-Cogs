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
import io
import aiohttp
import logging
import contextlib
import asyncio.sslproto
from typing import Any, Final, List, Literal

import discord
from discord.ext import tasks
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import humanize_list

from selenium.common.exceptions import NoSuchDriverException

from .common.filter import Filter
from .common import FirefoxManager
from .common.downloader import DriverManager
from .common.exceptions import ProxyConnectFailedError
from .common.utils import counter as counter_api, URLConverter, ScreenshotView, Flags

# isort: on


log: logging.Logger = logging.getLogger("red.seina.screenshot.core")


class Screenshot(commands.Cog):
    """
    Take screenshot of web pages using the bot.
    """

    setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)

    __version__: Final[str] = "0.1.1"
    __author__: Final[List[str]] = ["inthedark.org"]

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=69_420_666, force_registration=True)
        self.config.register_global(**{"updated": False, "nsfw": "normal"})

        self.session: aiohttp.ClientSession = aiohttp.ClientSession(trust_env=True)
        self.manager: DriverManager = DriverManager(session=self.session)
        self.driver: FirefoxManager = FirefoxManager(self)
        self.filter: Filter = Filter(self)

        self.tasks: List[asyncio.Task[Any]] = []

    async def cog_load(self) -> None:
        self.tasks.append(asyncio.create_task(self.update_counter_api()))
        self.tasks.append(asyncio.create_task(self.manager.initialize()))
        self.bg_task.start()

    async def cog_unload(self) -> None:
        for task in self.tasks:
            if isinstance(task, asyncio.Task):
                task.cancel()
        self.bg_task.cancel()
        await self.session.close()
        if self.manager._tor_process is not discord.utils.MISSING:
            await self.manager.close()
        with contextlib.suppress(BaseException):
            self.driver.clear_all_drivers()

    @counter_api
    def counter(self) -> str:
        return self.__class__.__name__.lower()

    async def update_counter_api(self) -> None:
        await self.bot.wait_until_red_ready()
        if not await self.config.updated():
            await self.session.get(
                "https://api.counterapi.dev/v1/japandotorg/{}/up".format(self.counter())
            )
            await self.config.updated.set(True)

    @tasks.loop(minutes=5.0, reconnect=True, name="red:seina:screenshot")
    async def bg_task(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.driver.remove_drivers_if_time_has_passed(minutes=10.0)

    @bg_task.before_loop
    async def bg_task_before_loop(self) -> None:
        await self.manager.wait_until_driver_downloaded()

    @commands.is_owner()
    @commands.group(name="screenshotset", aliases=["screenset"])
    async def screenshot_set(self, _: commands.Context):
        """Configuration commands for screenshot."""

    @screenshot_set.command(name="model")  # type: ignore
    async def screenshot_set_model(
        self, ctx: commands.Context, model: Literal["small", "normal", "large"]
    ):
        """
        Change the AI model responsible for the nsfw detection.

        Defaults to ``normal``.

        - ``small``: faster but less accurate.
        - ``normal``: faster but more accurate than ``small``.
        - ``large``: slower but the most accurate one.
        """
        await self.config.nsfw.set(model.lower())
        await ctx.tick()

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_permissions(attach_files=True, embed_links=True)
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    async def screenshot(self, ctx: commands.Context, url: URLConverter, *, flags: str = ""):
        """
        Take screenshot of a web page.

        **Arguments**:
        - ``<url>  ``: a well formatted url.
        - ``<flags>``:
          - ``--full`` for a full screenshot of the page.
          - ``--mode <mode>`` either ``light`` or ``dark``.

        **Examples**:
        - ``[p]screenshot https://seina-cogs.readthedocs.io``
        - ``[p]screenshot https://seina-cogs.readthedocs.io --full``
        - ``[p]screenshot https://seina-cogs.readthedocs.io --mode dark``
        - ``[p]screenshot https://seina-cogs.readthedocs.io --full --mode dark``
        """
        async with ctx.typing():
            size, mode = await Flags().convert(ctx, flags)
            try:
                image: bytes = await self.driver.get_screenshot_bytes_from_url(
                    url=url, size=size, mode=mode
                )
            except NoSuchDriverException:
                if await self.bot.is_owner(ctx.author):
                    await ctx.send(
                        "Something went wrong with the screenshot cog, a cog reload should fix it.",
                        reference=ctx.message.to_reference(fail_if_not_exists=False),
                        allowed_mentions=discord.AllowedMentions(replied_user=False),
                    )
                else:
                    await self.bot.send_to_owners(
                        "Something went wrong with the screenshot cog, a cog reload should fix it."
                    )
                    await ctx.send(
                        "Something went wrong with the screenshot cog, try again later.",
                        reference=ctx.message.to_reference(fail_if_not_exists=False),
                        allowed_mentions=discord.AllowedMentions(replied_user=False),
                    )
                raise commands.CheckFailure()
            except ProxyConnectFailedError:
                await self.manager.close()
                await self.manager.execute_tor_binary()
                await ctx.send(
                    "Something went wrong, try again later.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                raise commands.CheckFailure()
            except asyncio.TimeoutError:
                await ctx.send(
                    "Timed out waiting for the website to load.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                raise commands.CheckFailure()
            except commands.UserFeedbackCheckFailure as error:
                if message := error.message:
                    await ctx.send(
                        message,
                        reference=ctx.message.to_reference(fail_if_not_exists=False),
                        allowed_mentions=discord.AllowedMentions(replied_user=False),
                    )
                raise commands.CheckFailure()
            self.filter.maybe_setup_models()
            if (
                isinstance(
                    ctx.channel,
                    (
                        discord.TextChannel,
                        discord.VoiceChannel,
                        discord.StageChannel,
                        discord.Thread,
                    ),
                )
                and not ctx.channel.is_nsfw()
                and await self.filter.read(image=image)
            ):
                file: discord.File = discord.File(
                    io.BytesIO(image), "screenshot.png", spoiler=True
                )
                view: ScreenshotView = ScreenshotView(ctx, file=file)
                view._message = await ctx.send(
                    "This image contains nsfw content, and cannot be sent on this channel.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                    view=view,
                )
                raise commands.CheckFailure()
        view: ScreenshotView = ScreenshotView(ctx)
        file: discord.File = discord.File(io.BytesIO(image), "screenshot.png")
        view._message = await ctx.send(file=file, view=view)
