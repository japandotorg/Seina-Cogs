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

from .base import Pool as Pool, reset_commit as reset_commit, reset_none as reset_none, reset_rollback as reset_rollback
from .dbapi_proxy import clear_managers as clear_managers, manage as manage
from .impl import (
    AssertionPool as AssertionPool,
    AsyncAdaptedQueuePool as AsyncAdaptedQueuePool,
    FallbackAsyncAdaptedQueuePool as FallbackAsyncAdaptedQueuePool,
    NullPool as NullPool,
    QueuePool as QueuePool,
    SingletonThreadPool as SingletonThreadPool,
    StaticPool as StaticPool,
)

__all__ = [
    "Pool",
    "reset_commit",
    "reset_none",
    "reset_rollback",
    "clear_managers",
    "manage",
    "AssertionPool",
    "NullPool",
    "QueuePool",
    "AsyncAdaptedQueuePool",
    "FallbackAsyncAdaptedQueuePool",
    "SingletonThreadPool",
    "StaticPool",
]
