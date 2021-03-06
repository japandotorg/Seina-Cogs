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

from collections.abc import Iterable, Iterator
from typing import Any, TypeVar, overload

CallExpr = Any  # from mypy.nodes
Context = Any  # from mypy.nodes
Expression = Any  # from mypy.nodes
JsonDict = Any  # from mypy.nodes
NameExpr = Any  # from mypy.nodes
Statement = Any  # from mypy.nodes
TypeInfo = Any  # from mypy.nodes
AttributeContext = Any  # from mypy.plugin
ClassDefContext = Any  # from mypy.plugin
DynamicClassDefContext = Any  # from mypy.plugin
SemanticAnalyzerPluginInterface = Any  # from mypy.plugin
Type = Any  # from mypy.types

_TArgType = TypeVar("_TArgType", bound=CallExpr | NameExpr)

class SQLAlchemyAttribute:
    name: Any
    line: Any
    column: Any
    type: Any
    info: Any
    def __init__(
        self, name: str, line: int, column: int, typ: Type | None, info: TypeInfo
    ) -> None: ...
    def serialize(self) -> JsonDict: ...
    def expand_typevar_from_subtype(self, sub_type: TypeInfo) -> None: ...
    @classmethod
    def deserialize(
        cls, info: TypeInfo, data: JsonDict, api: SemanticAnalyzerPluginInterface
    ) -> SQLAlchemyAttribute: ...

def name_is_dunder(name): ...
def establish_as_sqlalchemy(info: TypeInfo) -> None: ...
def set_is_base(info: TypeInfo) -> None: ...
def get_is_base(info: TypeInfo) -> bool: ...
def has_declarative_base(info: TypeInfo) -> bool: ...
def set_has_table(info: TypeInfo) -> None: ...
def get_has_table(info: TypeInfo) -> bool: ...
def get_mapped_attributes(
    info: TypeInfo, api: SemanticAnalyzerPluginInterface
) -> list[SQLAlchemyAttribute] | None: ...
def set_mapped_attributes(info: TypeInfo, attributes: list[SQLAlchemyAttribute]) -> None: ...
def fail(api: SemanticAnalyzerPluginInterface, msg: str, ctx: Context) -> None: ...
def add_global(
    ctx: ClassDefContext | DynamicClassDefContext, module: str, symbol_name: str, asname: str
) -> None: ...
@overload
def get_callexpr_kwarg(
    callexpr: CallExpr, name: str, *, expr_types: None = ...
) -> CallExpr | NameExpr | None: ...
@overload
def get_callexpr_kwarg(
    callexpr: CallExpr, name: str, *, expr_types: tuple[type[_TArgType], ...]
) -> _TArgType | None: ...
def flatten_typechecking(stmts: Iterable[Statement]) -> Iterator[Statement]: ...
def unbound_to_instance(api: SemanticAnalyzerPluginInterface, typ: Type) -> Type: ...
def info_for_cls(cls, api: SemanticAnalyzerPluginInterface) -> TypeInfo | None: ...
def expr_to_mapped_constructor(expr: Expression) -> CallExpr: ...
