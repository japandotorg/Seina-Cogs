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

import asyncio as asyncio
from collections.abc import Callable, Coroutine
from typing import Any

from .langhelpers import memoized_property

_greenlet = Any  # actually greenlet.greenlet

def is_exit_exception(e): ...

class _AsyncIoGreenlet(_greenlet):
    driver: Any
    gr_context: Any
    def __init__(self, fn, driver) -> None: ...

def await_only(awaitable: Coroutine[Any, Any, Any]) -> Any: ...
def await_fallback(awaitable: Coroutine[Any, Any, Any]) -> Any: ...
async def greenlet_spawn(fn: Callable[..., Any], *args, _require_await: bool = ..., **kwargs) -> Any: ...

class AsyncAdaptedLock:
    @memoized_property
    def mutex(self): ...
    def __enter__(self): ...
    def __exit__(self, *arg, **kw) -> None: ...

def get_event_loop(): ...
