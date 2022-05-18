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

def add_class(classname, cls, decl_class_registry) -> None: ...
def remove_class(classname, cls, decl_class_registry) -> None: ...

class _MultipleClassMarker:
    on_remove: Any
    contents: Any
    def __init__(self, classes, on_remove: Any | None = ...) -> None: ...
    def remove_item(self, cls) -> None: ...
    def __iter__(self): ...
    def attempt_get(self, path, key): ...
    def add_item(self, item) -> None: ...

class _ModuleMarker:
    parent: Any
    name: Any
    contents: Any
    mod_ns: Any
    path: Any
    def __init__(self, name, parent) -> None: ...
    def __contains__(self, name): ...
    def __getitem__(self, name): ...
    def resolve_attr(self, key): ...
    def get_module(self, name): ...
    def add_class(self, name, cls): ...
    def remove_class(self, name, cls) -> None: ...

class _ModNS:
    def __init__(self, parent) -> None: ...
    def __getattr__(self, key): ...

class _GetColumns:
    cls: Any
    def __init__(self, cls) -> None: ...
    def __getattr__(self, key): ...

class _GetTable:
    key: Any
    metadata: Any
    def __init__(self, key, metadata) -> None: ...
    def __getattr__(self, key): ...

class _class_resolver:
    cls: Any
    prop: Any
    arg: Any
    fallback: Any
    favor_tables: Any
    def __init__(self, cls, prop, fallback, arg, favor_tables: bool = ...) -> None: ...
    def __call__(self): ...
