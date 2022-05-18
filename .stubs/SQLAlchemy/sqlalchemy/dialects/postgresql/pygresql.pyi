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
from .base import UUID, PGCompiler, PGDialect, PGIdentifierPreparer
from .hstore import HSTORE
from .json import JSON, JSONB

class _PGNumeric(Numeric):
    def bind_processor(self, dialect) -> None: ...
    def result_processor(self, dialect, coltype): ...

class _PGHStore(HSTORE):
    def bind_processor(self, dialect): ...
    def result_processor(self, dialect, coltype): ...

class _PGJSON(JSON):
    def bind_processor(self, dialect): ...
    def result_processor(self, dialect, coltype): ...

class _PGJSONB(JSONB):
    def bind_processor(self, dialect): ...
    def result_processor(self, dialect, coltype): ...

class _PGUUID(UUID):
    def bind_processor(self, dialect): ...
    def result_processor(self, dialect, coltype): ...

class _PGCompiler(PGCompiler):
    def visit_mod_binary(self, binary, operator, **kw): ...
    def post_process_text(self, text): ...

class _PGIdentifierPreparer(PGIdentifierPreparer): ...

class PGDialect_pygresql(PGDialect):
    driver: str
    supports_statement_cache: bool
    statement_compiler: Any
    preparer: Any
    @classmethod
    def dbapi(cls): ...
    colspecs: Any
    dbapi_version: Any
    supports_unicode_statements: bool
    supports_unicode_binds: bool
    has_native_hstore: Any
    has_native_json: Any
    has_native_uuid: Any
    def __init__(self, **kwargs) -> None: ...
    def create_connect_args(self, url): ...
    def is_disconnect(self, e, connection, cursor): ...

dialect = PGDialect_pygresql
