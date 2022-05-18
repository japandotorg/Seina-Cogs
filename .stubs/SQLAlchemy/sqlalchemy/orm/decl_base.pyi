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

class _MapperConfig:
    @classmethod
    def setup_mapping(cls, registry, cls_, dict_, table, mapper_kw): ...
    cls: Any
    classname: Any
    properties: Any
    declared_attr_reg: Any
    def __init__(self, registry, cls_, mapper_kw) -> None: ...
    def set_cls_attribute(self, attrname, value): ...

class _ImperativeMapperConfig(_MapperConfig):
    dict_: Any
    local_table: Any
    inherits: Any
    def __init__(self, registry, cls_, table, mapper_kw) -> None: ...
    def map(self, mapper_kw=...): ...

class _ClassScanMapperConfig(_MapperConfig):
    dict_: Any
    local_table: Any
    persist_selectable: Any
    declared_columns: Any
    column_copies: Any
    table_args: Any
    tablename: Any
    mapper_args: Any
    mapper_args_fn: Any
    inherits: Any
    def __init__(self, registry, cls_, dict_, table, mapper_kw) -> None: ...
    def map(self, mapper_kw=...): ...

class _DeferredMapperConfig(_ClassScanMapperConfig):
    @property
    def cls(self): ...
    @cls.setter
    def cls(self, class_) -> None: ...
    @classmethod
    def has_cls(cls, class_): ...
    @classmethod
    def raise_unmapped_for_cls(cls, class_) -> None: ...
    @classmethod
    def config_for_cls(cls, class_): ...
    @classmethod
    def classes_for_base(cls, base_cls, sort: bool = ...): ...
    def map(self, mapper_kw=...): ...
