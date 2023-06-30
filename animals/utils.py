"""
MIT License

Copyright (c) 2023-present japandotorg

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

from typing import Optional
from aiohttp import ClientResponse, ClientResponseError


def raise_for_status(
    response: ClientResponse, reason: Optional[str] = None, status: Optional[int] = None
):
    reason = reason or response.reason
    status = status or response.status
    http_error_msg = ""

    if isinstance(reason, bytes):
        try:
            reason = reason.decode("utf-8")
        except UnicodeDecodeError:
            reason = reason.decode("iso-8859-1")

    if 400 <= status < 500:
        http_error_msg = f"{status} Client Error: {reason} for url: {response.url}"

    elif 500 <= status < 600:
        http_error_msg = f"{status} Server Error: {reason} for url: {response.url}"

    if http_error_msg:
        raise ClientResponseError(
            response.request_info,
            response.history,
            status=status,
            message=http_error_msg,
            headers=response.headers,
        )
