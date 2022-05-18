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

from .. import util
from .descriptor_props import (
    CompositeProperty as CompositeProperty,
    ConcreteInheritedProperty as ConcreteInheritedProperty,
    SynonymProperty as SynonymProperty,
)
from .interfaces import PropComparator, StrategizedProperty
from .relationships import RelationshipProperty as RelationshipProperty

__all__ = ["ColumnProperty", "CompositeProperty", "ConcreteInheritedProperty", "RelationshipProperty", "SynonymProperty"]

class ColumnProperty(StrategizedProperty):
    logger: Any
    strategy_wildcard_key: str
    inherit_cache: bool
    columns: Any
    group: Any
    deferred: Any
    raiseload: Any
    instrument: Any
    comparator_factory: Any
    descriptor: Any
    active_history: Any
    expire_on_flush: Any
    info: Any
    doc: Any
    strategy_key: Any
    def __init__(self, *columns, **kwargs) -> None: ...
    def __clause_element__(self): ...
    @property
    def expression(self): ...
    def instrument_class(self, mapper) -> None: ...
    def do_init(self) -> None: ...
    def copy(self): ...
    def merge(
        self, session, source_state, source_dict, dest_state, dest_dict, load, _recursive, _resolve_conflict_map
    ) -> None: ...

    class Comparator(util.MemoizedSlots, PropComparator[Any]):
        expressions: Any
        def _memoized_method___clause_element__(self): ...
        def operate(self, op, *other, **kwargs): ...
        def reverse_operate(self, op, other, **kwargs): ...
