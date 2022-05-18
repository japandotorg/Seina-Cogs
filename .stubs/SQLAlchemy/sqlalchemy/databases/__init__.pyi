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

from ..dialects.firebird import base as firebird_base
from ..dialects.mssql import base as mssql_base
from ..dialects.mysql import base as mysql_base
from ..dialects.oracle import base as oracle_base
from ..dialects.postgresql import base as postgresql_base
from ..dialects.sqlite import base as sqlite_base
from ..dialects.sybase import base as sybase_base

__all__ = ("firebird", "mssql", "mysql", "postgresql", "sqlite", "oracle", "sybase")

firebird = firebird_base
mssql = mssql_base
mysql = mysql_base
oracle = oracle_base
postgresql = postgresql_base
postgres = postgresql_base
sqlite = sqlite_base
sybase = sybase_base
