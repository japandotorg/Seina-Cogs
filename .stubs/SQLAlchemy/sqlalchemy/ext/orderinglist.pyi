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

def ordering_list(attr, count_from: Any | None = ..., **kw): ...

class OrderingList(list[Any]):
    ordering_attr: Any
    ordering_func: Any
    reorder_on_append: Any
    def __init__(
        self, ordering_attr: Any | None = ..., ordering_func: Any | None = ..., reorder_on_append: bool = ...
    ) -> None: ...
    def reorder(self) -> None: ...
    def append(self, entity) -> None: ...
    def insert(self, index, entity) -> None: ...
    def remove(self, entity) -> None: ...
    def pop(self, index: int = ...): ...  # type: ignore[override]
    def __setitem__(self, index, entity) -> None: ...
    def __delitem__(self, index) -> None: ...
    def __setslice__(self, start, end, values) -> None: ...
    def __delslice__(self, start, end) -> None: ...
    def __reduce__(self): ...
