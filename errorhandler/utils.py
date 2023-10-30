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

import ast
import re
from types import CodeType
from typing import Iterator, Literal, Pattern

from redbot.core.utils.chat_formatting import pagify

START_CODE_BLOCK_RE: Pattern[str] = re.compile(r"^((```[\w.+\-]+\n+(?!```))|(```\n*))")


def async_compile(source: str, filename: str, mode: Literal["eval", "exec"]) -> CodeType:
    return compile(
        source, filename, mode, flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT, optimize=0, dont_inherit=True
    )


def get_pages(message: str) -> Iterator[str]:
    return pagify(message, delims=["\n", " "], priority=True, shorten_by=10)


def get_syntax_error(e: SyntaxError):
    if e.text is None:
        return get_pages("{0.__class__.__name__}: {0}".format(e))
    return get_pages("{0.text}\n{1:>{0.offset}}\n{2}: {0}".format(e, "^", type(e).__name__))


def cleanup_code(content: str) -> str:
    if content.startswith("```") and content.endswith("```"):
        return START_CODE_BLOCK_RE.sub("", content)[:-3].rstrip("\n")
    return content.strip("` \n")
