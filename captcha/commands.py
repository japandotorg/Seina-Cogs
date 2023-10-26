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

from typing import Any, Dict, Optional

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box
from redbot.core.utils.views import ConfirmView

from ._tagscript import TagscriptConverter
from .abc import CompositeMetaClass, MixinMeta


class CaptchaCommands(MixinMeta, metaclass=CompositeMetaClass):
    @commands.guild_only()
    @commands.group(name="captcha")  # type: ignore
    @commands.admin_or_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.guild)
    @commands.bot_has_permissions(kick_members=True, manage_roles=True)
    async def _captcha(self, _: commands.Context):
        """
        Manage Captcha settings.
        """

    @_captcha.command(name="toggle")
    async def _toggle(self, ctx: commands.Context, toggle: bool):
        """
        Toggle the captcha verification system.
        """
        await self.config.guild(ctx.guild).toggle.set(toggle)  # type: ignore
        await ctx.send(
            f"Captcha verification is now {'enabled' if toggle else 'disabled'}.",
        )

    @_captcha.command(name="channel")
    async def _channel(
        self, ctx: commands.Context, *, channel: Optional[discord.TextChannel] = None
    ):
        """
        Configure the captcha verification channel.

        **Note:**
        - Run the command without the channel argument to clear the config.
        """
        if channel is None:
            await self.config.guild(ctx.guild).channel.clear()  # type: ignore
            await ctx.send(f"Cleared the captcha verification channel.")
            return
        await self.config.guild(ctx.guild).channel.set(channel.id)  # type: ignore
        await ctx.send(
            f"Configured the captcha verification channel to {channel.name} ({channel.id})."
        )

    @_captcha.command(name="role")
    async def _role(self, ctx: commands.Context, *, role: Optional[discord.Role] = None):
        """
        Configure the role for captcha verification.

        **Note:**
        - Run the command without the role argument to clear the config.
        """
        if role is None:
            await self.config.guild(ctx.guild).role_after_captcha.clear()  # type: ignore
            await ctx.send(f"Cleared the captcha verification role.")
            return
        await self.config.guild(ctx.guild).role_after_captcha.set(role.id)  # type: ignore
        await ctx.send(
            f"Configured the captcha verification role to {role.name} ({role.id}).",
        )

    @_captcha.command(name="timeout")
    async def _timeout(self, ctx: commands.Context, amount: commands.Range[int, 50, 300]):
        """
        Configure the timeout for captcha verification. (Defaults to 120 seconds.)
        """
        await self.config.guild(ctx.guild).timeout.set(amount)  # type: ignore
        await ctx.send(
            f"Configured the timeout for captcha verification to {amount}.",
        )

    @_captcha.command(name="tries")
    async def _tries(self, ctx: commands.Context, amount: commands.Range[int, 2, 10]):
        """
        Configure the amount of tries needed for the captcha verification. (Defaults to 3 tries.)
        """
        await self.config.guild(ctx.guild).tries.set(amount)  # type: ignore
        await ctx.send(
            f"Configured the amount of tries needed for the captcha verification to {amount}."
        )

    @_captcha.group(name="message")
    async def _message(self, _: commands.Context):
        """
        Configure the after and before messages.
        """

    @_message.command(name="before")
    async def _before(
        self, ctx: commands.Context, *, message: Optional[TagscriptConverter] = None
    ):
        """
        Configure the before captcha message.
        """
        if message is None:
            await self.config.guild(ctx.guild).message_before_captcha.clear()  # type: ignore
            await ctx.send(f"Cleared the before captcha message.")
            return
        await self.config.guild(ctx.guild).message_before_captcha.set(message)  # type: ignore
        await ctx.send(f"Changed the before captcha message:\n{box(str(message), lang='json')}")

    @_message.command(name="after")
    async def _after(
        self,
        ctx: commands.Context,
        *,
        message: Optional[TagscriptConverter] = None,
    ):
        """
        Configure the after captcha message.
        """
        if message is None:
            await self.config.guild(ctx.guild).message_after_captcha.clear()  # type: ignore
            await ctx.send(f"Cleared the after captcha message.")
            return
        await self.config.guild(ctx.guild).message_after_captcha.set(message)  # type: ignore
        await ctx.send(f"Changed the after captcha message:\n{box(str(message), lang='json')}")

    @commands.bot_has_permissions(embed_links=True)
    @_captcha.command(name="settings", aliases=["showsettings", "show", "ss"])
    async def _settings(self, ctx: commands.Context):
        """
        View the captcha settings.
        """
        data: Dict[str, Any] = await self.config.guild(ctx.guild).all()  # type: ignore
        role = ctx.guild.get_role(data["role_after_captcha"])
        if role is None:
            role = "None"
        else:
            role = f"<@&{role.id}> ({role.id})"
        channel = ctx.guild.get_channel(data["channel"])
        if channel is None:
            channel = "None"
        else:
            channel = f"<#{channel.id}> ({channel.id})"
        embed: discord.Embed = discord.Embed(
            title="Captcha Settings",
            description=(
                f"**Toggle**: {data['toggle']}\n"
                f"**Channel**: {channel}\n"
                f"**Timeout**: {data['timeout']}\n"
                f"**Tries**: {data['tries']}\n"
                f"**Role**: {role}\n"
            ),
            color=await ctx.embed_color(),
        )
        embed.set_thumbnail(url=getattr(ctx.guild.icon, "url", ""))  # type: ignore
        embed.add_field(
            name="Before Captcha Message:",
            value=box(str(data["message_before_captcha"]), lang="json"),
            inline=False,
        )
        embed.add_field(
            name="After Captcha Message:",
            value=box(str(data["message_after_captcha"]), lang="json"),
            inline=False,
        )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_captcha.command(name="reset", aliases=["clear"])
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def _reset(self, ctx: commands.Context):
        """
        Reset all the captcha settings back to default.
        """
        if not await self.config.guild(ctx.guild).all():  # type: ignore
            return await ctx.send("There are no captcha settings to reset.")
        view = ConfirmView(ctx.author, disable_buttons=True)
        view.message = await ctx.send(
            "Are you sure you want to reset all the captcha settings back to default?", view=view
        )
        await view.wait()
        if view.result:
            await self.config.guild(ctx.guild).clear()
            await ctx.send("Successfully reset all the captcha settings back to default.")
        else:
            await ctx.send("Cancelled, i wont reset the captcha settings.")
