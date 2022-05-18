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

from .. import exc as sa_exc

NO_STATE: Any

class StaleDataError(sa_exc.SQLAlchemyError): ...

ConcurrentModificationError = StaleDataError

class FlushError(sa_exc.SQLAlchemyError): ...
class UnmappedError(sa_exc.InvalidRequestError): ...
class ObjectDereferencedError(sa_exc.SQLAlchemyError): ...

class DetachedInstanceError(sa_exc.SQLAlchemyError):
    code: str

class UnmappedInstanceError(UnmappedError):
    def __init__(self, obj, msg: Any | None = ...) -> None: ...
    def __reduce__(self): ...

class UnmappedClassError(UnmappedError):
    def __init__(self, cls, msg: Any | None = ...) -> None: ...
    def __reduce__(self): ...

class ObjectDeletedError(sa_exc.InvalidRequestError):
    def __init__(self, state, msg: Any | None = ...) -> None: ...
    def __reduce__(self): ...

class UnmappedColumnError(sa_exc.InvalidRequestError): ...

class LoaderStrategyException(sa_exc.InvalidRequestError):
    def __init__(self, applied_to_property_type, requesting_property, applies_to, actual_strategy_type, strategy_key) -> None: ...
