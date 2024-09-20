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

import functools
import hashlib
import logging
from typing import TYPE_CHECKING, Callable

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box, text_to_file

if TYPE_CHECKING:
    from ..core import Screenshot

try:
    import regex as re
except ModuleNotFoundError:
    import re as re


log: logging.Logger = logging.getLogger("red.seina.screenshot.core")


def counter(func: Callable[["Screenshot"], str]) -> Callable[["Screenshot"], str]:
    @functools.wraps(func)
    def wrapper(self: "Screenshot") -> str:
        string: str = func(self)
        return hashlib.sha1(string.encode("utf-8")).hexdigest()

    return wrapper


async def send_notification(cog: "Screenshot") -> None:
    await cog.bot.send_to_owners(
        content=(
            "**To unlock the full potential of this cog. (i.e., to conceal your IP address when taking screenshots)**\n\n"
            "You'll have to install and setup the [**tor protocol**](https://www.torproject.org/download/tor/) either by "
            "installing the browser or by using the tor expert bundle.\n\n{}\n"
            "If you already have a tor browser install and wish to use a separate instance of the tor protocol "
            "you can do so by leveraging the docker file given below.\n\n"
            "Finally to activate the tor protocol within the cog run the following commands if needed -\n"
            "- `[p]screenset tor <true_or_false>` to make the cog actually use the tor protocol.\n"
            "- `[p]screenset tor port <YOUR-PORT>` to change the default port to use the one configured by you.\n\n"
            "-# *You'll keep receiving this message everytime you load/reload the cog if you don't configure tor.*"
        ).format(
            (
                (
                    "It is recommended to use the command line arguments to install tor. "
                    "Follow this [**guide**](https://community.torproject.org/onion-services/setup/install/) to install "
                    "tor in your system. Make sure to run this command after installing the tor protocol -\n{}"
                ).format(box("sudo systemctl enable --now tor", lang="bash"))
                if cog.manager.get_os_name().startswith("linux")
                else (
                    "To install the tor protocol as a windows service, assuming it's installed in the `C:/Tor` folder.\n"
                    "Run this command to install tor as a service (depending on how you installed it) -\n{} or {}"
                ).format(
                    box("C:\\Tor\\tor.ext --service install", lang="bash"),
                    box(
                        "C:\\Tor\\Browser\\TorBrowser\\Tor\\tor.exe --service install",
                        lang="bash",
                    ),
                )
            ),
        ),
        file=text_to_file(
            (
                "FROM alpine:3.20\n"
                "RUN echo '@edge https://dl-cdn.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories\n"
                "RUN echo '@edge https://dl-cdn.alpinelinux.org/alpine/edge/testing'   >> /etc/apk/repositories\n"
                "RUN apk -U upgrade\n"
                "RUN apk -v add tor@edge obfs4proxy@edge curl\n"
                "RUN chmod 700 /var/lib/tor\n"
                "RUN rm -rf /var/cache/apk/*\n"
                "RUN tor --version\n"
                "RUN touch torrc\n"
                "RUN echo 'HardwareAccel 1' >> torrc\n"
                "RUN echo 'Log notice stdout' >> torrc\n"
                "RUN echo 'DNSPort 0.0.0.0:8853' >> torrc\n"
                "RUN echo 'SocksPort 0.0.0.0:<YOUR-PORT>' >> torrc\n"
                "RUN echo 'DataDirectory /var/lib/tor' >> torrc\n"
                "RUN mv -f torrc /etc/tor/\n"
                "HEALTHCHECK --timeout=10s --start-period=60s CMD curl --fail --socks5-hostname localhost:<YOUR-PORT> -I -L 'https://www.torproject.org' || exit 1\n"
                "USER tor\n"
                "EXPOSE 8853/udp <YOUR-PORT>/tcp\n"
                "CMD ['/usr/bin/tor', '-f', '/etc/tor/torrc']\n"
            ),
            filename="Dockerfile",
        ),
    )


class URLConverter(commands.Converter[str]):
    async def convert(self, ctx: commands.Context, argument: str) -> str:
        if not re.match(r"https?://", argument):
            return "https://{}".format(argument)
        return argument


class DeleteView(discord.ui.View):
    def __init__(self, *, timeout: float = 120.0) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message = discord.utils.MISSING
