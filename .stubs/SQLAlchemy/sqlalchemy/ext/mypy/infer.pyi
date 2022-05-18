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

from collections.abc import Sequence
from typing import Any

AssignmentStmt = Any  # from mypy.nodes
Expression = Any  # from mypy.nodes
RefExpr = Any  # from mypy.nodes
TypeInfo = Any  # from mypy.nodes
Var = Any  # from mypy.nodes
StrExpr = Any  # from mypy.nodes
SemanticAnalyzerPluginInterface = Any  # from mypy.plugin
ProperType = Any  # from mypy.types

def infer_type_from_right_hand_nameexpr(
    api: SemanticAnalyzerPluginInterface,
    stmt: AssignmentStmt,
    node: Var,
    left_hand_explicit_type: ProperType | None,
    infer_from_right_side: RefExpr,
) -> ProperType | None: ...
def infer_type_from_left_hand_type_only(
    api: SemanticAnalyzerPluginInterface, node: Var, left_hand_explicit_type: ProperType | None
) -> ProperType | None: ...
def extract_python_type_from_typeengine(
    api: SemanticAnalyzerPluginInterface, node: TypeInfo, type_args: Sequence[Expression]
) -> ProperType: ...
