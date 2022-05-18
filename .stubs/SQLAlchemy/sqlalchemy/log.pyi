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

from _typeshed import Self
from logging import Logger
from typing import Any, TypeVar, overload
from typing_extensions import Literal, TypeAlias

_ClsT = TypeVar("_ClsT", bound=type)
_EchoFlag: TypeAlias = bool | Literal["debug"] | None

rootlogger: Any

def class_logger(cls: _ClsT) -> _ClsT: ...

class Identified:
    logging_name: str | None

class InstanceLogger:
    echo: _EchoFlag
    logger: Logger
    def __init__(self, echo: _EchoFlag, name: str | None) -> None: ...
    def debug(self, msg, *args, **kwargs) -> None: ...
    def info(self, msg, *args, **kwargs) -> None: ...
    def warning(self, msg, *args, **kwargs) -> None: ...
    warn = warning
    def error(self, msg, *args, **kwargs) -> None: ...
    def exception(self, msg, *args, **kwargs) -> None: ...
    def critical(self, msg, *args, **kwargs) -> None: ...
    def log(self, level, msg, *args, **kwargs) -> None: ...
    def isEnabledFor(self, level): ...
    def getEffectiveLevel(self): ...

def instance_logger(instance: Identified, echoflag: _EchoFlag = ...) -> None: ...

class echo_property:
    __doc__: str
    @overload
    def __get__(self: Self, instance: None, owner: object) -> Self: ...
    @overload
    def __get__(self, instance: Identified, owner: object) -> _EchoFlag: ...
    def __set__(self, instance: Identified, value: _EchoFlag) -> None: ...
