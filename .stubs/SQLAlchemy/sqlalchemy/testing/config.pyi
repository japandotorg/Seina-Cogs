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

requirements: Any
db: Any
db_url: Any
db_opts: Any
file_config: Any
test_schema: Any
test_schema_2: Any
any_async: bool
ident: str

def combinations(*comb, **kw): ...
def combinations_list(arg_iterable, **kw): ...
def fixture(*arg, **kw): ...
def get_current_test_name(): ...
def mark_base_test_class(): ...

class Config:
    db: Any
    db_opts: Any
    options: Any
    file_config: Any
    test_schema: str
    test_schema_2: str
    is_async: Any
    def __init__(self, db, db_opts, options, file_config) -> None: ...
    @classmethod
    def register(cls, db, db_opts, options, file_config): ...
    @classmethod
    def set_as_current(cls, config, namespace) -> None: ...
    @classmethod
    def push_engine(cls, db, namespace) -> None: ...
    @classmethod
    def push(cls, config, namespace) -> None: ...
    @classmethod
    def pop(cls, namespace) -> None: ...
    @classmethod
    def reset(cls, namespace) -> None: ...
    @classmethod
    def all_configs(cls): ...
    @classmethod
    def all_dbs(cls) -> None: ...
    def skip_test(self, msg) -> None: ...

def skip_test(msg) -> None: ...
def async_test(fn): ...
