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

from . import assertions
from .entities import ComparableEntity as ComparableEntity

class TestBase:
    __requires__: Any
    __unsupported_on__: Any
    __only_on__: Any
    __skip_if__: Any
    __leave_connections_for_teardown__: bool
    def assert_(self, val, msg: Any | None = ...) -> None: ...
    def connection_no_trans(self) -> None: ...
    def connection(self) -> None: ...
    def registry(self, metadata) -> None: ...
    def future_connection(self, future_engine, connection) -> None: ...
    def future_engine(self) -> None: ...
    def testing_engine(self): ...
    def async_testing_engine(self, testing_engine): ...
    def metadata(self, request) -> None: ...
    def trans_ctx_manager_fixture(self, request, metadata): ...

class FutureEngineMixin: ...

class TablesTest(TestBase):
    run_setup_bind: str
    run_define_tables: str
    run_create_tables: str
    run_inserts: str
    run_deletes: str
    run_dispose_bind: Any
    bind: Any
    tables: Any
    other: Any
    sequences: Any
    @property
    def tables_test_metadata(self): ...
    @classmethod
    def setup_bind(cls): ...
    @classmethod
    def dispose_bind(cls, bind) -> None: ...
    @classmethod
    def define_tables(cls, metadata) -> None: ...
    @classmethod
    def fixtures(cls): ...
    @classmethod
    def insert_data(cls, connection) -> None: ...
    def sql_count_(self, count, fn) -> None: ...
    def sql_eq_(self, callable_, statements) -> None: ...

class NoCache: ...

class RemovesEvents:
    def event_listen(self, target, name, fn, **kw) -> None: ...

def fixture_session(**kw): ...
def stop_test_class_inside_fixtures(cls) -> None: ...
def after_test() -> None: ...

class ORMTest(TestBase): ...

class MappedTest(TablesTest, assertions.AssertsExecutionResults):
    run_setup_classes: str
    run_setup_mappers: str
    classes: Any
    @classmethod
    def setup_classes(cls) -> None: ...
    @classmethod
    def setup_mappers(cls) -> None: ...

class DeclarativeMappedTest(MappedTest):
    run_setup_classes: str
    run_setup_mappers: str

class ComputedReflectionFixtureTest(TablesTest):
    run_inserts: Any
    run_deletes: Any
    __backend__: bool
    __requires__: Any
    regexp: Any
    def normalize(self, text): ...
    @classmethod
    def define_tables(cls, metadata) -> None: ...
