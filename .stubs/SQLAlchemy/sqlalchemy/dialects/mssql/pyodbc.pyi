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

from ...connectors.pyodbc import PyODBCConnector
from ...types import DateTime, Float, Numeric
from .base import BINARY, DATETIMEOFFSET, VARBINARY, MSDialect, MSExecutionContext

class _ms_numeric_pyodbc:
    def bind_processor(self, dialect): ...

class _MSNumeric_pyodbc(_ms_numeric_pyodbc, Numeric): ...
class _MSFloat_pyodbc(_ms_numeric_pyodbc, Float): ...

class _ms_binary_pyodbc:
    def bind_processor(self, dialect): ...

class _ODBCDateTimeBindProcessor:
    has_tz: bool
    def bind_processor(self, dialect): ...

class _ODBCDateTime(_ODBCDateTimeBindProcessor, DateTime): ...

class _ODBCDATETIMEOFFSET(_ODBCDateTimeBindProcessor, DATETIMEOFFSET):
    has_tz: bool

class _VARBINARY_pyodbc(_ms_binary_pyodbc, VARBINARY): ...
class _BINARY_pyodbc(_ms_binary_pyodbc, BINARY): ...

class MSExecutionContext_pyodbc(MSExecutionContext):
    def pre_exec(self) -> None: ...
    def post_exec(self) -> None: ...

class MSDialect_pyodbc(PyODBCConnector, MSDialect):
    supports_statement_cache: bool
    supports_sane_rowcount_returning: bool
    colspecs: Any
    description_encoding: Any
    use_scope_identity: Any
    fast_executemany: Any
    def __init__(
        self, description_encoding: Any | None = ..., fast_executemany: bool = ..., **params
    ) -> None: ...
    def on_connect(self): ...
    def do_executemany(self, cursor, statement, parameters, context: Any | None = ...) -> None: ...
    def is_disconnect(self, e, connection, cursor): ...

dialect = MSDialect_pyodbc
