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
import logging
import asyncio
import contextlib
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, AsyncGenerator, Dict, Literal, TypeVar

from redbot.core import commands

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import TimeoutException, WebDriverException, ScreenshotException

from .firefox import Firefox
from .exceptions import ProxyConnectFailedError

if TYPE_CHECKING:
    from ..core import Screenshot

try:
    import regex as re
except (ImportError, ModuleNotFoundError):
    import re as re
# isort: on


T = TypeVar("T")


log: logging.Logger = logging.getLogger("red.seina.screenshot.core")


class FirefoxManager:
    def __init__(self, cog: "Screenshot") -> None:
        self.cog: "Screenshot" = cog
        self.drivers: Dict[datetime, Firefox] = {}
        self.lock: asyncio.Lock = asyncio.Lock()

    def get_service(self) -> Service:
        return Service(
            executable_path=str(self.cog.manager.driver_location),
            service_args=["--log", "debug"],
            log_output=str(self.cog.manager.logs_directory / "gecko.log"),
        )

    def get_options(self) -> Options:
        cog: "Screenshot" = self.cog
        options: Options = Options()
        options.add_argument("--headless")
        options.page_load_strategy = "normal"
        options.binary_location = str(cog.manager.firefox_location)
        options.proxy = Proxy(
            {
                "proxyType": ProxyType.MANUAL,
                "socksProxy": "127.0.0.1:21666",
                "socksVersion": 5,
            }
        )
        options.profile = FirefoxProfile()
        options.profile.set_preference("browser.cache.disk.enable", False)
        options.profile.set_preference("browser.cache.memory.enable", False)
        options.profile.set_preference("browser.cache.offline.enable", False)
        options.profile.set_preference("network.http.use-cache", False)
        return options

    def clear_all_drivers(self) -> None:
        for date, driver in self.drivers.items():
            if isinstance(driver, Firefox):
                with contextlib.suppress(BaseException):
                    driver.delete_all_cookies()
                    driver.quit()
                with contextlib.suppress(KeyError):
                    del self.drivers[date]

    def remove_drivers_if_time_has_passed(self, minutes: float = 10.0) -> None:
        def has_time_passed(started: datetime, minutes: float) -> bool:
            now: datetime = datetime.now(timezone.utc)
            return now - started > timedelta(minutes=minutes) or now.minute != started.minute

        for date, driver in self.drivers.items():
            if has_time_passed(date, minutes):
                if isinstance(driver, Firefox):
                    with contextlib.suppress(BaseException):
                        driver.delete_all_cookies()
                        driver.quit()
                with contextlib.suppress(KeyError):
                    del self.drivers[date]

    def take_screenshot_with_url(
        self, driver: Firefox, *, url: str, mode: Literal["normal", "full"], wait: int = 10
    ) -> bytes:
        try:
            driver.get(url)
        except TimeoutException:
            raise commands.UserFeedbackCheckFailure("Timed out opening the website.")
        except WebDriverException as error:
            if re.search(pattern="about:neterror", string=str(error.msg), flags=re.IGNORECASE):
                log.exception("Something went wrong connecting to the internet.", exc_info=error)
                raise ProxyConnectFailedError()
            raise commands.UserFeedbackCheckFailure(
                "Could not get a screenshot of that website, try again later."
            )
        except Exception:
            raise commands.UserFeedbackCheckFailure(
                "Could not get a screenshot of that website, try again later."
            )
        driver.implicitly_wait(wait)
        try:
            if mode.lower() == "normal":
                byte: bytes = driver.get_screenshot_as_png()
            elif mode.lower() == "full":
                byte: bytes = driver.get_full_page_screenshot_as_png()
            else:
                raise commands.UserFeedbackCheckFailure(
                    "Invalid mode provided '{}'.".format(mode.lower())
                )
        except TimeoutException:
            raise commands.UserFeedbackCheckFailure("Timed-out getting the screenshot.")
        except ScreenshotException:
            raise commands.UserFeedbackCheckFailure(
                "Failed to take a screenshot of the website, please try again later or check the url."
            )
        return byte

    @asynccontextmanager
    async def driver(self) -> AsyncGenerator[Firefox, None]:
        await self.cog.manager.wait_until_driver_downloaded()
        await self.lock.acquire()
        now: datetime = datetime.now(timezone.utc)
        try:
            driver: Firefox = await self.launcher()
            driver.set_page_load_timeout(time_to_wait=230.0)
            driver.fullscreen_window()
            try:
                yield driver
                self.drivers[now] = driver
            except BaseException as error:
                with contextlib.suppress(BaseException):
                    if isinstance(driver, Firefox):
                        driver.delete_all_cookies()
                        driver.quit()
                    del self.drivers[now]
                raise error
        finally:
            self.lock.release()

    async def launcher(self) -> Firefox:
        return await asyncio.to_thread(
            lambda: Firefox(service=self.get_service(), options=self.get_options())
        )

    async def get_screenshot_bytes_from_url(
        self, *, url: str, mode: Literal["normal", "full"], wait: int = 10
    ) -> bytes:
        async with self.driver() as driver:
            return await asyncio.to_thread(
                lambda: self.take_screenshot_with_url(
                    driver,
                    url=url,
                    mode=mode,
                    wait=wait,
                )
            )
