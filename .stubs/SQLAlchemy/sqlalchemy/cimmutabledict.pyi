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

from _typeshed import SupportsKeysAndGetItem
from collections.abc import Iterable
from typing import Generic, TypeVar, overload
from typing_extensions import final

_KT = TypeVar("_KT")
_KT2 = TypeVar("_KT2")
_VT = TypeVar("_VT")
_VT2 = TypeVar("_VT2")

@final
class immutabledict(dict[_KT, _VT], Generic[_KT, _VT]):
    @overload
    def union(self, __dict: dict[_KT2, _VT2]) -> immutabledict[_KT | _KT2, _VT | _VT2]: ...
    @overload
    def union(self, __dict: None = ..., **kw: SupportsKeysAndGetItem[_KT2, _VT2]) -> immutabledict[_KT | _KT2, _VT | _VT2]: ...
    def merge_with(
        self, *args: SupportsKeysAndGetItem[_KT | _KT2, _VT2] | Iterable[tuple[_KT2, _VT2]] | None
    ) -> immutabledict[_KT | _KT2, _VT | _VT2]: ...
