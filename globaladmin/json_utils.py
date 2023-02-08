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

import json
import logging
import os
import time
from typing import Any, Dict, Union

import aiohttp
import backoff

log: logging.Logger = logging.getLogger("red.seina-cogs.globaladmin.json_utils")


def should_download(file_path: str, expiry_secs: int) -> bool:
    if not os.path.exists(file_path):
        log.debug(f"file does not exist, downloading {file_path}")
        return True

    ftime = os.path.getmtime(file_path)
    file_age = time.time() - ftime

    if file_age <= expiry_secs:
        return False
    log.debug(f"file {file_path} too old, download it")
    return True


def write_json_file(file_path: str, js_data: Any) -> None:
    with open(file_path, "w") as f:
        json.dump(js_data, f, indent=4)


def read_json_file(file_path: str) -> Any:
    with open(file_path) as f:
        return json.load(f)


def safe_read_json(file_path: str) -> Union[Any, Dict]:
    """
    This returns an empty dict rather than raising an error if the file contains invalid json
    """
    try:
        return read_json_file(file_path)
    except (json.JSONDecodeError, FileNotFoundError):
        log.error(f"failed to read {file_path} got exception", exc_info=True)
    return {}


def validate_json(fp: str) -> bool:
    try:
        json.load(open(fp))
        return True
    except json.JSONDecodeError:
        return False


@backoff.on_exception(backoff.expo, aiohttp.ClientError, max_time=60)
@backoff.on_exception(backoff.expo, aiohttp.ServerDisconnectedError, max_time=60)
async def async_cached_dadguide_request(file_path: str, file_url: str, expiry_secs: int) -> None:
    if should_download(file_path, expiry_secs):
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                assert resp.status == 200
                with open(file_path, "wb") as f:
                    f.write(await resp.read())


def write_plain_file(file_path: str, text_data: Union[str, bytes]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        if isinstance(text_data, str):
            f.write(text_data)
        elif isinstance(text_data, bytes):
            f.write(text_data.decode())


def read_plain_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


async def async_plain_request(file_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            return await resp.text()


async def async_cached_plain_request(file_path: str, file_url: str, expiry_secs: int) -> str:
    if should_download(file_path, expiry_secs):
        resp = await async_plain_request(file_url)
        write_plain_file(file_path, resp)
    return read_plain_file(file_path)
