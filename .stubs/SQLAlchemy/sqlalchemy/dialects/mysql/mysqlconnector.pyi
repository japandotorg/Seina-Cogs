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
from .base import BIT, MySQLCompiler, MySQLDialect, MySQLIdentifierPreparer

class MySQLCompiler_mysqlconnector(MySQLCompiler):
    def visit_mod_binary(self, binary, operator, **kw): ...
    def post_process_text(self, text): ...
    def escape_literal_column(self, text): ...

class MySQLIdentifierPreparer_mysqlconnector(MySQLIdentifierPreparer): ...

class _myconnpyBIT(BIT):
    def result_processor(self, dialect, coltype) -> None: ...

class MySQLDialect_mysqlconnector(MySQLDialect):
    driver: str
    supports_statement_cache: bool
    supports_unicode_binds: bool
    supports_sane_rowcount: bool
    supports_sane_multi_rowcount: bool
    supports_native_decimal: bool
    default_paramstyle: str
    statement_compiler: Any
    preparer: Any
    colspecs: Any
    def __init__(self, *arg, **kw) -> None: ...
    @property
    def description_encoding(self): ...
    @memoized_property
    def supports_unicode_statements(self): ...
    @classmethod
    def dbapi(cls): ...
    def do_ping(self, dbapi_connection): ...
    def create_connect_args(self, url): ...
    def is_disconnect(self, e, connection, cursor): ...

dialect = MySQLDialect_mysqlconnector
