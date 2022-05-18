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

from ..util import memoized_property
from . import interfaces

class InstanceState(interfaces.InspectionAttrInfo):
    session_id: Any
    key: Any
    runid: Any
    load_options: Any
    load_path: Any
    insert_order: Any
    modified: bool
    expired: bool
    is_instance: bool
    identity_token: Any
    callables: Any
    class_: Any
    manager: Any
    committed_state: Any
    expired_attributes: Any
    def __init__(self, obj, manager) -> None: ...
    @memoized_property
    def attrs(self): ...
    @property
    def transient(self): ...
    @property
    def pending(self): ...
    @property
    def deleted(self): ...
    @property
    def was_deleted(self): ...
    @property
    def persistent(self): ...
    @property
    def detached(self): ...
    @property
    def session(self): ...
    @property
    def async_session(self): ...
    @property
    def object(self): ...
    @property
    def identity(self): ...
    @property
    def identity_key(self): ...
    @memoized_property
    def parents(self): ...
    @memoized_property
    def mapper(self): ...
    @property
    def has_identity(self): ...
    def obj(self) -> None: ...
    @property
    def dict(self): ...
    def get_history(self, key, passive): ...
    def get_impl(self, key): ...
    @property
    def unmodified(self): ...
    def unmodified_intersection(self, keys): ...
    @property
    def unloaded(self): ...
    @property
    def unloaded_expirable(self): ...

class AttributeState:
    state: Any
    key: Any
    def __init__(self, state, key) -> None: ...
    @property
    def loaded_value(self): ...
    @property
    def value(self): ...
    @property
    def history(self): ...
    def load_history(self): ...

class PendingCollection:
    deleted_items: Any
    added_items: Any
    def __init__(self) -> None: ...
    def append(self, value) -> None: ...
    def remove(self, value) -> None: ...
