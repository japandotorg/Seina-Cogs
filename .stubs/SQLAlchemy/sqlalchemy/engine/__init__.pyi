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

from ..sql import ddl as ddl
from . import events as events, util as util
from .base import (
    Connection as Connection,
    Engine as Engine,
    NestedTransaction as NestedTransaction,
    RootTransaction as RootTransaction,
    Transaction as Transaction,
    TwoPhaseTransaction as TwoPhaseTransaction,
)
from .create import create_engine as create_engine, engine_from_config as engine_from_config
from .cursor import (
    BaseCursorResult as BaseCursorResult,
    BufferedColumnResultProxy as BufferedColumnResultProxy,
    BufferedColumnRow as BufferedColumnRow,
    BufferedRowResultProxy as BufferedRowResultProxy,
    CursorResult as CursorResult,
    FullyBufferedResultProxy as FullyBufferedResultProxy,
    LegacyCursorResult as LegacyCursorResult,
    ResultProxy as ResultProxy,
)
from .interfaces import (
    AdaptedConnection as AdaptedConnection,
    Compiled as Compiled,
    Connectable as Connectable,
    CreateEnginePlugin as CreateEnginePlugin,
    Dialect as Dialect,
    ExceptionContext as ExceptionContext,
    ExecutionContext as ExecutionContext,
    TypeCompiler as TypeCompiler,
)
from .mock import create_mock_engine as create_mock_engine
from .reflection import Inspector as Inspector
from .result import (
    ChunkedIteratorResult as ChunkedIteratorResult,
    FrozenResult as FrozenResult,
    IteratorResult as IteratorResult,
    MappingResult as MappingResult,
    MergedResult as MergedResult,
    Result as Result,
    ScalarResult as ScalarResult,
    result_tuple as result_tuple,
)
from .row import BaseRow as BaseRow, LegacyRow as LegacyRow, Row as Row, RowMapping as RowMapping
from .url import URL as URL, make_url as make_url
from .util import connection_memoize as connection_memoize
