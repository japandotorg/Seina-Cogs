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

from ...connectors.mxodbc import MxODBCConnector
from .base import VARBINARY, MSDialect, _MSDate, _MSTime
from .pyodbc import MSExecutionContext_pyodbc, _MSNumeric_pyodbc

class _MSNumeric_mxodbc(_MSNumeric_pyodbc): ...

class _MSDate_mxodbc(_MSDate):
    def bind_processor(self, dialect): ...

class _MSTime_mxodbc(_MSTime):
    def bind_processor(self, dialect): ...

class _VARBINARY_mxodbc(VARBINARY):
    def bind_processor(self, dialect): ...

class MSExecutionContext_mxodbc(MSExecutionContext_pyodbc): ...

class MSDialect_mxodbc(MxODBCConnector, MSDialect):
    supports_statement_cache: bool
    colspecs: Any
    description_encoding: Any
    def __init__(self, description_encoding: Any | None = ..., **params) -> None: ...

dialect = MSDialect_mxodbc
