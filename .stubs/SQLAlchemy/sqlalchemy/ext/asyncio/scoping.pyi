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

from ...orm.scoping import ScopedSessionMixin
from ...util import memoized_property

class async_scoped_session(ScopedSessionMixin):
    session_factory: Any
    registry: Any
    def __init__(self, session_factory, scopefunc) -> None: ...
    async def remove(self) -> None: ...
    # proxied from Session
    @classmethod
    async def close_all(cls): ...
    @classmethod
    def identity_key(cls, *args, **kwargs): ...
    @classmethod
    def object_session(cls, instance): ...
    bind: Any
    identity_map: Any
    autoflush: Any
    def __contains__(self, instance): ...
    def __iter__(self): ...
    def add(self, instance, _warn: bool = ...) -> None: ...
    def add_all(self, instances) -> None: ...
    def begin(self, **kw): ...
    def begin_nested(self, **kw): ...
    async def close(self): ...
    async def commit(self): ...
    async def connection(self, **kw): ...
    async def delete(self, instance): ...
    async def execute(
        self,
        statement,
        params: Any | None = ...,
        execution_options=...,
        bind_arguments: Any | None = ...,
        **kw,
    ): ...
    def expire(self, instance, attribute_names: Any | None = ...) -> None: ...
    def expire_all(self) -> None: ...
    def expunge(self, instance) -> None: ...
    def expunge_all(self) -> None: ...
    async def flush(self, objects: Any | None = ...) -> None: ...
    async def get(
        self,
        entity,
        ident,
        options: Any | None = ...,
        populate_existing: bool = ...,
        with_for_update: Any | None = ...,
        identity_token: Any | None = ...,
    ): ...
    def get_bind(
        self, mapper: Any | None = ..., clause: Any | None = ..., bind: Any | None = ..., **kw
    ): ...
    def is_modified(self, instance, include_collections: bool = ...): ...
    async def merge(self, instance, load: bool = ..., options: Any | None = ...): ...
    async def refresh(
        self, instance, attribute_names: Any | None = ..., with_for_update: Any | None = ...
    ): ...
    async def rollback(self): ...
    async def scalar(
        self,
        statement,
        params: Any | None = ...,
        execution_options=...,
        bind_arguments: Any | None = ...,
        **kw,
    ): ...
    async def scalars(
        self,
        statement,
        params: Any | None = ...,
        execution_options=...,
        bind_arguments: Any | None = ...,
        **kw,
    ): ...
    async def stream(
        self,
        statement,
        params: Any | None = ...,
        execution_options=...,
        bind_arguments: Any | None = ...,
        **kw,
    ): ...
    async def stream_scalars(
        self,
        statement,
        params: Any | None = ...,
        execution_options=...,
        bind_arguments: Any | None = ...,
        **kw,
    ): ...
    @property
    def dirty(self): ...
    @property
    def deleted(self): ...
    @property
    def new(self): ...
    @property
    def is_active(self): ...
    @property
    def no_autoflush(self) -> None: ...
    @memoized_property
    def info(self): ...
