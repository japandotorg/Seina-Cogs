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

from ..sql.base import Generative
from .interfaces import LoaderOption

class Load(Generative, LoaderOption):
    path: Any
    context: Any
    local_opts: Any
    is_class_strategy: bool
    def __init__(self, entity) -> None: ...
    @classmethod
    def for_existing_path(cls, path): ...
    is_opts_only: bool
    strategy: Any
    propagate_to_loaders: bool
    def process_compile_state_replaced_entities(self, compile_state, mapper_entities) -> None: ...
    def process_compile_state(self, compile_state) -> None: ...
    def options(self, *opts) -> None: ...
    def set_relationship_strategy(
        self, attr, strategy, propagate_to_loaders: bool = ...
    ) -> None: ...
    def set_column_strategy(
        self, attrs, strategy, opts: Any | None = ..., opts_only: bool = ...
    ) -> None: ...
    def set_generic_strategy(self, attrs, strategy) -> None: ...
    def set_class_strategy(self, strategy, opts) -> None: ...
    # added dynamically at runtime
    def contains_eager(self, attr, alias: Any | None = ...): ...
    def load_only(self, *attrs): ...
    def joinedload(self, attr, innerjoin: Any | None = ...): ...
    def subqueryload(self, attr): ...
    def selectinload(self, attr): ...
    def lazyload(self, attr): ...
    def immediateload(self, attr): ...
    def noload(self, attr): ...
    def raiseload(self, attr, sql_only: bool = ...): ...
    def defaultload(self, attr): ...
    def defer(self, key, raiseload: bool = ...): ...
    def undefer(self, key): ...
    def undefer_group(self, name): ...
    def with_expression(self, key, expression): ...
    def selectin_polymorphic(self, classes): ...

class _UnboundLoad(Load):
    path: Any
    local_opts: Any
    def __init__(self) -> None: ...

class loader_option:
    def __init__(self) -> None: ...
    name: Any
    fn: Any
    def __call__(self, fn): ...

def contains_eager(loadopt, attr, alias: Any | None = ...): ...
def load_only(loadopt, *attrs): ...
def joinedload(loadopt, attr, innerjoin: Any | None = ...): ...
def subqueryload(loadopt, attr): ...
def selectinload(loadopt, attr): ...
def lazyload(loadopt, attr): ...
def immediateload(loadopt, attr): ...
def noload(loadopt, attr): ...
def raiseload(loadopt, attr, sql_only: bool = ...): ...
def defaultload(loadopt, attr): ...
def defer(loadopt, key, raiseload: bool = ...): ...
def undefer(loadopt, key): ...
def undefer_group(loadopt, name): ...
def with_expression(loadopt, key, expression): ...
def selectin_polymorphic(loadopt, classes): ...
