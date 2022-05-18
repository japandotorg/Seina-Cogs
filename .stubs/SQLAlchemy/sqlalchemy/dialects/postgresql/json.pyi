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

class JSONPathType(sqltypes.JSON.JSONPathType):
    def bind_processor(self, dialect): ...
    def literal_processor(self, dialect): ...

class JSON(sqltypes.JSON):
    astext_type: Any
    def __init__(self, none_as_null: bool = ..., astext_type: Any | None = ...) -> None: ...

    class Comparator(sqltypes.JSON.Comparator):
        @property
        def astext(self): ...
    comparator_factory: Any

class JSONB(JSON):
    __visit_name__: str

    class Comparator(JSON.Comparator):
        def has_key(self, other): ...
        def has_all(self, other): ...
        def has_any(self, other): ...
        def contains(self, other, **kwargs): ...
        def contained_by(self, other): ...
    comparator_factory: Any
