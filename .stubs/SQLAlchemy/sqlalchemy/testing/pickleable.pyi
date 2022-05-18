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

from . import fixtures

class User(fixtures.ComparableEntity): ...
class Order(fixtures.ComparableEntity): ...
class Dingaling(fixtures.ComparableEntity): ...
class EmailUser(User): ...
class Address(fixtures.ComparableEntity): ...
class Child1(fixtures.ComparableEntity): ...
class Child2(fixtures.ComparableEntity): ...
class Parent(fixtures.ComparableEntity): ...

class Screen:
    obj: Any
    parent: Any
    def __init__(self, obj, parent: Any | None = ...) -> None: ...

class Foo:
    data: str
    stuff: Any
    moredata: Any
    def __init__(self, moredata, stuff: str = ...) -> None: ...
    __hash__: Any
    def __eq__(self, other): ...

class Bar:
    x: Any
    y: Any
    def __init__(self, x, y) -> None: ...
    __hash__: Any
    def __eq__(self, other): ...

class OldSchool:
    x: Any
    y: Any
    def __init__(self, x, y) -> None: ...
    def __eq__(self, other): ...

class OldSchoolWithoutCompare:
    x: Any
    y: Any
    def __init__(self, x, y) -> None: ...

class BarWithoutCompare:
    x: Any
    y: Any
    def __init__(self, x, y) -> None: ...

class NotComparable:
    data: Any
    def __init__(self, data) -> None: ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...

class BrokenComparable:
    data: Any
    def __init__(self, data) -> None: ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...
