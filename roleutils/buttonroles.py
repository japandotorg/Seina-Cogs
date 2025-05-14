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
from typing import Any, Dict, Optional, Union

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils import menus
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.chat_formatting import pagify

from .abc import MixinMeta, CompositeMetaClass
from .converters import EmojiRole

log = logging.getLogger("red.roleutils.buttonroles")


class ButtonRoles(MixinMeta, metaclass=CompositeMetaClass):
    """Manage button-based role assignment."""

    def __init__(self, *_args: Any) -> None:
        super().__init__(*_args)
        self.button_method: str = "build"
        self.cache["buttonroles"] = {"message_cache": set()}

        default_guild = {
            "buttonroles": {}
        }

    async def initialize(self) -> None:
        """Initialize button roles."""
        log.debug("ButtonRoles Initialize")
        self.create_task(self._load_existing_button_roles())
        await self._update_button_cache()
        await super().initialize()

    async def _initialize_button_roles(self) -> None:
        """Background task to initialize button roles."""
        try:
            await self.bot.wait_until_red_ready()
            await self._load_existing_button_roles()
        except Exception as e:
            log.exception("Failed to initialize button roles", exc_info=e)

    async def _update_button_cache(self) -> None:
        """Update the button roles message cache."""
        all_guilds = await self.config.all_guilds()
        for guild_id, guild_data in all_guilds.items():
            if "buttonroles" in guild_data:
                for message_id in guild_data["buttonroles"]:
                    self.cache["buttonroles"]["message_cache"].add(int(message_id))

    async def _load_existing_button_roles(self) -> None:
        """Load existing button roles from config."""
        all_guilds = await self.config.all_guilds()
        for guild in self.bot.guilds:
            guild_data = all_guilds.get(str(guild.id), {})
            if "buttonroles" not in guild_data:
                continue

            buttonroles = guild_data["buttonroles"]
            for message_id, data in buttonroles.items():
                channel = self.bot.get_channel(int(data["channel"]))
                if channel:
                    try:
                        message = await channel.fetch_message(int(message_id))
                        await self._add_buttons_to_message(message, data["bindings"])
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                        log.debug(f"Failed to load button roles for message {message_id}: {e}")
                        continue

    async def _add_buttons_to_message(self, message: discord.Message, bindings: Dict[str, int]) -> None:
        """Add buttons to a message based on bindings."""
        view = discord.ui.View(timeout=None)

        for emoji, role_id in bindings.items():
            role = message.guild.get_role(int(role_id))
            if role:
                button = discord.ui.Button(
                    label=None,
                    emoji=emoji,
                    custom_id=f"buttonrole_{message.guild.id}_{role.id}",
                    style=discord.ButtonStyle.primary
                )
                button.callback = self._create_button_callback(role)
                view.add_item(button)

        try:
            await message.edit(view=view)
        except discord.HTTPException as e:
            log.debug(f"Failed to edit message {message.id}: {e}")

    def _create_button_callback(self, role: discord.Role):
        """Create a callback for button interactions."""
        async def callback(interaction: discord.Interaction):
            if not interaction.guild or not isinstance(interaction.user, discord.Member):
                return await interaction.response.send_message(
                    "This only works in servers.", ephemeral=True
                )

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

        return callback

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
        async with self.config.guild(ctx.guild).buttonroles() as br:
            if str(message.id) not in br:
                br[str(message.id)] = {"channel": message.channel.id, "bindings": {}}
            
            old_role_id = br[str(message.id)]["bindings"].get(emoji)
            if old_role_id:
                old_role = ctx.guild.get_role(old_role_id)
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

            br[str(message.id)]["bindings"][emoji] = role.id
        
        await self._add_buttons_to_message(message, {emoji: role.id})
        await ctx.send(f"`{role}` has been binded to {emoji} on {message.jump_url}")
        self.cache["buttonroles"]["message_cache"].add(message.id)

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
        """Create a button role.

        Emoji and role groups should be seperated by a ';' and have no space.

        Example:
            - [p]buttonrole create 🎃;@SpookyRole 🅱️;MemeRole #role_channel Red
        """
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
        async with self.config.guild(ctx.guild).buttonroles() as br:
            br[str(message.id)] = {"channel": message.channel.id, "bindings": {}}
            for emoji, role in emoji_role_groups:
                emoji_str = str(emoji)
                if emoji_str in bindings or role.id in bindings.values():
                    duplicates[emoji] = role
                else:
                    bindings[emoji_str] = role.id
            br[str(message.id)]["bindings"] = bindings
        
        await self._add_buttons_to_message(message, bindings)
        
        if duplicates:
            dupes = "The following groups were duplicates and weren't added:\n"
            for emoji, role in duplicates.items():
                dupes += f"{emoji};{role}\n"
            await ctx.send(dupes)
        await ctx.tick()
        self.cache["buttonroles"]["message_cache"].add(message.id)

    @buttonrole.group(name="delete", aliases=["remove"], invoke_without_command=True)
    async def buttonrole_delete(
        self,
        ctx: commands.Context,
        message: discord.Message,
    ):
        """Delete an entire button role for a message."""
        message_data = await self.config.guild(ctx.guild).buttonroles.all()
        if str(message.id) not in message_data or not message_data[str(message.id)].get("bindings"):
            return await ctx.send("There are no button roles set up for that message.")

        msg = await ctx.send(
            "Are you sure you want to remove all button roles for that message?"
        )
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await self.bot.wait_for("message", check=pred, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Action cancelled.")

        if pred.result:
            async with self.config.guild(ctx.guild).buttonroles() as br:
                if str(message.id) in br:
                    del br[str(message.id)]
            try:
                await message.edit(view=None)
            except discord.HTTPException:
                pass
            await ctx.send("Button roles cleared for that message.")
            self.cache["buttonroles"]["message_cache"].discard(message.id)
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
        async with self.config.guild(ctx.guild).buttonroles() as br:
            if str(message.id) not in br or emoji not in br[str(message.id)]["bindings"]:
                return await ctx.send("That wasn't a valid emoji for that message.")
            
            del br[str(message.id)]["bindings"][emoji]
            if not br[str(message.id)]["bindings"]:
                del br[str(message.id)]
                try:
                    await message.edit(view=None)
                except discord.HTTPException:
                    pass
                self.cache["buttonroles"]["message_cache"].discard(message.id)
            else:
                await self._add_buttons_to_message(message, br[str(message.id)]["bindings"])
        
        await ctx.send(f"That button role bind was deleted.")

    @buttonrole.command(name="list")
    async def button_list(self, ctx: commands.Context):
        """View the button roles on this server."""
        data = await self.config.guild(ctx.guild).buttonroles.all()
        if not data:
            return await ctx.send("There are no button roles set up here!")

        guild: discord.Guild = ctx.guild
        to_delete_message_emoji_ids = {}
        button_roles = []
        for index, (message_id, message_data) in enumerate(data.items(), start=1):
            channel: discord.TextChannel = guild.get_channel(message_data["channel"])
            if channel is None:
                continue
            
            if self.button_method == "fetch":
                try:
                    message: discord.Message = await channel.fetch_message(int(message_id))
                    link = message.jump_url
                except discord.NotFound:
                    continue
            elif self.button_method == "build":
                link = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}/{message_id}"
            else:
                link = ""

            to_delete_emoji_ids = []

            buttons = [f"[Button Role #{index}]({link})"]
            for emoji, role_id in message_data["bindings"].items():
                role = ctx.guild.get_role(role_id)
                if role:
                    buttons.append(f"{emoji}: {role.mention}")
                else:
                    to_delete_emoji_ids.append(emoji)
            if to_delete_emoji_ids:
                to_delete_message_emoji_ids[message_id] = to_delete_emoji_ids
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

        if to_delete_message_emoji_ids:
            for message_id, emojis in to_delete_message_emoji_ids.items():
                async with self.config.guild(ctx.guild).buttonroles() as br:
                    if message_id in br:
                        for emoji in emojis:
                            if emoji in br[message_id]["bindings"]:
                                del br[message_id]["bindings"][emoji]
                        if not br[message_id]["bindings"]:
                            del br[message_id]
                            self.cache["buttonroles"]["message_cache"].discard(int(message_id))

    @commands.is_owner()
    @buttonrole.command(hidden=True)
    async def clear(self, ctx: commands.Context):
        """Clear all ButtonRole data."""
        msg = await ctx.send("Are you sure you want to clear all button role data?")
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await self.bot.wait_for("message", check=pred, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Action cancelled.")

        if pred.result:
            await self.config.guild(ctx.guild).buttonroles.clear()
            await ctx.send("Data cleared.")
            self.cache["buttonroles"]["message_cache"].clear()
        else:
            await ctx.send("Action cancelled.")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if payload.guild_id is None:
            return

        if payload.message_id not in self.cache["buttonroles"]["message_cache"]:
            return

        if await self.bot.cog_disabled_in_guild_raw(self.qualified_name, payload.guild_id):
            return

        async with self.config.guild_from_id(payload.guild_id).buttonroles() as br:
            if str(payload.message_id) in br:
                del br[str(payload.message_id)]
        self.cache["buttonroles"]["message_cache"].discard(payload.message_id)

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: discord.RawBulkMessageDeleteEvent):
        if payload.guild_id is None:
            return

        if await self.bot.cog_disabled_in_guild_raw(self.qualified_name, payload.guild_id):
            return

        async with self.config.guild_from_id(payload.guild_id).buttonroles() as br:
            for message_id in payload.message_ids:
                if message_id in self.cache["buttonroles"]["message_cache"]:
                    if str(message_id) in br:
                        del br[str(message_id)]
                    self.cache["buttonroles"]["message_cache"].discard(message_id)
