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

from ...types import Numeric
from .base import MSDialect, MSIdentifierPreparer

class _MSNumeric_pymssql(Numeric):
    def result_processor(self, dialect, type_): ...

class MSIdentifierPreparer_pymssql(MSIdentifierPreparer):
    def __init__(self, dialect) -> None: ...

class MSDialect_pymssql(MSDialect):
    supports_statement_cache: bool
    supports_native_decimal: bool
    driver: str
    preparer: Any
    colspecs: Any
    @classmethod
    def dbapi(cls): ...
    def create_connect_args(self, url): ...
    def is_disconnect(self, e, connection, cursor): ...
    def set_isolation_level(self, connection, level) -> None: ...

dialect = MSDialect_pymssql
