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

from typing import Any

class _EventKey:
    target: Any
    identifier: Any
    fn: Any
    fn_key: Any
    fn_wrap: Any
    dispatch_target: Any
    def __init__(
        self, target, identifier, fn, dispatch_target, _fn_wrap: Any | None = ...
    ) -> None: ...
    def with_wrapper(self, fn_wrap): ...
    def with_dispatch_target(self, dispatch_target): ...
    def listen(self, *args, **kw) -> None: ...
    def remove(self) -> None: ...
    def contains(self): ...
    def base_listen(
        self,
        propagate: bool = ...,
        insert: bool = ...,
        named: bool = ...,
        retval: Any | None = ...,
        asyncio: bool = ...,
    ) -> None: ...
    def append_to_list(self, owner, list_): ...
    def remove_from_list(self, owner, list_) -> None: ...
    def prepend_to_list(self, owner, list_): ...
