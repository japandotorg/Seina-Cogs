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
from ...types import TypeDecorator

ischema: Any

class CoerceUnicode(TypeDecorator):
    impl: Any
    cache_ok: bool
    def process_bind_param(self, value, dialect): ...
    def bind_expression(self, bindvalue): ...

class _cast_on_2005(expression.ColumnElement[Any]):
    bindvalue: Any
    def __init__(self, bindvalue) -> None: ...

schemata: Any
tables: Any
columns: Any
mssql_temp_table_columns: Any
constraints: Any
column_constraints: Any
key_constraints: Any
ref_constraints: Any
views: Any
computed_columns: Any
sequences: Any

class IdentitySqlVariant(TypeDecorator):
    impl: Any
    cache_ok: bool
    def column_expression(self, colexpr): ...

identity_columns: Any
