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

from datetime import timedelta
from typing import Dict, Final, Literal, Union

import yarl

SESSION_TIMEOUT: int = 15

URL_EXPIRE_AFTER: Dict[str, timedelta] = {"*.truthordarebot.xyz": timedelta(seconds=3)}

StrOrUrl = Union[str, yarl.URL]
BASE_URL: Final[StrOrUrl] = "https://api.truthordarebot.xyz/v1"

Endpoints = Literal["truth", "dare", "wyr", "nhie", "paranoia"]
Ratings = Literal["pg", "pg13", "r"]
Methods = Literal["GET", "HEAD"]
RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]
