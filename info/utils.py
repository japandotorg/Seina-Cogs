from typing import Dict, Final, List, Optional

import discord
from redbot.core import app_commands
from redbot.core.bot import Red

MELON: Final[int] = 808706062013825036  # MELON's ID (i'm lazy)
MELON_BADGES: Dict[str, Dict[str, int]] = {  # MELON specific badges (i'm lazy)
    "926230917641560114": {  # Melon's Lounge
        "926231002752356372": 945342314497335356,  # Development
        "954636730110210048": 947520903850385428,  # Admin
        "954637490797563944": 946348330332618822,  # Staff
        "954636892496879626": 1001563639838408835,  # Bot moderator
        "954637406513008660": 947520442804088872,  # Bot Support
        "989560884374421526": 1087718941373243483,  # Patreon
        "1006288816862150847": 1087089040429416488,  # Bug hunter tier 1
        "1087098525826953306": 1087089088538103918,  # Bug hunter tier 2
        "1087098639509364807": 1087089200253386802,  # Bug hunter tier 3
        "1087098716323844116": 1087089349767733278,  # Bug hunter tier 4
        "1087098793914277909": 1087089466713309254,  # Bug Hunter tier 5
        "1123586317503168634": 1123609477552287837,  # Cog Contributors
    },
    "133049272517001216": {  # Red
        "739263148024004749": 594238096934043658,  # Org Member
        # 346744009458450433: 245684056744787968,  # Contributor
    },
}


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
