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

from . import util

AssignmentStmt = Any  # from mypy.nodes
NameExpr = Any  # from mypy.nodes
StrExpr = Any  # from mypy.nodes
SemanticAnalyzerPluginInterface = Any  # from mypy.plugin
ProperType = Any  # from mypy.types

def apply_mypy_mapped_attr(
    cls, api: SemanticAnalyzerPluginInterface, item: NameExpr | StrExpr, attributes: list[util.SQLAlchemyAttribute]
) -> None: ...
def re_apply_declarative_assignments(
    cls, api: SemanticAnalyzerPluginInterface, attributes: list[util.SQLAlchemyAttribute]
) -> None: ...
def apply_type_to_mapped_statement(
    api: SemanticAnalyzerPluginInterface,
    stmt: AssignmentStmt,
    lvalue: NameExpr,
    left_hand_explicit_type: ProperType | None,
    python_type_for_type: ProperType | None,
) -> None: ...
def add_additional_orm_attributes(
    cls, api: SemanticAnalyzerPluginInterface, attributes: list[util.SQLAlchemyAttribute]
) -> None: ...
