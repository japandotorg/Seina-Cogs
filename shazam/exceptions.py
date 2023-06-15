from __future__ import annotations

from typing import Any, Optional

from redbot.core import commands


class CommandWarning(commands.CommandError):
    def __init__(self, message: Optional[str] = None, **kwargs: Any):
        super().__init__(message)
        self.kwargs: Any = kwargs
