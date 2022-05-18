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

from . import roles
from .base import CompileState, DialectKWArgs, Executable, HasCompileState
from .elements import ClauseElement
from .selectable import HasCTE, HasPrefixes, ReturnsRows

class DMLState(CompileState):
    isupdate: bool
    isdelete: bool
    isinsert: bool
    def __init__(self, statement, compiler, **kw) -> None: ...
    @property
    def dml_table(self): ...

class InsertDMLState(DMLState):
    isinsert: bool
    include_table_with_column_exprs: bool
    statement: Any
    def __init__(self, statement, compiler, **kw) -> None: ...

class UpdateDMLState(DMLState):
    isupdate: bool
    include_table_with_column_exprs: bool
    statement: Any
    is_multitable: Any
    def __init__(self, statement, compiler, **kw) -> None: ...

class DeleteDMLState(DMLState):
    isdelete: bool
    statement: Any
    def __init__(self, statement, compiler, **kw) -> None: ...

class UpdateBase(
    roles.DMLRole,
    HasCTE,
    HasCompileState,
    DialectKWArgs,
    HasPrefixes,
    ReturnsRows,
    Executable,
    ClauseElement,
):
    __visit_name__: str
    named_with_column: bool
    is_dml: bool
    def params(self, *arg, **kw) -> None: ...
    def with_dialect_options(self, **opt) -> None: ...
    bind: Any
    def returning(self, *cols) -> None: ...
    @property
    def exported_columns(self): ...
    def with_hint(self, text, selectable: Any | None = ..., dialect_name: str = ...) -> None: ...

class ValuesBase(UpdateBase):
    __visit_name__: str
    select: Any
    table: Any
    def __init__(self, table, values, prefixes) -> None: ...
    def values(self, *args, **kwargs) -> None: ...
    def return_defaults(self, *cols) -> None: ...

class Insert(ValuesBase):
    __visit_name__: str
    select: Any
    include_insert_from_select_defaults: bool
    is_insert: bool
    def __init__(
        self,
        table,
        values: Any | None = ...,
        inline: bool = ...,
        bind: Any | None = ...,
        prefixes: Any | None = ...,
        returning: Any | None = ...,
        return_defaults: bool = ...,
        **dialect_kw,
    ) -> None: ...
    def inline(self) -> None: ...
    def from_select(self, names, select, include_defaults: bool = ...) -> None: ...

class DMLWhereBase:
    def where(self, *whereclause) -> None: ...
    def filter(self, *criteria): ...
    def filter_by(self, **kwargs): ...
    @property
    def whereclause(self): ...

class Update(DMLWhereBase, ValuesBase):
    __visit_name__: str
    is_update: bool
    def __init__(
        self,
        table,
        whereclause: Any | None = ...,
        values: Any | None = ...,
        inline: bool = ...,
        bind: Any | None = ...,
        prefixes: Any | None = ...,
        returning: Any | None = ...,
        return_defaults: bool = ...,
        preserve_parameter_order: bool = ...,
        **dialect_kw,
    ) -> None: ...
    def ordered_values(self, *args) -> None: ...
    def inline(self) -> None: ...

class Delete(DMLWhereBase, UpdateBase):
    __visit_name__: str
    is_delete: bool
    table: Any
    def __init__(
        self,
        table,
        whereclause: Any | None = ...,
        bind: Any | None = ...,
        returning: Any | None = ...,
        prefixes: Any | None = ...,
        **dialect_kw,
    ) -> None: ...
