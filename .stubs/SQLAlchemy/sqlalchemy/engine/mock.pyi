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

from _typeshed import Self
from abc import abstractmethod
from collections.abc import Mapping
from typing import Any, overload

from .base import _Executable
from .cursor import CursorResult
from .interfaces import Connectable, Dialect
from .url import URL

class MockConnection(Connectable):
    def __init__(self, dialect: Dialect, execute) -> None: ...
    @property
    def engine(self: Self) -> Self: ...  # type: ignore[override]
    @property
    def dialect(self) -> Dialect: ...
    @property
    def name(self) -> str: ...
    def schema_for_object(self, obj): ...
    def connect(self, **kwargs): ...
    def execution_options(self, **kw): ...
    def compiler(self, statement, parameters, **kwargs): ...
    def create(self, entity, **kwargs) -> None: ...
    def drop(self, entity, **kwargs) -> None: ...
    @abstractmethod
    @overload
    def execute(
        self, object_: _Executable, *multiparams: Mapping[str, Any], **params: Any
    ) -> CursorResult: ...
    @abstractmethod
    @overload
    def execute(
        self, object_: str, *multiparams: Any | tuple[Any, ...] | Mapping[str, Any], **params: Any
    ) -> CursorResult: ...

def create_mock_engine(url: URL | str, executor, **kw) -> MockConnection: ...
