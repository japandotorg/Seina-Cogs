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

# TODO: Tempory copy of _typeshed.dbapi, until that file is available in all typecheckers.
# Does not exist at runtime.

from collections.abc import Mapping, Sequence
from typing import Any, Protocol
from typing_extensions import TypeAlias

DBAPITypeCode: TypeAlias = Any | None
# Strictly speaking, this should be a Sequence, but the type system does
# not support fixed-length sequences.
DBAPIColumnDescription: TypeAlias = tuple[str, DBAPITypeCode, int | None, int | None, int | None, int | None, bool | None]

class DBAPIConnection(Protocol):
    def close(self) -> object: ...
    def commit(self) -> object: ...
    # optional:
    # def rollback(self) -> Any: ...
    def cursor(self) -> DBAPICursor: ...

class DBAPICursor(Protocol):
    @property
    def description(self) -> Sequence[DBAPIColumnDescription] | None: ...
    @property
    def rowcount(self) -> int: ...
    # optional:
    # def callproc(self, __procname: str, __parameters: Sequence[Any] = ...) -> Sequence[Any]: ...
    def close(self) -> object: ...
    def execute(self, __operation: str, __parameters: Sequence[Any] | Mapping[str, Any] = ...) -> object: ...
    def executemany(self, __operation: str, __seq_of_parameters: Sequence[Sequence[Any]]) -> object: ...
    def fetchone(self) -> Sequence[Any] | None: ...
    def fetchmany(self, __size: int = ...) -> Sequence[Sequence[Any]]: ...
    def fetchall(self) -> Sequence[Sequence[Any]]: ...
    # optional:
    # def nextset(self) -> None | Literal[True]: ...
    arraysize: int
    def setinputsizes(self, __sizes: Sequence[DBAPITypeCode | int | None]) -> object: ...
    def setoutputsize(self, __size: int, __column: int = ...) -> object: ...
