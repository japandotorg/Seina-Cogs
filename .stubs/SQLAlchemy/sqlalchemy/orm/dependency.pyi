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

class DependencyProcessor:
    prop: Any
    cascade: Any
    mapper: Any
    parent: Any
    secondary: Any
    direction: Any
    post_update: Any
    passive_deletes: Any
    passive_updates: Any
    enable_typechecks: Any
    sort_key: Any
    key: Any
    def __init__(self, prop) -> None: ...
    @classmethod
    def from_relationship(cls, prop): ...
    def hasparent(self, state): ...
    def per_property_preprocessors(self, uow) -> None: ...
    def per_property_flush_actions(self, uow) -> None: ...
    def per_state_flush_actions(self, uow, states, isdelete) -> None: ...
    def presort_deletes(self, uowcommit, states): ...
    def presort_saves(self, uowcommit, states): ...
    def process_deletes(self, uowcommit, states) -> None: ...
    def process_saves(self, uowcommit, states) -> None: ...
    def prop_has_changes(self, uowcommit, states, isdelete): ...

class OneToManyDP(DependencyProcessor):
    def per_property_dependencies(
        self,
        uow,
        parent_saves,
        child_saves,
        parent_deletes,
        child_deletes,
        after_save,
        before_delete,
    ) -> None: ...
    def per_state_dependencies(
        self,
        uow,
        save_parent,
        delete_parent,
        child_action,
        after_save,
        before_delete,
        isdelete,
        childisdelete,
    ) -> None: ...
    def presort_deletes(self, uowcommit, states) -> None: ...
    def presort_saves(self, uowcommit, states) -> None: ...
    def process_deletes(self, uowcommit, states) -> None: ...
    def process_saves(self, uowcommit, states) -> None: ...

class ManyToOneDP(DependencyProcessor):
    def __init__(self, prop) -> None: ...
    def per_property_dependencies(
        self,
        uow,
        parent_saves,
        child_saves,
        parent_deletes,
        child_deletes,
        after_save,
        before_delete,
    ) -> None: ...
    def per_state_dependencies(
        self,
        uow,
        save_parent,
        delete_parent,
        child_action,
        after_save,
        before_delete,
        isdelete,
        childisdelete,
    ) -> None: ...
    def presort_deletes(self, uowcommit, states) -> None: ...
    def presort_saves(self, uowcommit, states) -> None: ...
    def process_deletes(self, uowcommit, states) -> None: ...
    def process_saves(self, uowcommit, states) -> None: ...

class DetectKeySwitch(DependencyProcessor):
    def per_property_preprocessors(self, uow) -> None: ...
    def per_property_flush_actions(self, uow) -> None: ...
    def per_state_flush_actions(self, uow, states, isdelete) -> None: ...
    def presort_deletes(self, uowcommit, states) -> None: ...
    def presort_saves(self, uow, states) -> None: ...
    def prop_has_changes(self, uow, states, isdelete): ...
    def process_deletes(self, uowcommit, states) -> None: ...
    def process_saves(self, uowcommit, states) -> None: ...

class ManyToManyDP(DependencyProcessor):
    def per_property_dependencies(
        self,
        uow,
        parent_saves,
        child_saves,
        parent_deletes,
        child_deletes,
        after_save,
        before_delete,
    ) -> None: ...
    def per_state_dependencies(
        self,
        uow,
        save_parent,
        delete_parent,
        child_action,
        after_save,
        before_delete,
        isdelete,
        childisdelete,
    ) -> None: ...
    def presort_deletes(self, uowcommit, states) -> None: ...
    def presort_saves(self, uowcommit, states) -> None: ...
    def process_deletes(self, uowcommit, states) -> None: ...
    def process_saves(self, uowcommit, states) -> None: ...
