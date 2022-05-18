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

from ..sql.base import CompileState, Options
from ..sql.dml import DeleteDMLState, UpdateDMLState

def save_obj(base_mapper, states, uowtransaction, single: bool = ...) -> None: ...
def post_update(base_mapper, states, uowtransaction, post_update_cols) -> None: ...
def delete_obj(base_mapper, states, uowtransaction) -> None: ...

class BulkUDCompileState(CompileState):
    class default_update_options(Options): ...

    @classmethod
    def orm_pre_session_exec(
        cls, session, statement, params, execution_options, bind_arguments, is_reentrant_invoke
    ): ...
    @classmethod
    def orm_setup_cursor_result(
        cls, session, statement, params, execution_options, bind_arguments, result
    ): ...

class BulkORMUpdate(UpdateDMLState, BulkUDCompileState):
    mapper: Any
    extra_criteria_entities: Any
    @classmethod
    def create_for_statement(cls, statement, compiler, **kw): ...

class BulkORMDelete(DeleteDMLState, BulkUDCompileState):
    mapper: Any
    extra_criteria_entities: Any
    @classmethod
    def create_for_statement(cls, statement, compiler, **kw): ...
