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
from redbot.core.utils.chat_formatting import box, humanize_list

from ._tagscript import TagscriptConverter
from .abc import MixinMeta


class Commands(MixinMeta):
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.group(name="threadopener", aliases=["to"])  # type: ignore
    @commands.bot_has_permissions(manage_threads=True, create_public_threads=True)
    async def _thread_opener(self, _: commands.Context):
        """Manage ThreadOpener settings."""

    @_thread_opener.command(name="toggle")  # type: ignore
    async def _toggle(self, ctx: commands.Context, toggle: bool):
        """
        Toggle ThreadOpener enable or disable.
        """
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
            f"{'Added' if add_or_remove.lower() == 'add' else 'Removed'} "
            f"{channels} {'channel' if channels == 1 else 'channels'}."
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

    @_thread_opener.command(name="slowmode", aliases=["slow"])  # type: ignore
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

    @_thread_opener.group(name="message")  # type: ignore
    async def _message(self, _: commands.Context):
        """
        Manage thread opener notifications when they are opened.
        """

    @_message.command(name="toggle")
    async def _message_toggle(self, ctx: commands.Context, toggle: bool):
        """Toggle the thread opener notification message."""
        await self.config.guild(ctx.guild).message_toggle.set(toggle)  # type: ignore
        await ctx.send(
            f"ThreadOpener notifications are now {'enabled' if toggle else 'disabled'}."
        )

    @_message.command(name="set")
    async def _message_set(self, ctx: commands.Context, *, message: TagscriptConverter):
        """
        Change the thread opener notification message.

        (Supports Tagscript)

        **Blocks:**
        - [Assugnment Block](https://phen-cogs.readthedocs.io/en/latest/tags/tse_blocks.html#assignment-block)
        - [If Block](https://phen-cogs.readthedocs.io/en/latest/tags/tse_blocks.html#if-block)
        - [Embed Block](https://phen-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#embed-block)
        - [Command Block](https://phen-cogs.readthedocs.io/en/latest/tags/parsing_blocks.html#command-block)

        **Variable:**
        - `{server}`: [Your guild/server.](https://phen-cogs.readthedocs.io/en/latest/tags/default_variables.html#server-block)
        - `{author}`: [Author of the message.](https://phen-cogs.readthedocs.io/en/latest/tags/default_variables.html#author-block)
        - `{color}`: [botname]'s default color.

        **Example:**
        ```
        {embed(description):Welcome to the thread.}
        {embed(thumbnail):{member(avatar)}}
        {embed(color):{color}}
        ```
        """
        if message:
            await self.config.member(ctx.author).custom_message.set(message)  # type: ignore
            await ctx.send("Successfully changed the thread opener notification message.")
        else:
            await self.config.member(ctx.author).custom_message.clear()  # type: ignore
            await ctx.send("Successfully reset the thread opener notification message.")

    @_thread_opener.command(name="showsettings", aliases=["ss", "show"])  # type: ignore
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
        )
        embed.add_field(
            name=f"Message Toggle: {data['message_toggle']}",
            value=box(str(data["message"]), lang="json"),
            inline=False,
        )
        embed.add_field(name="Slowmode Delay", value=data["slowmode_delay"])
        if active_channels:
            embed.add_field(
                name="Active Channels",
                value=humanize_list(active_channels)[:2000],
                inline=False,
            )
        await ctx.send(embed=embed)