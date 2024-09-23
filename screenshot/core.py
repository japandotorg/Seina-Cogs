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
from typing import Final, List, Literal

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
from .common.utils import counter as counter_api, URLConverter

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

        self.__task: asyncio.Task[None] = asyncio.create_task(self.update_counter_api())

    async def cog_load(self) -> None:
        if self.manager.tor_location is None:
            await self.manager.download_and_extract_tor()
        await self.manager.execute_tor_binary()
        if self.manager.firefox_location is None:
            await self.manager.download_and_extract_firefox()
        if self.manager.driver_location is None:
            await self.manager.download_and_extract_driver()
        self.manager.set_driver_downloaded()
        self.bg_task.start()

    async def cog_unload(self) -> None:
        self.filter.close()
        self.__task.cancel()
        self.bg_task.cancel()
        await self.session.close()
        if self.manager._tor_process is not discord.utils.MISSING:
            self.manager._tor_process.terminate()
            self.manager._tor_process.kill()
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

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.has_permissions(attach_files=True, embed_links=True)
    @commands.bot_has_permissions(attach_files=True, embed_links=True)
    async def screenshot(
        self, ctx: commands.Context, url: URLConverter, mode: Literal["normal", "full"] = "normal"
    ):
        """
        Take screenshot of a web page.

        **Arguments**:
        - ``<url>`` - a well formatted url.
        - ``<mode>`` - weather to take a full screen window screenshot or a full web page screenshot. (defaults to "normal")

        **Examples**:
        - ``[p]screenshot https://seina-cogs.readthedocs.io``
        - ``[p]screenshot https://seina-cogs.readthedocs.io full``
        """
        if not self.filter.is_valid_url(url):
            await ctx.send(
                "That is not a valid url.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            raise commands.CheckFailure()
        async with ctx.typing():
            try:
                image: bytes = await self.driver.get_screenshot_bytes_from_url(url=url, mode=mode)
            except NoSuchDriverException:
                await self.bot.send_to_owners(
                    "Something went wrong with the screenshot cog, a cog reload should fix it."
                )
                await ctx.send(
                    "Something went wrong with the screenshot cog, {}".format(
                        "a cog reload should fix it."
                    )
                    if await self.bot.is_owner(ctx.author)
                    else "try again later."
                )
                raise commands.CheckFailure()
            except ProxyConnectFailedError as error:
                log.exception(
                    "Failed connecting to the proxy.",
                    exc_info=error,
                )
                await self.bot.send_to_owners(
                    "Something went wrong with the screenshot cog, check logs for more details."
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
                and await self.filter.read(image=image, model="small")
            ):
                await ctx.send(
                    "This image contains nsfw content, and cannot be sent on this channel.",
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
                raise commands.CheckFailure()
        file: discord.File = discord.File(io.BytesIO(image), "screenshot.png")
        await ctx.send(file=file)
