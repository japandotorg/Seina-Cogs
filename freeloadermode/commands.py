"""
MIT License

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

from datetime import timedelta, timezone, datetime
from typing import Literal, Optional, Union, Dict, Any

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box

from .converters import TimeConverter, BanLengthConverter, TagScriptConverter
from .abc import CompositeMetaClass, MixinMeta
from .utils import guild_roughly_chunked


class CommandsMixin(MixinMeta, metaclass=CompositeMetaClass):
    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.admin_or_permissions(manage_guild=True)
    @commands.group(name="freeloader", aliases=["fm", "freeloadermode"])  # type: ignore
    async def _freeloader(self, _: commands.GuildContext) -> None:
        """
        Configuration options for freeloader mode.
        """

    @_freeloader.command(name="on", aliases=["start"])  # type: ignore
    async def _on(self, ctx: commands.GuildContext, time: Optional[TimeConverter] = None):
        """
        Toggle freeloader mode with an optional time to untoggle.

        To use this command properly please make sure you have set the action and time length.
        """
        if guild_roughly_chunked(ctx.guild) is False and self.bot.intents.members:
            await ctx.guild.chunk(cache=True)

        toggled: bool = await self.config.guild(ctx.guild).toggled()
        if toggled:
            embed: discord.Embed = discord.Embed(
                description="You are already on freeloader mode.",
                color=await ctx.embed_color(),
            )
            await ctx.send(
                embed=embed,
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return

        await self.config.guild(ctx.guild).toggled.set(True)

        if not time:
            embed: discord.Embed = discord.Embed(
                title="Freeloader Mode Activated!",
                description=(
                    "You are now in freeloader mode. I will ban anyone "
                    "who leaves unless they are on the ignore list. I'll be watching for "
                    f"freeloaders until you've run the `{ctx.clean_prefix}freeloadermode off` command."
                ),
                timestamp=ctx.message.created_at.replace(tzinfo=timezone.utc),
                color=await ctx.embed_color(),
            )
            embed.set_author(name=ctx.guild.name, icon_url=getattr(ctx.guild.icon, "url", None))

            await ctx.send(embed=embed)
            return

        end_time: Union[float, timedelta] = datetime.utcnow().timestamp() + time  # type: ignore
        await self.config.guild(ctx.guild).untoggletime.set(end_time)
        end_time: Union[float, timedelta] = datetime.fromtimestamp(end_time) - datetime.utcnow()  # type: ignore

        embed: discord.Embed = discord.Embed(
            title="Freeloader Mode Activated!",
            description=(
                "You are now in freeloader mode. I will ban anyone "
                "who leaves unless they are on the ignore list.\n"
                f"Freeloader mode will get untoggled automatically in {end_time.total_seconds()} seconds."
            ),
            timestamp=datetime.utcnow(),
            color=await ctx.embed_color(),
        )
        embed.set_author(name=ctx.guild.name, icon_url=getattr(ctx.guild.icon, "url", None))

        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_freeloader.command(name="off", aliases=["end"])  # type: ignore
    async def _off(self, ctx: commands.GuildContext):
        """
        Toggle freeloader mode off.
        """
        toggled: bool = await self.config.guild(ctx.guild).toggled()
        if not toggled:
            embed: discord.Embed = discord.Embed(
                description="You are not on freeloader mode.",
                color=await ctx.embed_color(),
            )
            await ctx.send(
                embed=embed,
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await self.config.guild(ctx.guild).toggled.clear()
        await self.config.guild(ctx.guild).untoggletime.clear()
        embed: discord.Embed = discord.Embed(
            description="No longer in freeloader mode.",
            color=await ctx.embed_color(),
        )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_freeloader.command(name="action")  # type: ignore
    async def _action(self, ctx: commands.GuildContext, action: Literal["ban", "tempban"]):
        """
        Set the action to take upon freeloaders that leave the server.

        Actions can be one of:
        - Ban
        - Tempban
        """
        await self.config.guild(ctx.guild).action.set(action.lower())
        await ctx.send(
            f"Action set to `{action.lower()}`.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_freeloader.command(name="time", aliases=["length"])  # type: ignore
    async def _time(self, ctx: commands.GuildContext, time: BanLengthConverter):
        """
        Sets the time length of the tempban.

        `<time>` - The length of the ban. Must be entered as a valid integer and must be better 1 and 7 days.
        """
        await self.config.guild(ctx.guild).tempban_duration.set(time)
        await ctx.send(
            f"The tempban time length has been set to `{time}` days.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_freeloader.command(name="log", aliases=["logchannel"])  # type: ignore
    async def _log(
        self, ctx: commands.GuildContext, channel: Optional[discord.TextChannel] = None
    ):
        """
        Set the channel where freeloader stats are logged in.
        """
        await self.config.guild(ctx.guild).log_channel.set(getattr(channel, "id", None))
        await ctx.send(
            f"Log channel set to {channel.mention}." if channel else "Log channel cleared.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_freeloader.command(name="message")  # type: ignore
    async def _message(
        self, ctx: commands.GuildContext, *, message: Optional[TagScriptConverter] = None
    ):
        """"""
        if message:
            await self.config.guild(ctx.guild).message.set(message)
            await ctx.send(
                f"Successfully changed the freeloadermode dm message for this server.\n{box(str(message), lang='json')}",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
        else:
            await self.config.guild(ctx.guild).message.clear()
            await ctx.send(
                "Reset this server's ban message.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )

    @_freeloader.command(name="whitelist")  # type: ignore
    async def _whitelist(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        users: commands.Greedy[Union[discord.Member, discord.User]],
    ):
        """
        Adds or removes managers for your guild.

        `<add_or_remove>` should be either `add` to add users or `remove` to remove users.
        """
        async with self.config.guild(ctx.guild).ignored() as i:
            for user in users:
                if add_or_remove.lower() == "add":
                    if not user.id in i:
                        i.append(user.id)
                elif add_or_remove.lower() == "remove":
                    if user.id in i:
                        i.remove(user.id)

        await ctx.send(
            f"Successfully {'added' if add_or_remove.lower() == 'add' else 'removed'} {len(users)} roles.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_freeloader.command(name="settings", aliases=["showsettings", "show"])  # type: ignore
    async def _settings(self, ctx: commands.GuildContext):
        """
        Show the current settings for freeloader mode.
        """
        data: Dict[str, Any] = await self.config.guild(ctx.guild).all()
        embed: discord.Embed = discord.Embed(
            title="Freeloader Mode Settings",
            description=(
                f"Action: **{data['action']}**\n"
                f"Log Channel: **{data['log_channel']}**\n"
                f"Tempban Duration: **{data['tempban_duration']}**\n"
                f"Ban Message: {box(str(data['message']))}"
            ),
            color=await ctx.embed_color(),
        )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
