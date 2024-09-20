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

import io
import os
import asyncio
import logging
import platform
import concurrent.futures
from typing import ClassVar, Dict, Final, Optional

import pathlib
import zipfile
import aiohttp
import tarfile
from mozdownload.factory import FactoryScraper

from redbot.core import data_manager

from .exceptions import DriverDownloadFailed


log: logging.Logger = logging.getLogger("red.seina.screenshot.downloader")


class DriverManager:
    SYSTEM: Final[Dict[str, str]] = {"linux": "linux", "windows": "win", "arm": "linux-aarch"}
    DOWNLOAD_URL: Final[str] = "https://github.com/mozilla/geckodriver/releases/download"
    LATEST_RELEASE_URL: Final[str] = (
        "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
    )
    RELEASE_TAG_URL: ClassVar[str] = (
        "https://api.github.com/repos/mozilla/geckodriver/releases/tags/{version}"
    )
    EXTRAS: Final[str] = (
        "/DesktopShortcut=false /StartMenuShortcut=false /PrivateBrowsingShortcut=false"
    )

    def __init__(self, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.__session: aiohttp.ClientSession = session or aiohttp.ClientSession()
        self.__event: asyncio.Event = asyncio.Event()

    @staticmethod
    def get_os_architecture() -> int:
        if platform.machine().endswith("64"):
            return 64
        else:
            return 32

    @property
    def data_directory(self) -> pathlib.Path:
        return data_manager.cog_data_path(raw_name="Screenshot")

    @property
    def location(self) -> Optional[pathlib.Path]:
        return (
            loc[0]
            if (
                loc := list(self.data_directory.glob("geckodriver-{}*".format(self.get_os())))
                or (loc := list(self.data_directory.glob("geckodrive-{}*".format(self.get_os()))))
            )
            else None
        )

    @property
    def firefox(self) -> Optional[pathlib.Path]:
        return loc[0] if (loc := list(self.data_directory.glob("firefox/firefox*"))) else None

    def get_os_name(self) -> str:
        if platform.machine().lower() == "aarch64":
            return self.SYSTEM["arm"]
        if platform.system().lower() == "linux":
            return self.SYSTEM["linux"]
        elif platform.system().lower() == "windows":
            return self.SYSTEM["windows"]
        else:
            raise RuntimeError()

    def get_os(self) -> str:
        return "{}{}".format(self.get_os_name(), self.get_os_architecture())

    def set_driver_downloaded(self) -> None:
        self.__event.set()

    async def wait_until_driver_downloaded(self) -> None:
        await self.__event.wait()

    async def get_latest_release_version(self) -> str:
        async with self.__session.get(url=self.LATEST_RELEASE_URL) as response:
            json: Dict[str, str] = await response.json()
        version: str = json.get("tag_name", "v0.35.0")
        return version

    async def get_driver_download_url(self) -> str:
        version: str = await self.get_latest_release_version()
        async with self.__session.get(self.RELEASE_TAG_URL.format(version=version)) as response:
            json = await response.json()
        assets = json["assets"]
        name: str = "{}-{}-{}.".format("geckodriver", version, self.get_os())
        output_dict = [asset for asset in assets if asset["name"].startswith(name)]
        url: str = output_dict[0]["browser_download_url"]
        log.debug("Downloading driver (%s) for [%s]" % (url, self.get_os()))
        return url

    async def download_and_extract_driver(self) -> None:
        url: str = await self.get_driver_download_url()
        async with self.__session.get(url=url, timeout=aiohttp.ClientTimeout(120)) as response:
            if response.status == 404:
                raise DriverDownloadFailed(
                    "Could not find a driver with url: '%s" % url, retry=False
                )
            elif 400 <= response.status < 600:
                raise DriverDownloadFailed(retry=True)
            response.raise_for_status()
            byte: bytes = await response.read()
        if url.endswith(".zip"):
            with zipfile.ZipFile(file=io.BytesIO(byte), mode="r") as zip:
                zip.extractall(path=self.data_directory)
        elif url.endswith(".tar.gz"):
            tar: tarfile.TarFile = tarfile.TarFile.open(fileobj=io.BytesIO(byte), mode="r:gz")
            tar.extractall(path=self.data_directory)
        else:
            raise DriverDownloadFailed("Failed to download the driver.")
        path: pathlib.Path = list(self.data_directory.glob("geckodriver*"))[0]
        idx: int = path.name.rfind(".")
        name: str = path.name[:idx] + "-{}".format(
            "linux-aarch64" if platform.machine() == "aarch64" else self.get_os()
        )
        os.rename(
            path,
            (
                self.data_directory / "{}.exe".format(name)
                if self.get_os().startswith(self.SYSTEM["windows"])
                else self.data_directory / name
            ),
        )
        log.info("Downloaded driver successfully with location: {}".format(self.location))

    async def download_firefox(self) -> str:
        log.info("Downloading firefox in {}".format(self.data_directory))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            scraper: FactoryScraper = FactoryScraper(
                scraper_type="release",
                version="130.0",
                platform="linux-arm64" if platform.machine() == "aarch64" else None,
                destination=str(self.data_directory),
            )
            res: str = await asyncio.get_running_loop().run_in_executor(
                executor=executor, func=scraper.download
            )
            if self.get_os() == self.SYSTEM["windows"]:
                process: asyncio.subprocess.Process = await asyncio.create_subprocess_shell(
                    "{} /InstallDirectoryPath={} {}".format(
                        res, str(self.data_directory / "firefox"), self.EXTRAS
                    ),
                    shell=True,
                )
                await process.wait()
            elif res.endswith("tar.bz2"):
                tar: tarfile.TarFile = tarfile.TarFile.open(name=res, mode="r:bz2")
                tar.extractall(path=self.data_directory)
            else:
                raise RuntimeError()
            os.remove(res)
        log.info("Successfully downloaded firefox.")
        return res
