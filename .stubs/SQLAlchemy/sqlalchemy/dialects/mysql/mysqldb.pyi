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

from ...util import memoized_property
from .base import MySQLCompiler, MySQLDialect, MySQLExecutionContext

class MySQLExecutionContext_mysqldb(MySQLExecutionContext):
    @property
    def rowcount(self): ...

class MySQLCompiler_mysqldb(MySQLCompiler): ...

class MySQLDialect_mysqldb(MySQLDialect):
    driver: str
    supports_statement_cache: bool
    supports_unicode_statements: bool
    supports_sane_rowcount: bool
    supports_sane_multi_rowcount: bool
    supports_native_decimal: bool
    default_paramstyle: str
    statement_compiler: Any
    preparer: Any
    def __init__(self, **kwargs) -> None: ...
    @memoized_property
    def supports_server_side_cursors(self): ...
    @classmethod
    def dbapi(cls): ...
    def on_connect(self): ...
    def do_ping(self, dbapi_connection): ...
    def do_executemany(self, cursor, statement, parameters, context: Any | None = ...) -> None: ...
    def create_connect_args(self, url, _translate_args: Any | None = ...): ...

dialect = MySQLDialect_mysqldb
