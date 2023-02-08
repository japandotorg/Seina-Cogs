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

from abc import abstractmethod
from typing import Callable, List, Optional, Type, TypeVar, Literal, Any, List

import redbot.core.commands as commands
from redbot.core.commands import Cog, Command

from .helper import CogABCMeta
from .utils import CogMixin

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

RTT = TypeVar("RTT", bound="RequestType")


class CogMixin(Cog, metaclass=CogABCMeta):
    
    @abstractmethod
    def setup_self(self: "CogMixin") -> None:
        ...

    @abstractmethod
    async def red_get_data_for_user(self: "CogMixin", *, user_id: int) -> Optional[str]:
        ...

    @abstractmethod
    async def red_delete_data_for_user(self: "CogMixin", *, requester: Type[RTT], user_id: int) -> None:
        ...

    def setup_mixins(self) -> None:
        for mixin in self.active_mixins:
            super(mixin, self).setup_self()  # noqa

    async def get_mixin_user_data(self, user_id: int) -> List[str]:
        ret = []
        for mixin in self.active_mixins:
            if text := await super(mixin, self).red_get_data_for_user(user_id=user_id):  # noqa
                ret.append(str(text))
        return ret

    async def delete_mixin_user_data(self, requester: Type[RTT], user_id: int) -> None:
        for mixin in self.active_mixins:
            await super(mixin, self).red_delete_data_for_user(
                requester=requester, user_id=user_id
            )  # noqa

    @property
    def active_mixins(self) -> List[Type["CogMixin"]]:
        return [
            class_
            for class_ in self.__class__.__mro__
            if issubclass(class_, CogMixin) and class_ != CogMixin
        ]


class MixinCommand:
    def __init__(self, function: Callable, parent: Optional[str] = None, **kwargs: Any) -> None:
        self.function: Callable = function
        self.parent: Optional[str] = parent
        self.kwargs: Any = kwargs

    def setup(self, cog: Cog, parent: Optional[Command] = None) -> None:
        parent = parent or self.parent or commands
        if isinstance(parent, str):
            parent = getattr(cog, parent)
        command = parent.command(**self.kwargs)(self.function)
        add_command_to_cog(command, cog)


class MixinGroup:
    def __init__(self, function: Callable, parent: Optional[str] = None, **kwargs: Any) -> None:
        self.function: Callable = function
        self.parent: Optional[str] = parent
        self.kwargs: Any = kwargs
        self.children: List = []

    def command(self, **kwargs: Any) -> Callable[[Callable], MixinCommand]:
        def _decorator(func: Callable) -> MixinCommand:
            child = MixinCommand(func, **kwargs)
            self.children.append(child)
            return child

        return _decorator

    def group(self, **kwargs: Any) -> Callable[[Callable], "MixinGroup"]:
        def _decorator(func: Callable) -> MixinGroup:
            child = MixinGroup(func, **kwargs)
            self.children.append(child)
            return child

        return _decorator

    def setup(self, cog: Cog, parent: Optional[Command] = None) -> None:
        parent = parent or self.parent or commands
        if isinstance(parent, str):
            parent = getattr(cog, parent)
        group = parent.group(**self.kwargs)(self.function)
        add_command_to_cog(group, cog)
        for child in self.children:
            child.setup(cog, group)


def add_command_to_cog(command: Command, cog: Cog) -> None:
    command.cog = cog
    cog.__cog_commands__ = (*cog.__cog_commands__, command)
    setattr(cog, command.callback.__name__, command)

    lookup = {cmd.qualified_name: cmd for cmd in cog.__cog_commands__}

    parent = command.parent
    if parent is not None:
        parent = lookup[parent.qualified_name]
        parent.remove_command(command.name)
        parent.add_command(command)


def mixin_command(parent: Optional[str], **kwargs: Any) -> Callable[[Callable], MixinCommand]:
    def _decorator(func: Callable) -> MixinCommand:
        return MixinCommand(func, parent, **kwargs)

    return _decorator


def mixin_group(parent: Optional[str], **kwargs: Any) -> Callable[[Callable], MixinGroup]:
    def _decorator(func: Callable) -> MixinGroup:
        return MixinGroup(func, parent, **kwargs)

    return _decorator
