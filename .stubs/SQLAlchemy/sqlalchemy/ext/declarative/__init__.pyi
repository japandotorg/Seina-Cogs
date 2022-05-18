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

from ...orm.decl_api import (
    DeclarativeMeta as DeclarativeMeta,
    as_declarative as as_declarative,
    declarative_base as declarative_base,
    declared_attr as declared_attr,
    has_inherited_table as has_inherited_table,
    synonym_for as synonym_for,
)
from .extensions import (
    AbstractConcreteBase as AbstractConcreteBase,
    ConcreteBase as ConcreteBase,
    DeferredReflection as DeferredReflection,
    instrument_declarative as instrument_declarative,
)

__all__ = [
    "declarative_base",
    "synonym_for",
    "has_inherited_table",
    "instrument_declarative",
    "declared_attr",
    "as_declarative",
    "ConcreteBase",
    "AbstractConcreteBase",
    "DeclarativeMeta",
    "DeferredReflection",
]
