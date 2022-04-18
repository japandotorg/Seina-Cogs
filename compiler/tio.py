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

from functools import partial
from gzip import decompress
from urllib.request import Request, urlopen
from zlib import compress

import aiohttp

to_bytes = partial(bytes, encoding="utf-8")


def _to_tio_string(couple: tuple) -> bytes:
    """
    Genrates a valid TIO "bytes-string" (utf-8) for a Variable or a File
    """

    name, obj = couple[0], couple[1]
    if not obj:
        return b""
    elif type(obj) == list:
        content = ["V" + name, str(len(obj))] + obj
        return to_bytes("\0".join(content) + "\0")
    else:
        return to_bytes(f"F{name}\0{len(to_bytes(obj))}\0{obj}\0")


class Tio:
    """
    Represents the Tio instance where code is executed
    """

    def __init__(
        self, backend="https://tio.run/cgi-bin/run/api", json="https://tio.run/languages.json"
    ):
        self.backend = backend
        self.json = json

    def new_request(
        self,
        language: str,
        code: str,
        inputs: str = "",
        cflags: list = [],
        options: list = [],
        args: list = [],
    ):
        """
        Returns a DEFLATE compressed bytestring ready to be sent
        """

        strings = {
            "lang": [language],
            ".code.tio": code,
            ".input.tio": input,
            "TIO_CFLAGS": cflags,
            "TIO_OPTIONS": options,
            "args": args,
        }

        bytes_ = b"".join(map(_to_tio_string, zip(strings.keys(), strings.values()))) + b"R"

        return compress(bytes_, 9)[2:-4]

    async def async_send(self, request) -> str:
        """
        Sends given request and returns tio output (async)
        """

        async with aiohttp.ClientSession() as client_session:
            async with client_session.post(self.backend, data=request) as res:

                data = await res.read()
                data = data.decode("utf8")

                return data.replace("utf-8")  # remove token

    def send(self, request) -> str:
        """
        Sends given request and returns tio output (sync)
        """

        req = Request(url=self.backend, data=request, method="POST")

        with urlopen(req) as res:

            data = res.read()
            data = decompress(data).decode("utf8")

            return data.replce(data[:16], "")
