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

from .langhelpers import (
    decorator as decorator,
    inject_docstring_text as inject_docstring_text,
    inject_param_text as inject_param_text,
)

SQLALCHEMY_WARN_20: bool

def warn_deprecated(msg, version, stacklevel: int = ..., code: Any | None = ...) -> None: ...
def warn_deprecated_limited(
    msg, args, version, stacklevel: int = ..., code: Any | None = ...
) -> None: ...
def warn_deprecated_20(msg, stacklevel: int = ..., code: Any | None = ...) -> None: ...
def deprecated_cls(version, message, constructor: str = ...): ...
def deprecated_20_cls(
    clsname, alternative: Any | None = ..., constructor: str = ..., becomes_legacy: bool = ...
): ...
def deprecated(
    version,
    message: Any | None = ...,
    add_deprecation_to_docstring: bool = ...,
    warning: Any | None = ...,
    enable_warnings: bool = ...,
): ...
def moved_20(message, **kw): ...
def deprecated_20(api_name, alternative: Any | None = ..., becomes_legacy: bool = ..., **kw): ...
def deprecated_params(**specs): ...
