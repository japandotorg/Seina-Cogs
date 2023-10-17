"""
MIT License

Copyright (c) 2023-present japandotorg

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

from typing import Any, Callable, Dict, Optional, Tuple, Union, final

import discord
from redbot.core import commands


@final
class ThreadCooldown(commands.CooldownMapping[commands.Context]):
    def __init__(
        self,
        original: Optional[commands.Cooldown],
        type: Callable[[commands.Context], Any],
    ) -> None:
        super().__init__(original, type)
        self._cache: Dict[Any, commands.Cooldown] = {}
        self._cooldown: Optional[commands.Cooldown] = original
        self._type: Callable[[commands.Context], Any] = type

    def __call__(self) -> "ThreadCooldown":
        return self

    def get_bucket(
        self, message: discord.Message, current: Optional[float] = None
    ) -> Optional[commands.Cooldown]:
        return super().get_bucket(message, current)  # type: ignore

    def _bucket_key(self, tup: Tuple[int, Union[int, str]]) -> Tuple[int, Union[int, str]]:
        return tup

    def is_rate_limited(self, message: discord.Message) -> bool:
        bucket = self.get_bucket(message)
        return bucket.update_rate_limit() is not None  # type: ignore
