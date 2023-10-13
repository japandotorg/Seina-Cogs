"""
MIT License

Copyright (c) 2021-present Kuro-Rui

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

from typing import List, Literal

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list

from .abc import MixinMeta


class Commands(MixinMeta):
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_threads=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.group(name="threadopener", aliases=["to"])  # type: ignore
    async def _thread_opener(self, _: commands.Context):
        """Manage ThreadOpener settings."""

    @_thread_opener.command(name="toggle")  # type: ignore
    async def _toggle(self, ctx: commands.Context, toggle: bool):
        """
        Toggle ThreadOpener enable or disable.
        """
        if "THREADS_ENABLED" not in ctx.guild.features:  # type: ignore
            await ctx.send("Threads are not enabled in this server.")
            return
        await self.config.guild(ctx.guild).toggle.set(toggle)  # type: ignore
        await ctx.send(f"Thread opener is now {'enabled' if toggle else 'disabled'}.")

    @_thread_opener.command(name="channels", aliases=["channel"])  # type: ignore
    async def _channels(
        self,
        ctx: commands.Context,
        add_or_remove: Literal["add", "remove"],
        channels: commands.Greedy[discord.TextChannel],  # type: ignore
    ):
        """
        Add or remove channels for your guild.

        - `<add_or_remove>` should be either `add` to add channels or `remove` to remove channels.

        **Example:**
        - `[p]threadopener channels add #channel`
        - `[p]threadopener channels remove #channel`

        **Note:**
        - You can add or remove multiple channels at once.
        - You can also use channel ID instead of mentioning the channel.
        """
        async with self.config.guild(ctx.guild).channels() as c:  # type: ignore
            for channel in channels:
                if add_or_remove.lower() == "add":
                    if not channel.id in c:
                        c.append(channel.id)
                elif add_or_remove.lower() == "remove":
                    if channel.id in c:
                        c.remove(channel.id)

        channels = len(channels)  # type: ignore

        await ctx.send(
            f"{'added' if add_or_remove.lower() == 'add' else 'removed'} "
            "{channels} {'channel' if channels == 1 else 'channels'}."
        )

    @_thread_opener.command(name="archive")  # type: ignore
    async def _archive(self, ctx: commands.Context, amount: Literal[0, 60, 1440, 4320, 10080]):
        """
        Change the archive duration of threads.

        - Use `0` to disable auto archive duration of threads.
        """
        if amount == 0:
            await self.config.guild(ctx.guild).auto_archive_duration.clear()  # type: ignore
            await ctx.send("Disabled auto archive duration.")
            return
        await self.config.guild(ctx.guild).auto_archive_duration.set(amount)  # type: ignore
        await ctx.send(f"Auto archive duration is now {amount}.")

    @_thread_opener.command()  # type: ignore
    async def _slowmode(self, ctx: commands.Context, amount: commands.Range[int, 0, 21600]):
        """
        Change the slowmode of threads.

        - Use `0` to dsiable slowmode delay in threads.
        """
        if amount == 0:
            await self.config.guild(ctx.guild).slowmode_delay.clear()  # type: ignore
            await ctx.send("Disabled slowmode on opening threads.")
        await self.config.guild(ctx.guild).slowmode_delay.set(amount)  # type: ignore
        await ctx.send(f"Slowmode is now {amount}.")

    @_thread_opener.command()  # type: ignore
    async def _show_settings(self, ctx: commands.Context):
        """Show ThreadOpener settings."""
        data = await self.config.guild(ctx.guild).all()  # type: ignore
        toggle = data["toggle"]
        channels = data["channels"]
        active_channels: List[str] = []
        for channel in channels:
            channel = ctx.guild.get_channel(channel)  # type: ignore
            active_channels.append(channel.mention)  # type: ignore
        embed: discord.Embed = discord.Embed(
            title="ThreadOpener Settings",
            description=f"ThreadOpener is currently **{'enabled' if toggle else 'disabled'}**.",
            color=await ctx.embed_color(),
        )
        embed.add_field(
            name="Auto Archive Duration",
            value=data["auto_archive_duration"],
            inline=False,
        )
        embed.add_field(name="Slowmode Delay", value=data["slowmode_delay"], inline=False)
        if active_channels:
            embed.add_field(
                name="Active Channels",
                value=humanize_list(active_channels),
                inline=False,
            )
        await ctx.send(embed=embed)
