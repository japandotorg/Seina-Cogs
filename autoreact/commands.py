from typing import Dict, List, Literal, Optional

import discord
from redbot.core import commands

from .abc import CompositeMetaClass, MixinMeta
from .utils import (
    MAXIMUM_EVENT_REACTIONS,
    MAXIMUM_TRIGGER_LENGTH,
    MAXIMUM_TRIGGER_REACTIONS,
    EmojiConverter,
    paginate,
)


class Commands(MixinMeta, metaclass=CompositeMetaClass):
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.group(name="autoreact", aliases=["ar"])  # type: ignore
    async def _autoreact(self, _: commands.GuildContext):
        """Configure automatic reactions to messages that match a trigger."""

    @_autoreact.group(name="add", aliases=["+", "create"], invoke_without_command=True)  # type: ignore
    async def _autoreact_add(
        self, ctx: commands.GuildContext, trigger: str, reaction: EmojiConverter
    ):
        """Add a reaction to a trigger."""
        if reaction in self.cache.autoreact.get(ctx.guild.id, {}).get(trigger, []):
            await ctx.send("That is already a reaction for that trigger.")
            return
        if (
            len(self.cache.autoreact.get(ctx.guild.id, {}).get(trigger, []))
            > MAXIMUM_TRIGGER_REACTIONS
        ):
            await ctx.send("There are too many reactions for that trigger.")
            return
        if len(trigger) > MAXIMUM_TRIGGER_LENGTH:
            await ctx.send(
                "Please provide a valid trigger under {} characters".format(MAXIMUM_TRIGGER_LENGTH)
            )
            return
        reactions: Dict[str, List[str]] = await self.config.guild(ctx.guild).reaction()
        reactions[trigger].append(str(reaction))
        if ctx.guild.id not in self.cache.autoreact:
            self.cache.autoreact[ctx.guild.id] = {}
        if trigger not in self.cache.autoreact[ctx.guild.id]:
            self.cache.autoreact[ctx.guild.id][trigger] = []
        self.cache.autoreact[ctx.guild.id][trigger].append(str(reaction))
        await ctx.send("Successfully added {} as a reaction for `{}`".format(reaction, trigger))

    @_autoreact_add.command(name="images")  # type: ignore
    async def _autoreact_add_images(self, ctx: commands.GuildContext, reaction: EmojiConverter):
        """Add a reaction for images."""
        if reaction in self.cache.event.get(ctx.guild.id, {}).get("images", []):
            await ctx.send("That is already an auto reaction for images.")
            return
        if len(self.cache.event.get(ctx.guild.id, {}).get("images", [])) > MAXIMUM_EVENT_REACTIONS:
            await ctx.send("There are too many reactions for that trigger.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["images"].append(str(reaction))
        if ctx.guild.id not in self.cache.event:
            self.cache.event[ctx.guild.id] = {}
        if "images" not in self.cache.event[ctx.guild.id]:
            self.cache.event[ctx.guild.id]["images"] = []
        self.cache.event[ctx.guild.id]["images"].append(str(reaction))
        await ctx.send("Successfully added {} as a reaction for images.".format(reaction))

    @_autoreact_add.command(name="spoilers")  # type: ignore
    async def _autoreact_add_spoilers(self, ctx: commands.GuildContext, reaction: EmojiConverter):
        """Add a reaction for spoilers."""
        if reaction in self.cache.event.get(ctx.guild.id, {}).get("spoilers", []):
            await ctx.send("That is already an auto reaction for spoilers.")
            return
        if (
            len(self.cache.event.get(ctx.guild.id, {}).get("spoilers", []))
            > MAXIMUM_EVENT_REACTIONS
        ):
            await ctx.send("There are too many reactions for that trigger.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["spoilers"].append(str(reaction))
        if ctx.guild.id not in self.cache.event:
            self.cache.event[ctx.guild.id] = {}
        if "spoilers" not in self.cache.event[ctx.guild.id]:
            self.cache.event[ctx.guild.id]["spoilers"] = []
        self.cache.event[ctx.guild.id]["spoilers"].append(str(reaction))
        await ctx.send("Successfully added {} as a reaction for spoilers.".format(reaction))

    @_autoreact_add.command(name="emojis")  # type: ignore
    async def _autoreact_add_emojis(self, ctx: commands.GuildContext, reaction: EmojiConverter):
        """Add a reaction for emojis."""
        if reaction in self.cache.event.get(ctx.guild.id, {}).get("emojis", []):
            await ctx.send("That is already an auto reaction for emojis.")
            return
        if len(self.cache.event.get(ctx.guild.id, {}).get("emojis", [])) > MAXIMUM_EVENT_REACTIONS:
            await ctx.send("There are too many reactions for that trigger.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["emojis"].append(str(reaction))
        if ctx.guild.id not in self.cache.event:
            self.cache.event[ctx.guild.id] = {}
        if "emojis" not in self.cache.event[ctx.guild.id]:
            self.cache.event[ctx.guild.id]["emojis"].append(str(reaction))
        self.cache.event[ctx.guild.id]["emojis"].append(str(reaction))
        await ctx.send("Successfully added {} as a reaction for emojis.".format(reaction))

    @_autoreact_add.command(name="stickers")  # type: ignore
    async def _autoreact_add_stickers(self, ctx: commands.GuildContext, reaction: EmojiConverter):
        """Add a reaction for stickers."""
        if reaction in self.cache.event.get(ctx.guild.id, {}).get("stickers", []):
            await ctx.send("That is already an auto reaction for stickers.")
            return
        if (
            len(self.cache.event.get(ctx.guild.id, {}).get("stickers", []))
            > MAXIMUM_EVENT_REACTIONS
        ):
            await ctx.send("There are too many reactions for that trigger.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["stickers"].append(str(reaction))
        if ctx.guild.id not in self.cache.event:
            self.cache.event[ctx.guild.id] = {}
        if "stickers" not in self.cache.event[ctx.guild.id]:
            self.cache.event[ctx.guild.id]["stickers"].append(str(reaction))
        self.cache.event[ctx.guild.id]["stickers"].append(str(reaction))
        await ctx.send("Successfully added {} as a reaction for stickers.".format(reaction))

    @_autoreact.group(name="remove", aliases=["-", "delete"], invoke_without_command=True)  # type: ignore
    async def _autoreact_remove(
        self, ctx: commands.GuildContext, trigger: str, reaction: EmojiConverter
    ):
        """Remove a reaction from an auto reaction trigger."""
        if reaction not in self.cache.autoreact.get(ctx.guild.id, {}).get(trigger, []):
            await ctx.send("That auto reaction doesn't belong to that trigger.")
            return
        reactions: Dict[str, List[str]] = await self.config.guild(ctx.guild).reaction()
        reactions[trigger].remove(str(reaction))
        self.cache.autoreact[ctx.guild.id][trigger].remove(str(reaction))
        await ctx.send("Successfully removed that auto reaction.")

    @_autoreact_remove.command(name="images")  # type: ignore
    async def _autoreact_remove_images(self, ctx: commands.GuildContext, reaction: EmojiConverter):
        """Remove a reaction for images."""
        if reaction not in self.cache.event.get(ctx.guild.id, {}).get("images", []):
            await ctx.send("That auto reaction doesn't belong to images.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["images"].remove(str(reaction))
        self.cache.event[ctx.guild.id]["images"].remove(str(reaction))
        await ctx.send("Successfully removed that auto reaction.")

    @_autoreact_remove.command(name="spoilers")  # type: ignore
    async def _autoreact_remove_spoilers(
        self, ctx: commands.GuildContext, reaction: EmojiConverter
    ):
        """Remove a reaction for spoilers."""
        if reaction not in self.cache.event.get(ctx.guild.id, {}).get("spoilers", []):
            await ctx.send("That auto reaction doesn't belong to spoilers.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["spoilers"].remove(str(reaction))
        self.cache.event[ctx.guild.id]["spoilers"].remove(str(reaction))
        await ctx.send("Successfully removed that auto reaction.")

    @_autoreact_remove.command(name="emojis")  # type: ignore
    async def _autoreact_remove_emojis(self, ctx: commands.GuildContext, reaction: EmojiConverter):
        """Remove a reaction for emojis."""
        if reaction not in self.cache.event.get(ctx.guild.id, {}).get("emojis", []):
            await ctx.send("That auto reaction doesn't belong to emojis.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["emojis"].remove(str(reaction))
        self.cache.event[ctx.guild.id]["emojis"].remove(str(reaction))
        await ctx.send("Successfully removed that auto reaction.")

    @_autoreact_remove.command(name="stickers")  # type: ignore
    async def _autoreact_remove_stickers(
        self, ctx: commands.GuildContext, reaction: EmojiConverter
    ):
        """Remove a reaction for stickers."""
        if reaction not in self.cache.event.get(ctx.guild.id, {}).get("stickers", []):
            await ctx.send("That auto reaction doesn't belong to stickers.")
            return
        event: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
        event["stickers"].remove(str(reaction))
        self.cache.event[ctx.guild.id]["stickers"].remove(str(reaction))
        await ctx.send("Successfully removed that auto reaction.")

    @_autoreact.command(name="clear")  # type: ignore
    async def _autoreact_clear(
        self,
        ctx: commands.GuildContext,
        event: Optional[Literal["images", "spoilers", "emojis", "stickers"]] = None,
    ):
        """Clear every or specific event auto reaction trigger in this server."""
        if ctx.guild.id not in self.cache.autoreact and ctx.guild.id not in self.cache.event:
            await ctx.send("There aren't any auto-react triggers in this server.")
            return
        if event is not None:
            if event.lower() not in ("images", "spoilers", "emojis", "stickers"):
                await ctx.send("There isn't an type like that.")
                return
            if ctx.guild.id not in self.cache.event:
                await ctx.send("There aren't any auto reaction events in this server.")
                return
            if event.lower() not in self.cache.event[ctx.guild.id]:
                await ctx.send("There isn't an auto reaction event like that in this server.")
                return
            events: Dict[str, List[str]] = await self.config.guild(ctx.guild).event()
            del events[event.lower()]
            del self.cache.event[ctx.guild.id][event.lower()]
            await ctx.send("Successfully cleared every auto reaction for that event.")
            return
        if ctx.guild.id in self.cache.autoreact:
            await self.config.guild(ctx.guild).reaction.clear()
            del self.cache.autoreact[ctx.guild.id]
        if ctx.guild.id in self.cache.event:
            await self.config.guild(ctx.guild).event.clear()
            del self.cache.event[ctx.guild.id]
        await ctx.send("Successfully cleared every auto reaction trigger and events.")

    @_autoreact.command(name="reset")  # type: ignore
    async def _autoreact_reset(self, ctx: commands.GuildContext, trigger: str):
        """Clear every auto reaction from a trigger."""
        if trigger not in self.cache.autoreact.get(ctx.guild.id, {}):
            await ctx.send("There aren't any auto reactions for that trigger.")
            return
        reaction: Dict[str, List[str]] = await self.config.guild(ctx.guild).reaction()
        del reaction[trigger]
        del self.cache.autoreact[ctx.guild.id][trigger]
        await ctx.send("Successfully cleared every auto reaction for that trigger.")

    @_autoreact.command(name="list")  # type: ignore
    async def _autoreact_list(self, ctx: commands.GuildContext, events: bool = False):
        """View every auto reacton trigger."""
        if events:
            if not self.cache.event.get(ctx.guild.id, {}):
                await ctx.send("There aren't any event auto reactions in this server.")
                return
            rows, embed = [], discord.Embed(
                color=await ctx.embed_color(),
                title="Event Auto Reactions in **__{}__**".format(ctx.guild.name),
            )
            for event, reactions in self.cache.event.get(ctx.guild.id, {}).items():
                rows.append(f"{event}\n- **Reactions:** {', '.join(reactions)}")
            await paginate(ctx, (embed, rows))
            return
        if not self.cache.autoreact.get(ctx.guild.id, {}):
            await ctx.send("There aren't any auto reaction triggers in this server.")
            return
        rows, embed = [], discord.Embed(
            color=await ctx.embed_color(),
            title="Auto Reaction Triggers in **__{}__**".format(ctx.guild.name),
        )
        for keyword, reactions in self.cache.autoreact[ctx.guild.id].items():
            rows.append(f"{keyword}\n- **Reactions:** {', '.join(reactions)}")
        await paginate(ctx, (embed, rows), False)
