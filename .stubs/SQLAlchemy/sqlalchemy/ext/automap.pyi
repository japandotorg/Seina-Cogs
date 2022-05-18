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

def classname_for_table(base, tablename, table): ...
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint): ...
def name_for_collection_relationship(base, local_cls, referred_cls, constraint): ...
def generate_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw): ...

class AutomapBase:
    __abstract__: bool
    classes: Any
    @classmethod
    def prepare(
        cls,
        autoload_with: Any | None = ...,
        engine: Any | None = ...,
        reflect: bool = ...,
        schema: Any | None = ...,
        classname_for_table: Any | None = ...,
        collection_class: Any | None = ...,
        name_for_scalar_relationship: Any | None = ...,
        name_for_collection_relationship: Any | None = ...,
        generate_relationship: Any | None = ...,
        reflection_options=...,
    ) -> None: ...

def automap_base(declarative_base: Any | None = ..., **kw): ...
