"""
GNU General Public License Version 3.0

Copyright (c) 2018-2023 Sitryk
Copyright (c) 2023-present japandotorg
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
