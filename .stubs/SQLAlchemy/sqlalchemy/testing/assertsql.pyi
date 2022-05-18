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

class AssertRule:
    is_consumed: bool
    errormessage: Any
    consume_statement: bool
    def process_statement(self, execute_observed) -> None: ...
    def no_more_statements(self) -> None: ...

class SQLMatchRule(AssertRule): ...

class CursorSQL(SQLMatchRule):
    statement: Any
    params: Any
    consume_statement: Any
    def __init__(self, statement, params: Any | None = ..., consume_statement: bool = ...) -> None: ...
    errormessage: Any
    is_consumed: bool
    def process_statement(self, execute_observed) -> None: ...

class CompiledSQL(SQLMatchRule):
    statement: Any
    params: Any
    dialect: Any
    def __init__(self, statement, params: Any | None = ..., dialect: str = ...) -> None: ...
    is_consumed: bool
    errormessage: Any
    def process_statement(self, execute_observed) -> None: ...

class RegexSQL(CompiledSQL):
    regex: Any
    orig_regex: Any
    params: Any
    dialect: Any
    def __init__(self, regex, params: Any | None = ..., dialect: str = ...) -> None: ...

class DialectSQL(CompiledSQL): ...

class CountStatements(AssertRule):
    count: Any
    def __init__(self, count) -> None: ...
    def process_statement(self, execute_observed) -> None: ...
    def no_more_statements(self) -> None: ...

class AllOf(AssertRule):
    rules: Any
    def __init__(self, *rules) -> None: ...
    is_consumed: bool
    errormessage: Any
    def process_statement(self, execute_observed) -> None: ...

class EachOf(AssertRule):
    rules: Any
    def __init__(self, *rules) -> None: ...
    errormessage: Any
    is_consumed: bool
    def process_statement(self, execute_observed) -> None: ...
    def no_more_statements(self) -> None: ...

class Conditional(EachOf):
    def __init__(self, condition, rules, else_rules) -> None: ...

class Or(AllOf):
    is_consumed: bool
    errormessage: Any
    def process_statement(self, execute_observed) -> None: ...

class SQLExecuteObserved:
    context: Any
    clauseelement: Any
    parameters: Any
    statements: Any
    def __init__(self, context, clauseelement, multiparams, params) -> None: ...

class SQLCursorExecuteObserved: ...

class SQLAsserter:
    accumulated: Any
    def __init__(self) -> None: ...
    def assert_(self, *rules) -> None: ...

def assert_engine(engine) -> None: ...
