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

from ...sql.dml import Insert as StandardInsert
from ...sql.elements import ClauseElement
from ...util import memoized_property

class Insert(StandardInsert):
    stringify_dialect: str
    inherit_cache: bool
    @memoized_property
    def excluded(self): ...
    def on_conflict_do_update(
        self,
        constraint: Any | None = ...,
        index_elements: Any | None = ...,
        index_where: Any | None = ...,
        set_: Any | None = ...,
        where: Any | None = ...,
    ) -> None: ...
    def on_conflict_do_nothing(
        self,
        constraint: Any | None = ...,
        index_elements: Any | None = ...,
        index_where: Any | None = ...,
    ) -> None: ...

insert: Any

class OnConflictClause(ClauseElement):
    stringify_dialect: str
    constraint_target: Any
    inferred_target_elements: Any
    inferred_target_whereclause: Any
    def __init__(
        self,
        constraint: Any | None = ...,
        index_elements: Any | None = ...,
        index_where: Any | None = ...,
    ) -> None: ...

class OnConflictDoNothing(OnConflictClause):
    __visit_name__: str

class OnConflictDoUpdate(OnConflictClause):
    __visit_name__: str
    update_values_to_set: Any
    update_whereclause: Any
    def __init__(
        self,
        constraint: Any | None = ...,
        index_elements: Any | None = ...,
        index_where: Any | None = ...,
        set_: Any | None = ...,
        where: Any | None = ...,
    ) -> None: ...
