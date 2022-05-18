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

from ...sql import expression
from ...sql.schema import ColumnCollectionConstraint

class aggregate_order_by(expression.ColumnElement[Any]):
    __visit_name__: str
    stringify_dialect: str
    inherit_cache: bool
    target: Any
    type: Any
    order_by: Any
    def __init__(self, target, *order_by) -> None: ...
    def self_group(self, against: Any | None = ...): ...
    def get_children(self, **kwargs): ...

class ExcludeConstraint(ColumnCollectionConstraint):
    __visit_name__: str
    where: Any
    inherit_cache: bool
    create_drop_stringify_dialect: str
    operators: Any
    using: Any
    ops: Any
    def __init__(self, *elements, **kw) -> None: ...

def array_agg(*arg, **kw): ...
