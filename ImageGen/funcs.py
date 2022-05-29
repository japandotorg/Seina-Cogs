from typing import Any, Optional, Union

import discord
from discord import Embed, Member, User

__all__ = ["create_embed", "fix_url"]


def fix_url(url: Any):
    if not url:
        return None

    return str(url)


def create_embed(
    user: Optional[Union[Member, User]], *, image=None, thumbnail=None, **kwargs
) -> Embed:
    """
    Makes a discord.Embed with options for image and thumbnail URLs, and adds a footer with author name
    """

    kwargs["color"] = kwargs.get("color", discord.Color.green())

    embed = discord.Embed(**kwargs)
    embed.set_image(url=fix_url(image))
    embed.set_thumbnail(url=fix_url(thumbnail))

    if user:
        embed.set_footer(text=f"Command sent by {user}", icon_url=fix_url(user.display_avatar))

    return
