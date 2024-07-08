from typing import Dict, List, Optional

import discord
from redbot.core import app_commands
from redbot.core.bot import Red


def guild_only_and_has_embed_links(interaction: discord.Interaction[Red]) -> bool:
    if not interaction.guild:
        raise app_commands.NoPrivateMessage()
    if not interaction.app_permissions.embed_links:
        raise app_commands.BotMissingPermissions(["embed_links"])
    if not interaction.user.guild_permissions.embed_links:  # type: ignore
        raise app_commands.MissingPermissions(["embed_links"])
    return True


def get_perms(perms: discord.Permissions) -> List[str]:
    if perms.administrator:
        return ["Administrator"]
    gp: Dict[str, bool] = dict(
        {x for x in perms if x[1] is True} - set(discord.Permissions(521942715969))
    )
    return [p.replace("_", " ").title() for p in gp]


def get_roles(member: discord.Member) -> Optional[List[str]]:
    roles: List[discord.Role] = list(reversed(member.roles))[:-1]
    if roles:
        return [x.mention for x in roles]
