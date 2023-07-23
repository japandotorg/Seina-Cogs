from typing import Any, Optional

import discord
from redbot.core import commands

__all__ = ("_maybe_reply",)


async def _maybe_reply(
    ctx: commands.Context, content: Optional[str] = None, **kwargs: Any
) -> discord.Message:
    if ctx.interaction is None:
        try:
            return await ctx.send(content, reference=ctx.message, **kwargs)
        except:
            return await ctx.send(content, **kwargs)
    else:
        return await ctx.send(content, **kwargs)
