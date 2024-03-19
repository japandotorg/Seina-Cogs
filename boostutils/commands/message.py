from typing import Dict, List, Literal, Optional, Union

import discord
from redbot.core import commands
from redbot.core.utils.views import SimpleMenu
from redbot.core.utils.chat_formatting import box, humanize_list

from ..abc import MixinMeta, CompositeMetaClass
from .._tagscript import TagscriptConverter
from ..utils import group_embeds_by_fields


class MessageCommands(MixinMeta, metaclass=CompositeMetaClass):
    @commands.guild_only()
    @commands.group(name="boostmessage", aliases=["boostmsg", "bmsg"])  # type: ignore
    async def _message(self, _: commands.GuildContext):
        """Configuration commands for boost messages."""

    @_message.command(name="settings", aliases=["show", "showsettings", "ss"])
    async def _message_settings(self, ctx: commands.GuildContext):
        """See the boost messages settings configured for your server."""
        cutoff = lambda x: x if len(x) < 1024 else x[:1021] + "..."  # noqa: E731
        config: Dict[str, Union[bool, List[int], str]] = await self.config.guild(
            ctx.guild
        ).boost_message()
        channels: List[int] = config["channels"]  # type: ignore
        description: str = "**Enable:** {}\n\n".format(config["toggle"])
        embed: discord.Embed = discord.Embed(
            title="Boost Messages Settings for **__{}__**".format(ctx.guild.name),
            description=description,
            color=await ctx.embed_color(),
        )
        fields: List[Dict[str, Union[str, bool]]] = [
            dict(
                name="**Boost Message:**",
                value=box(cutoff(config["boosted"])),
                inline=False,
            ),
            dict(
                name="**Unboost Message:**",
                value=box(cutoff(config["unboosted"])),
                inline=False,
            ),
            dict(
                name="**Channels:**",
                value=(
                    humanize_list(
                        [
                            chan.mention
                            for channel in channels
                            if (chan := ctx.guild.get_channel(channel))
                        ]
                    )
                    if channels
                    else "No channels configured."
                ),
                inline=False,
            ),
        ]
        embeds: List[discord.Embed] = [
            embed,
            *await group_embeds_by_fields(
                *fields,
                per_embed=3,
                title="Boost Messages Settings for **__{}__**".format(ctx.guild.name),
                color=await ctx.embed_color(),
            ),
        ]
        await SimpleMenu(embeds).start(ctx)  # type: ignore

    @_message.command(name="toggle")
    @commands.admin_or_permissions(manage_guild=True)
    async def _message_toggle(
        self,
        ctx: commands.GuildContext,
        true_or_false: Optional[bool] = None,
    ):
        """
        Enable or disable boost messages.

        - Running the command with no arguments will disable the boost messages.
        """
        if true_or_false is None:
            await self.config.guild(ctx.guild).boost_message.toggle.clear()  # type: ignore
            await ctx.send(
                "Boost message is now untoggled.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await self.config.guild(ctx.guild).boost_message.toggle.set(true_or_false)  # type: ignore
        await ctx.send(
            f"Boost message is now {'toggle' if true_or_false else 'untoggled'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_message.command(name="channels")
    @commands.admin_or_permissions(manage_guild=True)
    async def _message_channels(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        channels: commands.Greedy[discord.TextChannel],
    ):
        """Add or remove the channels for boost messages."""
        async with self.config.guild(ctx.guild).boost_message.channels() as c:  # type: ignore
            for channel in channels:
                if add_or_remove.lower() == "add":
                    if channel.id not in c:
                        c.append(channel.id)
                elif add_or_remove.lower() == "remove":
                    if channel.id in c:
                        c.remove(channel.id)
        await ctx.send(
            f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {len(channels)} channels.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_message.group(name="message")
    @commands.admin_or_permissions(manage_guild=True)
    async def _message_message(self, _: commands.GuildContext):
        """Configure boost and unboost messages."""

    @_message_message.command(name="boosted", aliases=["boost"])
    async def _message_boosted(
        self, ctx: commands.GuildContext, *, message: Optional[TagscriptConverter] = None
    ):
        """
        Configure the boost message.

        - Running the command with no arguments will reset the boost message.
        """
        if message is None:
            await self.config.guild(ctx.guild).boost_message.boosted.clear()  # type: ignore
            await ctx.send(
                "Cleared the boosted message.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await self.config.guild(ctx.guild).boost_message.boosted.set(message)  # type: ignore
        await ctx.send(
            f"Changed the boosted message:\n{box(str(message), lang='json')}",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_message_message.command(name="unboosted", aliases=["unboost"])
    async def _message_unboosted(
        self, ctx: commands.GuildContext, *, message: Optional[TagscriptConverter] = None
    ):
        """
        Configure the unboost message.

        - Running the command with no arguments will reset the unboost message.
        """
        if message is None:
            await self.config.guild(ctx.guild).boost_message.unboosted.clear()  # type: ignore
            await ctx.send(
                "Cleared the unboosted message.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await self.config.guild(ctx.guild).boost_message.unboosted.set(message)  # type: ignore
        await ctx.send(
            f"Changed the unboosted message:\n{box(str(message), lang='json')}",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
