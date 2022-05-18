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

from typing import Any as _Any

import sqlalchemy.types as sqltypes

from ...sql import expression

def Any(other, arrexpr, operator=...): ...
def All(other, arrexpr, operator=...): ...

class array(expression.ClauseList, expression.ColumnElement[_Any]):
    __visit_name__: str
    stringify_dialect: str
    inherit_cache: bool
    type: _Any
    def __init__(self, clauses, **kw) -> None: ...
    def self_group(self, against: _Any | None = ...): ...

CONTAINS: _Any
CONTAINED_BY: _Any
OVERLAP: _Any

class ARRAY(sqltypes.ARRAY):
    class Comparator(sqltypes.ARRAY.Comparator[_Any]):
        def contains(self, other, **kwargs): ...
        def contained_by(self, other): ...
        def overlap(self, other): ...
    comparator_factory: _Any
    item_type: _Any
    as_tuple: _Any
    dimensions: _Any
    zero_indexes: _Any
    def __init__(
        self,
        item_type,
        as_tuple: bool = ...,
        dimensions: _Any | None = ...,
        zero_indexes: bool = ...,
    ) -> None: ...
    @property
    def hashable(self): ...
    @property
    def python_type(self): ...
    def compare_values(self, x, y): ...
    def bind_expression(self, bindvalue): ...
    def bind_processor(self, dialect): ...
    def result_processor(self, dialect, coltype): ...
