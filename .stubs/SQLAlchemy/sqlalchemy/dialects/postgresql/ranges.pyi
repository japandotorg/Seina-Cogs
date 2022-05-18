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

import sqlalchemy.types as sqltypes

class RangeOperators:
    class comparator_factory(sqltypes.Concatenable.Comparator[Any]):
        def __ne__(self, other): ...
        def contains(self, other, **kw): ...
        def contained_by(self, other): ...
        def overlaps(self, other): ...
        def strictly_left_of(self, other): ...
        __lshift__: Any
        def strictly_right_of(self, other): ...
        __rshift__: Any
        def not_extend_right_of(self, other): ...
        def not_extend_left_of(self, other): ...
        def adjacent_to(self, other): ...
        def __add__(self, other): ...

class INT4RANGE(RangeOperators, sqltypes.TypeEngine):
    __visit_name__: str

class INT8RANGE(RangeOperators, sqltypes.TypeEngine):
    __visit_name__: str

class NUMRANGE(RangeOperators, sqltypes.TypeEngine):
    __visit_name__: str

class DATERANGE(RangeOperators, sqltypes.TypeEngine):
    __visit_name__: str

class TSRANGE(RangeOperators, sqltypes.TypeEngine):
    __visit_name__: str

class TSTZRANGE(RangeOperators, sqltypes.TypeEngine):
    __visit_name__: str
