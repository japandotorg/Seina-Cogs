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

from ..orm import interfaces

HYBRID_METHOD: Any
HYBRID_PROPERTY: Any

class hybrid_method(interfaces.InspectionAttrInfo):
    is_attribute: bool
    extension_type: Any
    func: Any
    def __init__(self, func, expr: Any | None = ...) -> None: ...
    def __get__(self, instance, owner): ...
    expr: Any
    def expression(self, expr): ...

class hybrid_property(interfaces.InspectionAttrInfo):
    is_attribute: bool
    extension_type: Any
    fget: Any
    fset: Any
    fdel: Any
    expr: Any
    custom_comparator: Any
    update_expr: Any
    def __init__(
        self,
        fget,
        fset: Any | None = ...,
        fdel: Any | None = ...,
        expr: Any | None = ...,
        custom_comparator: Any | None = ...,
        update_expr: Any | None = ...,
    ) -> None: ...
    def __get__(self, instance, owner): ...
    def __set__(self, instance, value) -> None: ...
    def __delete__(self, instance) -> None: ...
    @property
    def overrides(self): ...
    def getter(self, fget): ...
    def setter(self, fset): ...
    def deleter(self, fdel): ...
    def expression(self, expr): ...
    def comparator(self, comparator): ...
    def update_expression(self, meth): ...

class Comparator(interfaces.PropComparator[Any]):
    property: Any
    expression: Any
    def __init__(self, expression) -> None: ...
    def __clause_element__(self): ...
    def adapt_to_entity(self, adapt_to_entity): ...

_property = property

class ExprComparator(Comparator):
    cls: Any
    expression: Any
    hybrid: Any
    def __init__(self, cls, expression, hybrid) -> None: ...
    def __getattr__(self, key): ...
    @_property
    def info(self): ...
    @_property
    def property(self): ...
    def operate(self, op, *other, **kwargs): ...
    def reverse_operate(self, op, other, **kwargs): ...
