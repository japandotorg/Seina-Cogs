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

def track_cascade_events(descriptor, prop): ...

class UOWTransaction:
    session: Any
    attributes: Any
    deps: Any
    mappers: Any
    presort_actions: Any
    postsort_actions: Any
    dependencies: Any
    states: Any
    post_update_states: Any
    def __init__(self, session): ...
    @property
    def has_work(self): ...
    def was_already_deleted(self, state): ...
    def is_deleted(self, state): ...
    def memo(self, key, callable_): ...
    def remove_state_actions(self, state) -> None: ...
    def get_attribute_history(self, state, key, passive=...): ...
    def has_dep(self, processor): ...
    def register_preprocessor(self, processor, fromparent) -> None: ...
    def register_object(
        self,
        state,
        isdelete: bool = ...,
        listonly: bool = ...,
        cancel_delete: bool = ...,
        operation: Any | None = ...,
        prop: Any | None = ...,
    ): ...
    def register_post_update(self, state, post_update_cols) -> None: ...
    def filter_states_for_dep(self, dep, states): ...
    def states_for_mapper_hierarchy(self, mapper, isdelete, listonly) -> None: ...
    def execute(self): ...
    def finalize_flush_changes(self) -> None: ...

class IterateMappersMixin: ...

class Preprocess(IterateMappersMixin):
    dependency_processor: Any
    fromparent: Any
    processed: Any
    setup_flush_actions: bool
    def __init__(self, dependency_processor, fromparent) -> None: ...
    def execute(self, uow): ...

class PostSortRec:
    disabled: Any
    def __new__(cls, uow, *args): ...
    def execute_aggregate(self, uow, recs) -> None: ...

class ProcessAll(IterateMappersMixin, PostSortRec):
    dependency_processor: Any
    sort_key: Any
    isdelete: Any
    fromparent: Any
    def __init__(self, uow, dependency_processor, isdelete, fromparent) -> None: ...
    def execute(self, uow) -> None: ...
    def per_state_flush_actions(self, uow): ...

class PostUpdateAll(PostSortRec):
    mapper: Any
    isdelete: Any
    sort_key: Any
    def __init__(self, uow, mapper, isdelete) -> None: ...
    def execute(self, uow) -> None: ...

class SaveUpdateAll(PostSortRec):
    mapper: Any
    sort_key: Any
    def __init__(self, uow, mapper) -> None: ...
    def execute(self, uow) -> None: ...
    def per_state_flush_actions(self, uow) -> None: ...

class DeleteAll(PostSortRec):
    mapper: Any
    sort_key: Any
    def __init__(self, uow, mapper) -> None: ...
    def execute(self, uow) -> None: ...
    def per_state_flush_actions(self, uow) -> None: ...

class ProcessState(PostSortRec):
    dependency_processor: Any
    sort_key: Any
    isdelete: Any
    state: Any
    def __init__(self, uow, dependency_processor, isdelete, state) -> None: ...
    def execute_aggregate(self, uow, recs) -> None: ...

class SaveUpdateState(PostSortRec):
    state: Any
    mapper: Any
    sort_key: Any
    def __init__(self, uow, state) -> None: ...
    def execute_aggregate(self, uow, recs) -> None: ...

class DeleteState(PostSortRec):
    state: Any
    mapper: Any
    sort_key: Any
    def __init__(self, uow, state) -> None: ...
    def execute_aggregate(self, uow, recs) -> None: ...
