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

from .base import BIT, MySQLDialect, MySQLExecutionContext

class _oursqlBIT(BIT):
    def result_processor(self, dialect, coltype) -> None: ...

class MySQLExecutionContext_oursql(MySQLExecutionContext):
    @property
    def plain_query(self): ...

class MySQLDialect_oursql(MySQLDialect):
    driver: str
    supports_statement_cache: bool
    supports_unicode_binds: bool
    supports_unicode_statements: bool
    supports_native_decimal: bool
    supports_sane_rowcount: bool
    supports_sane_multi_rowcount: bool
    colspecs: Any
    @classmethod
    def dbapi(cls): ...
    def do_execute(self, cursor, statement, parameters, context: Any | None = ...) -> None: ...
    def do_begin(self, connection) -> None: ...
    def do_begin_twophase(self, connection, xid) -> None: ...
    def do_prepare_twophase(self, connection, xid) -> None: ...
    def do_rollback_twophase(
        self, connection, xid, is_prepared: bool = ..., recover: bool = ...
    ) -> None: ...
    def do_commit_twophase(
        self, connection, xid, is_prepared: bool = ..., recover: bool = ...
    ) -> None: ...
    def has_table(self, connection, table_name, schema: Any | None = ...): ...  # type: ignore[override]
    def get_table_options(self, connection, table_name, schema: Any | None = ..., **kw): ...
    def get_columns(self, connection, table_name, schema: Any | None = ..., **kw): ...
    def get_view_names(self, connection, schema: Any | None = ..., **kw): ...
    def get_table_names(self, connection, schema: Any | None = ..., **kw): ...
    def get_schema_names(self, connection, **kw): ...
    def initialize(self, connection): ...
    def is_disconnect(self, e, connection, cursor): ...
    def create_connect_args(self, url): ...

dialect = MySQLDialect_oursql
