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

from collections.abc import Callable
from typing import Any

MypyFile = Any  # from mypy.nodes
AttributeContext = Any  # from mypy.plugin
ClassDefContext = Any  # from mypy.plugin
DynamicClassDefContext = Any  # from mypy.plugin
Plugin = Any  # from mypy.plugin
Type = Any  # from mypy.types

class SQLAlchemyPlugin(Plugin):
    def get_dynamic_class_hook(
        self, fullname: str
    ) -> Callable[[DynamicClassDefContext], None] | None: ...
    def get_customize_class_mro_hook(
        self, fullname: str
    ) -> Callable[[ClassDefContext], None] | None: ...
    def get_class_decorator_hook(
        self, fullname: str
    ) -> Callable[[ClassDefContext], None] | None: ...
    def get_metaclass_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None: ...
    def get_base_class_hook(self, fullname: str) -> Callable[[ClassDefContext], None] | None: ...
    def get_attribute_hook(self, fullname: str) -> Callable[[AttributeContext], Type] | None: ...
    def get_additional_deps(self, file: MypyFile) -> list[tuple[int, str, int]]: ...

def plugin(version: str) -> type[SQLAlchemyPlugin]: ...
