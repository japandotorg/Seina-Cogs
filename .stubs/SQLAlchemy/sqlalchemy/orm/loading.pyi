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

def instances(cursor, context): ...
def merge_frozen_result(session, statement, frozen_result, load: bool = ...): ...
def merge_result(query, iterator, load: bool = ...): ...
def get_from_identity(session, mapper, key, passive): ...
def load_on_ident(
    session,
    statement,
    key,
    load_options: Any | None = ...,
    refresh_state: Any | None = ...,
    with_for_update: Any | None = ...,
    only_load_props: Any | None = ...,
    no_autoflush: bool = ...,
    bind_arguments=...,
    execution_options=...,
): ...
def load_on_pk_identity(
    session,
    statement,
    primary_key_identity,
    load_options: Any | None = ...,
    refresh_state: Any | None = ...,
    with_for_update: Any | None = ...,
    only_load_props: Any | None = ...,
    identity_token: Any | None = ...,
    no_autoflush: bool = ...,
    bind_arguments=...,
    execution_options=...,
): ...

class PostLoad:
    loaders: Any
    states: Any
    load_keys: Any
    def __init__(self) -> None: ...
    def add_state(self, state, overwrite) -> None: ...
    def invoke(self, context, path) -> None: ...
    @classmethod
    def for_context(cls, context, path, only_load_props): ...
    @classmethod
    def path_exists(cls, context, path, key): ...
    @classmethod
    def callable_for_path(cls, context, path, limit_to_mapper, token, loader_callable, *arg, **kw) -> None: ...

def load_scalar_attributes(mapper, state, attribute_names, passive) -> None: ...
