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

from typing import Any, overload
from typing_extensions import Literal

from ..engine import Connection as _LegacyConnection, Engine as _LegacyEngine
from ..engine.base import OptionEngineMixin
from ..engine.mock import MockConnection
from ..engine.url import URL

NO_OPTIONS: Any

@overload
def create_engine(url: URL | str, *, strategy: Literal["mock"], **kwargs) -> MockConnection: ...  # type: ignore[misc]
@overload
def create_engine(
    url: URL | str,
    *,
    module: Any | None = ...,
    enable_from_linting: bool = ...,
    future: bool = ...,
    **kwargs,
) -> Engine: ...

class Connection(_LegacyConnection):
    def begin(self): ...
    def begin_nested(self): ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...
    def execute(self, statement, parameters: Any | None = ..., execution_options: Any | None = ...): ...  # type: ignore[override]
    def scalar(self, statement, parameters: Any | None = ..., execution_options: Any | None = ...): ...  # type: ignore[override]

class Engine(_LegacyEngine):
    transaction: Any
    run_callable: Any
    execute: Any
    scalar: Any
    table_names: Any
    has_table: Any
    def begin(self) -> None: ...  # type: ignore[override]
    def connect(self): ...

class OptionEngine(OptionEngineMixin, Engine): ...  # type: ignore[misc]
