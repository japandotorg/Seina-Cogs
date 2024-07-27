import logging
from typing import cast

import discord
from redbot.core.bot import Red
from redbot.core.tree import RedTree
from redbot.core.utils.mod import get_audit_reason

log: logging.Logger = logging.getLogger("red.seina.threadopener.views")


class ThreadView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(ArchiveThreadButton())
        self.add_item(EditThreadTitleButton())
        self.add_item(DeleteThreadButton())

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if not cast(discord.Guild, interaction.guild).me.guild_permissions.manage_threads:
            await cast(RedTree, interaction.client.tree)._send_from_interaction(
                interaction, "I need the 'Manage Threads' permissions to do that!"
            )
            return False
        if not cast(discord.Member, interaction.user).guild_permissions.manage_threads:
            await cast(RedTree, interaction.client.tree)._send_from_interaction(
                interaction, "You're not authozied to use this button!"
            )
            return False
        return True


class EditTitleModal(discord.ui.Modal):
    name: discord.ui.TextInput = discord.ui.TextInput(
        label="Title",
        style=discord.TextStyle.short,
        placeholder="Your thread name.",
        min_length=1,
        max_length=30,
        required=True,
    )

    def __init__(self) -> None:
        super().__init__(title="Edit Thread Title", timeout=None)

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if not cast(discord.Guild, interaction.guild).me.guild_permissions.manage_threads:
            await cast(RedTree, interaction.client.tree)._send_from_interaction(
                interaction, "I need the 'Manage Threads' permissions to do that!"
            )
            return False
        if not cast(discord.Member, interaction.user).guild_permissions.manage_threads:
            await cast(RedTree, interaction.client.tree)._send_from_interaction(
                interaction, "You're not authozied to use this button!"
            )
            return False
        return True

    async def on_submit(self, interaction: discord.Interaction[Red]):
        channel: discord.Thread = cast(discord.Thread, interaction.channel)
        await channel.edit(name=self.name)
        await cast(RedTree, interaction.client.tree)._send_from_interaction(
            interaction, "Title updated to {}.".format(self.name)
        )


class EditThreadTitleButton(discord.ui.Button[ThreadView]):
    def __init__(self) -> None:
        super().__init__(
            label="Edit Title",
            style=discord.ButtonStyle.blurple,
            custom_id="threadopener:button:{}".format(self.__class__.__name__),
        )

    async def callback(self, interaction: discord.Interaction[Red]):
        modal: EditTitleModal = EditTitleModal()
        await interaction.response.send_modal(modal)


class ArchiveThreadButton(discord.ui.Button[ThreadView]):
    def __init__(self) -> None:
        super().__init__(
            label="Archive",
            style=discord.ButtonStyle.green,
            custom_id="threadopener:button:{}".format(self.__class__.__name__),
        )

    async def callback(self, interaction: discord.Interaction[Red]):
        channel: discord.Thread = cast(discord.Thread, interaction.channel)
        if channel.archived:
            await cast(RedTree, interaction.client.tree)._send_from_interaction(
                interaction, "Thread is already archived."
            )
            return
        await channel.edit(archived=True)
        await cast(RedTree, interaction.client.tree)._send_from_interaction(
            interaction, "Successfully archived the thread!"
        )


class DeleteThreadButton(discord.ui.Button[ThreadView]):
    def __init__(self) -> None:
        super().__init__(
            label="Delete",
            style=discord.ButtonStyle.red,
            custom_id="threadopener:button:{}".format(self.__class__.__name__),
        )

    async def callback(self, interaction: discord.Interaction[Red]):
        channel: discord.Thread = cast(discord.Thread, interaction.channel)
        reason: str = get_audit_reason(
            interaction.user,
            "[ThreadOpener] deleted the thread {0.name} ({0.id}).".format(channel),
        )
        await channel.delete(reason=reason)
