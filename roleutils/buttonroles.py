"""
MIT License

Copyright (c) 2020-2023 PhenoM4n4n
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

import asyncio
import discord
import logging
from typing import Any, Dict, Optional
from discord import ui, ButtonStyle

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils import menus
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.chat_formatting import pagify

from .abc import MixinMeta, CompositeMetaClass
from .converters import EmojiRole

log = logging.getLogger("red.roleutils.buttonroles")


class RoleButton(
    ui.DynamicItem[ui.Button],
    template=r"br:(?P<guild_id>[0-9]+):(?P<message_id>[0-9]+):(?P<role_id>[0-9]+)",
):
    def __init__(self):
        super().__init__()

    def create_item(self, guild_id: str, message_id: str, role_id: str) -> ui.Button:
        return ui.Button(
            style=ButtonStyle.primary,
            emoji=self.emoji,
            custom_id=f"br:{guild_id}:{message_id}:{role_id}",
            label=None,
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = int(self.match["guild_id"])
        message_id = int(self.match["message_id"])
        role_id = int(self.match["role_id"])

        if (
            not interaction.guild
            or interaction.guild.id != guild_id
            or not isinstance(interaction.user, discord.Member)
        ):
            return await interaction.response.send_message(
                "This only works in servers.", ephemeral=True
            )

        role = interaction.guild.get_role(role_id)
        if role is None:
            return await interaction.response.send_message("Role no longer exists.", ephemeral=True)

        try:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"Removed {role.name} from you.", ephemeral=True
                )
            else:
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"Added {role.name} to you.", ephemeral=True
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to manage that role.", ephemeral=True
            )
        except discord.HTTPException:
            await interaction.response.send_message(
                "Something went wrong. Please try again later.", ephemeral=True
            )


class ButtonRoles(MixinMeta, metaclass=CompositeMetaClass):
    """Manage button-based role assignment."""

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.button_method: str = "build"
        self.active_button_roles = {}

    async def cog_load(self) -> None:
        """Start async task after Red is fully ready."""
        self.bot.add_dynamic_items(RoleButton())

    async def cog_unload(self) -> None:
        """Clean up tasks when cog unloads."""
        if self._task:
            self._task.cancel()

    async def _initialize_button_roles(self) -> None:
        """Background task to initialize button roles."""
        await self.bot.wait_until_red_ready()

    async def _add_buttons_to_message(
        self, message: discord.Message, bindings: Dict[str, int]
    ) -> None:
        if message.guild.id not in self.active_button_roles:
            self.active_button_roles[message.guild.id] = {}

        self.active_button_roles[message.guild.id][message.id] = {
            "channel": message.channel.id,
            "bindings": bindings,
        }

        view = discord.ui.View(timeout=None)
        for emoji, role_id in bindings.items():
            role = message.guild.get_role(role_id)
            if role:
                button = RoleButton().from_custom_id(
                    f"br:{message.guild.id}:{message.id}:{role_id}", emoji=emoji
                )
                view.add_item(button)

        try:
            await message.edit(view=view)
        except discord.HTTPException as e:
            log.debug(f"Failed to edit message {message.id}: {e}")

    @commands.has_guild_permissions(manage_roles=True)
    @commands.group()
    async def buttonrole(self, ctx: commands.Context):
        """Base command for Button Role management."""

    @commands.bot_has_guild_permissions(manage_roles=True)
    @buttonrole.command(name="bind")
    async def buttonrole_add(
        self,
        ctx: commands.Context,
        message: discord.Message,
        emoji: str,
        role: discord.Role,
    ):
        """Bind a button role to an emoji on a message."""
        emoji = str(emoji)

        if ctx.guild.id not in self.active_button_roles:
            self.active_button_roles[ctx.guild.id] = {}

        if message.id not in self.active_button_roles[ctx.guild.id]:
            self.active_button_roles[ctx.guild.id][message.id] = {
                "channel": message.channel.id,
                "bindings": {},
            }

        bindings = self.active_button_roles[ctx.guild.id][message.id]["bindings"]

        if emoji in bindings:
            old_role = ctx.guild.get_role(bindings[emoji])
            msg = await ctx.send(
                f"`{old_role}` is already binded to {emoji} on {message.jump_url}\n"
                "Would you like to override it?"
            )
            pred = MessagePredicate.yes_or_no(ctx)
            try:
                await self.bot.wait_for("message", check=pred, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send("Bind cancelled.")

            if not pred.result:
                return await ctx.send("Bind cancelled.")

        bindings[emoji] = role.id
        await self._add_buttons_to_message(message, bindings)
        await ctx.send(f"`{role}` has been binded to {emoji} on {message.jump_url}")

    @commands.bot_has_permissions(manage_roles=True, embed_links=True)
    @buttonrole.command(name="create")
    async def buttonrole_create(
        self,
        ctx: commands.Context,
        emoji_role_groups: commands.Greedy[EmojiRole],
        channel: Optional[discord.TextChannel] = None,
        color: Optional[discord.Color] = None,
        *,
        name: Optional[str] = None,
    ):
        """Create a button role."""
        if not emoji_role_groups:
            raise commands.BadArgument
        channel = channel or ctx.channel
        if not channel.permissions_for(ctx.me).send_messages:
            return await ctx.send(
                f"I do not have permission to send messages in {channel.mention}."
            )
        if color is None:
            color = await ctx.embed_color()
        if name is None:
            await ctx.send("What would you like the button role name to be?")
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=MessagePredicate.same_context(ctx=ctx),
                    timeout=60,
                )
            except asyncio.TimeoutError:
                return await ctx.send("Button Role creation cancelled.")
            name = msg.content

        description = f"Click the following buttons to receive the corresponding role:\n"
        for emoji, role in emoji_role_groups:
            description += f"{emoji}: {role.mention}\n"
        e = discord.Embed(title=name[:256], color=color, description=description)
        message = await channel.send(embed=e)

        duplicates = {}
        bindings = {}
        for emoji, role in emoji_role_groups:
            emoji_str = str(emoji)
            if emoji_str in bindings or role.id in bindings.values():
                duplicates[emoji] = role
            else:
                bindings[emoji_str] = role.id

        await self._add_buttons_to_message(message, bindings)

        if duplicates:
            dupes = "The following groups were duplicates and weren't added:\n"
            for emoji, role in duplicates.items():
                dupes += f"{emoji};{role}\n"
            await ctx.send(dupes)
        await ctx.tick()

    @buttonrole.group(name="delete", aliases=["remove"], invoke_without_command=True)
    async def buttonrole_delete(
        self,
        ctx: commands.Context,
        message: discord.Message,
    ):
        """Delete an entire button role for a message."""
        if (
            ctx.guild.id not in self.active_button_roles
            or message.id not in self.active_button_roles[ctx.guild.id]
        ):
            return await ctx.send("There are no button roles set up for that message.")

        msg = await ctx.send("Are you sure you want to remove all button roles for that message?")
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await self.bot.wait_for("message", check=pred, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Action cancelled.")

        if pred.result:
            del self.active_button_roles[ctx.guild.id][message.id]
            try:
                await message.edit(view=None)
            except discord.HTTPException:
                pass
            await ctx.send("Button roles cleared for that message.")
        else:
            await ctx.send("Action cancelled.")

    @buttonrole_delete.command(name="bind")
    async def delete_bind(
        self,
        ctx: commands.Context,
        message: discord.Message,
        emoji: str,
    ):
        """Delete an emoji-role bind for a button role."""
        emoji = str(emoji)
        if (
            ctx.guild.id not in self.active_button_roles
            or message.id not in self.active_button_roles[ctx.guild.id]
            or emoji not in self.active_button_roles[ctx.guild.id][message.id]["bindings"]
        ):
            return await ctx.send("That wasn't a valid emoji for that message.")

        del self.active_button_roles[ctx.guild.id][message.id]["bindings"][emoji]

        if not self.active_button_roles[ctx.guild.id][message.id]["bindings"]:
            del self.active_button_roles[ctx.guild.id][message.id]
            try:
                await message.edit(view=None)
            except discord.HTTPException:
                pass
        else:
            await self._add_buttons_to_message(
                message, self.active_button_roles[ctx.guild.id][message.id]["bindings"]
            )

        await ctx.send(f"That button role bind was deleted.")

    @buttonrole.command(name="list")
    async def button_list(self, ctx: commands.Context):
        """View the button roles on this server."""
        if (
            ctx.guild.id not in self.active_button_roles
            or not self.active_button_roles[ctx.guild.id]
        ):
            return await ctx.send("There are no button roles set up here!")

        guild: discord.Guild = ctx.guild
        button_roles = []
        for index, (message_id, message_data) in enumerate(
            self.active_button_roles[ctx.guild.id].items(), start=1
        ):
            channel: discord.TextChannel = guild.get_channel(message_data["channel"])
            if channel is None:
                continue

            if self.button_method == "fetch":
                try:
                    message: discord.Message = await channel.fetch_message(message_id)
                    link = message.jump_url
                except discord.NotFound:
                    continue
            elif self.button_method == "build":
                link = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message_id}"
            else:
                link = ""

            buttons = [f"[Button Role #{index}]({link})"]
            for emoji, role_id in message_data["bindings"].items():
                role = ctx.guild.get_role(role_id)
                if role:
                    buttons.append(f"{emoji}: {role.mention}")

            if len(buttons) > 1:
                button_roles.append("\n".join(buttons))
        if not button_roles:
            return await ctx.send("There are no button roles set up here!")

        color = await ctx.embed_color()
        description = "\n\n".join(button_roles)
        embeds = []
        pages = list(pagify(description, delims=["\n\n", "\n"]))
        base_embed = discord.Embed(color=color)
        base_embed.set_author(
            name="Button Roles",
            icon_url=getattr(ctx.guild.icon, "url", None),
        )
        for page in pages:
            e = base_embed.copy()
            e.description = page
            embeds.append(e)
        await menus.menu(ctx, embeds, menus.DEFAULT_CONTROLS)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if payload.guild_id is None:
            return

        if (
            payload.guild_id in self.active_button_roles
            and payload.message_id in self.active_button_roles[payload.guild_id]
        ):
            del self.active_button_roles[payload.guild_id][payload.message_id]

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
        if payload.guild_id is None:
            return

        if payload.guild_id in self.active_button_roles:
            for message_id in payload.message_ids:
                if message_id in self.active_button_roles[payload.guild_id]:
                    del self.active_button_roles[payload.guild_id][message_id]
