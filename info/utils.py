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
