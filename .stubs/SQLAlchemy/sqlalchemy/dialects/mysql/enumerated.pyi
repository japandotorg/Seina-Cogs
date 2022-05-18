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

from ...sql import sqltypes
from .types import _StringType

class ENUM(sqltypes.NativeForEmulated, sqltypes.Enum, _StringType):  # type: ignore  # incompatible with base class
    __visit_name__: str
    native_enum: bool
    def __init__(self, *enums, **kw) -> None: ...
    @classmethod
    def adapt_emulated_to_native(cls, impl, **kw): ...

class SET(_StringType):
    __visit_name__: str
    retrieve_as_bitwise: Any
    values: Any
    def __init__(self, *values, **kw) -> None: ...
    def column_expression(self, colexpr): ...
    def result_processor(self, dialect, coltype): ...
    def bind_processor(self, dialect): ...
    def adapt(self, impltype, **kw): ...
