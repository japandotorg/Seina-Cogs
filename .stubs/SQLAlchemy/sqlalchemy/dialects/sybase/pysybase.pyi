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

from sqlalchemy import types as sqltypes
from sqlalchemy.dialects.sybase.base import SybaseDialect, SybaseExecutionContext, SybaseSQLCompiler

class _SybNumeric(sqltypes.Numeric):
    def result_processor(self, dialect, type_): ...

class SybaseExecutionContext_pysybase(SybaseExecutionContext):
    def set_ddl_autocommit(self, dbapi_connection, value) -> None: ...
    def pre_exec(self) -> None: ...

class SybaseSQLCompiler_pysybase(SybaseSQLCompiler):
    def bindparam_string(self, name, **kw): ...

class SybaseDialect_pysybase(SybaseDialect):
    driver: str
    statement_compiler: Any
    supports_statement_cache: bool
    colspecs: Any
    @classmethod
    def dbapi(cls): ...
    def create_connect_args(self, url): ...
    def do_executemany(self, cursor, statement, parameters, context: Any | None = ...) -> None: ...
    def is_disconnect(self, e, connection, cursor): ...

dialect = SybaseDialect_pysybase
