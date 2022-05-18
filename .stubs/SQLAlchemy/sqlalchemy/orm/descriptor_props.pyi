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

from typing import Any, Generic, TypeVar

from ..sql.operators import ColumnOperators
from ..util import memoized_property
from . import util as orm_util
from .interfaces import MapperProperty, PropComparator

_T = TypeVar("_T")

class DescriptorProperty(MapperProperty):
    doc: Any
    uses_objects: bool
    key: Any
    descriptor: Any
    def instrument_class(self, mapper): ...

class CompositeProperty(DescriptorProperty):
    attrs: Any
    composite_class: Any
    active_history: Any
    deferred: Any
    group: Any
    comparator_factory: Any
    info: Any
    def __init__(self, class_, *attrs, **kwargs) -> None: ...
    def instrument_class(self, mapper) -> None: ...
    def do_init(self) -> None: ...
    @memoized_property
    def props(self): ...
    @property
    def columns(self): ...
    def get_history(self, state, dict_, passive=...): ...

    class CompositeBundle(orm_util.Bundle):
        property: Any
        def __init__(self, property_, expr) -> None: ...
        def create_row_processor(self, query, procs, labels): ...

    class Comparator(PropComparator[_T], Generic[_T]):
        __hash__: Any
        @memoized_property
        def clauses(self): ...
        def __clause_element__(self): ...
        @memoized_property
        def expression(self): ...
        def __eq__(self, other) -> ColumnOperators[_T]: ...  # type: ignore[override]
        def __ne__(self, other) -> ColumnOperators[_T]: ...  # type: ignore[override]

class ConcreteInheritedProperty(DescriptorProperty):
    descriptor: Any
    def __init__(self): ...

class SynonymProperty(DescriptorProperty):
    name: Any
    map_column: Any
    descriptor: Any
    comparator_factory: Any
    doc: Any
    info: Any
    def __init__(
        self,
        name,
        map_column: Any | None = ...,
        descriptor: Any | None = ...,
        comparator_factory: Any | None = ...,
        doc: Any | None = ...,
        info: Any | None = ...,
    ) -> None: ...
    @property
    def uses_objects(self): ...
    def get_history(self, *arg, **kw): ...
    parent: Any
    def set_parent(self, parent, init) -> None: ...
