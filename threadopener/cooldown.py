from typing import Dict, Optional, Callable, Any, final, Tuple, Union

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
