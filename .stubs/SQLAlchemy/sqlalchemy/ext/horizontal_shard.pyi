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

from typing import Any, Generic, TypeVar

from ..orm.query import Query
from ..orm.session import Session

_T = TypeVar("_T")

class ShardedQuery(Query[_T], Generic[_T]):
    id_chooser: Any
    query_chooser: Any
    execute_chooser: Any
    def __init__(self, *args, **kwargs) -> None: ...
    def set_shard(self, shard_id): ...

class ShardedSession(Session):
    shard_chooser: Any
    id_chooser: Any
    execute_chooser: Any
    query_chooser: Any
    def __init__(
        self, shard_chooser, id_chooser, execute_chooser: Any | None = ..., shards: Any | None = ..., query_cls=..., **kwargs
    ): ...
    def connection_callable(self, mapper: Any | None = ..., instance: Any | None = ..., shard_id: Any | None = ..., **kwargs): ...
    def get_bind(self, mapper: Any | None = ..., shard_id: Any | None = ..., instance: Any | None = ..., clause: Any | None = ..., **kw): ...  # type: ignore[override]
    def bind_shard(self, shard_id, bind) -> None: ...
