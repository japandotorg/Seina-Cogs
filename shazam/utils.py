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

import functools
from urllib import parse
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Optional,
    ParamSpec,
    TypeVar,
    cast,
)

from redbot.core import commands

from .types import Genre


T = TypeVar("T")
P = ParamSpec("P")


def is_valid_url(url: str) -> bool:
    try:
        par: parse.ParseResult = parse.urlparse(url)
    except ValueError:
        return False
    return all([par.scheme, par.netloc])


def with_context_typing() -> Callable[
    [Callable[P, Awaitable[T]]], Callable[P, Coroutine[Any, Any, T]]
]:
    def decorator(
        func: Callable[P, Awaitable[T]],
    ) -> Callable[P, Coroutine[Any, Any, T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            ctx: commands.Context = cast(commands.Context, args[1])
            async with ctx.typing():
                return await func(*args, **kwargs)

        return wrapper

    return decorator


class TopFlags(commands.FlagConverter, prefix="", delimiter=":"):
    genre: Optional[Genre] = commands.flag(
        name="genre", aliases=["g"], description="Search genre specific top tracks."
    )
    country: Optional[str] = commands.flag(
        name="country",
        aliases=["cy", "cr", "co"],
        description="Search country specific top tracks.",
    )
    city: Optional[str] = commands.flag(
        name="city",
        aliases=["ct", "ci"],
        description="Search city specific top tracks.",
    )
    limit: commands.Range[int, 1, 100] = commands.flag(
        name="limit",
        aliases=["l"],
        default=10,
        description="Limit how many tracks should the command return.",
    )
