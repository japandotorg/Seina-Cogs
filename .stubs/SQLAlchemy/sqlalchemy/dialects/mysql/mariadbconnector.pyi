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

from .base import MySQLCompiler, MySQLDialect, MySQLExecutionContext

mariadb_cpy_minimum_version: Any

class MySQLExecutionContext_mariadbconnector(MySQLExecutionContext):
    def create_server_side_cursor(self): ...
    def create_default_cursor(self): ...

class MySQLCompiler_mariadbconnector(MySQLCompiler): ...

class MySQLDialect_mariadbconnector(MySQLDialect):
    driver: str
    supports_statement_cache: bool
    supports_unicode_statements: bool
    encoding: str
    convert_unicode: bool
    supports_sane_rowcount: bool
    supports_sane_multi_rowcount: bool
    supports_native_decimal: bool
    default_paramstyle: str
    statement_compiler: Any
    supports_server_side_cursors: bool
    paramstyle: str
    def __init__(self, **kwargs) -> None: ...
    @classmethod
    def dbapi(cls): ...
    def is_disconnect(self, e, connection, cursor): ...
    def create_connect_args(self, url): ...
    def do_begin_twophase(self, connection, xid) -> None: ...
    def do_prepare_twophase(self, connection, xid) -> None: ...
    def do_rollback_twophase(
        self, connection, xid, is_prepared: bool = ..., recover: bool = ...
    ) -> None: ...
    def do_commit_twophase(
        self, connection, xid, is_prepared: bool = ..., recover: bool = ...
    ) -> None: ...

dialect = MySQLDialect_mariadbconnector
