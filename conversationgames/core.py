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

# The idea of this cog is taken from https://github.com/Jintaku/Jintaku-Cogs-V3/tree/master/conversationgames

import io
import logging
from typing import Any, Dict, Final, List, Optional

import discord
from redbot.core import Config, app_commands, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .constants import Ratings, RequestType
from .http import TruthOrDareAPIClient
from .views import CGView

log: logging.Logger = logging.getLogger("red.seina.conversationgames")


class ConversationGames(commands.Cog):
    """Conversation games"""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.2.4"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, identifier=69420, force_registration=True)
        default_guild: Dict[str, Ratings] = {
            "rating": "pg",
        }
        self.config.register_guild(**default_guild)

    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, io.BytesIO]:
        """
        Nothing to delete.
        """
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, io.BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Any = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def _get_rating(self, guild: discord.Guild) -> Ratings:
        rating = await self.config.guild(guild).rating()
        return rating

    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(embed_links=True)
    @app_commands.default_permissions(use_application_commands=True)
    @commands.hybrid_command(name="wouldyourather", aliases=["wyr"])
    async def _wyr(self, ctx: commands.Context):
        """
        Would you rather?
        """
        async with TruthOrDareAPIClient() as client, ctx.typing():
            rating = await self._get_rating(ctx.guild)  # type: ignore
            result = await client._request("wyr", rating)
            embed: discord.Embed = discord.Embed(
                description=result["question"], color=await ctx.embed_color()
            )
            embed.set_footer(text=f"Rating: {result['rating']} | ID: {result['id']}")
        _view = CGView(ctx, result)
        _out = await ctx.send(
            embed=embed,
            view=_view,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
        _view._message = _out

    @commands.guild_only()
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(embed_links=True)
    @app_commands.default_permissions(use_application_commands=True)
    @commands.hybrid_command(name="neverhaveiever", aliases=["nhie"])
    async def _nhie(self, ctx: commands.Context):
        """
        Never have I ever.
        """
        async with TruthOrDareAPIClient() as client, ctx.typing():
            rating = await self._get_rating(ctx.guild)  # type: ignore
            result = await client._request("nhie", rating)
            embed: discord.Embed = discord.Embed(
                description=result["question"], color=await ctx.embed_color()
            )
            embed.set_footer(text=f"Rating: {result['rating']} | ID: {result['id']}")
        _view = CGView(ctx, result)
        _out = await ctx.send(
            embed=embed,
            view=_view,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
        _view._message = _out

    @commands.guild_only()
    @commands.hybrid_command(name="paranoia")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(embed_links=True)
    @app_commands.default_permissions(use_application_commands=True)
    async def _paranoia(self, ctx: commands.Context):
        """
        Paranoia questions.
        """
        async with TruthOrDareAPIClient() as client, ctx.typing():
            rating = await self._get_rating(ctx.guild)  # type: ignore
            result = await client._request("paranoia", rating)
            embed: discord.Embed = discord.Embed(
                description=result["question"], color=await ctx.embed_color()
            )
            embed.set_footer(text=f"Rating: {result['rating']} | ID: {result['id']}")
        _view = CGView(ctx, result)
        _out = await ctx.send(
            embed=embed,
            view=_view,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
        _view._message = _out

    @commands.guild_only()
    @commands.hybrid_command(name="truth")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(embed_links=True)
    @app_commands.default_permissions(use_application_commands=True)
    @app_commands.describe(member="The member you want to ask question.")
    async def _truth(self, ctx: commands.Context, *, member: Optional[discord.Member] = None):
        """
        Truth questions, optionally ask truth questions to members!
        """
        if member is None:
            title = None
        else:
            title = f"{ctx.author.name} asked {member.name}"
        async with TruthOrDareAPIClient() as client, ctx.typing():
            rating = await self._get_rating(ctx.guild)  # type: ignore
            result = await client._request("truth", rating)
            embed: discord.Embed = discord.Embed(
                title=title, description=result["question"], color=await ctx.embed_color()
            )
            embed.set_footer(text=f"Rating: {result['rating']} | ID: {result['id']}")
        _view = CGView(ctx, result)
        _out = await ctx.send(
            embed=embed,
            view=_view,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
        _view._message = _out

    @commands.guild_only()
    @commands.hybrid_command(name="dare")
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(embed_links=True)
    @app_commands.default_permissions(use_application_commands=True)
    @app_commands.describe(member="The member you want to ask question.")
    async def _dare(self, ctx: commands.Context, *, member: Optional[discord.Member] = None):
        """
        Dare questions, optionally ask dare questions to members!
        """
        if member is None:
            title = None
        else:
            title = f"{ctx.author.name} asked {member.name}"
        async with TruthOrDareAPIClient() as client, ctx.typing():
            rating = await self._get_rating(ctx.guild)  # type: ignore
            result = await client._request("dare", rating)
            embed: discord.Embed = discord.Embed(
                title=title, description=result["question"], color=await ctx.embed_color()
            )
            embed.set_footer(text=f"Rating: {result['rating']} | ID: {result['id']}")
        _view = CGView(ctx, result)
        _out = await ctx.send(
            embed=embed,
            view=_view,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
        _view._message = _out

    @commands.guild_only()
    @commands.group(name="cgset")  # type: ignore
    @commands.admin_or_permissions(manage_guild=True)
    async def _cgset(self, ctx: commands.Context):
        """
        Configurating options for Conversation Games.
        """

    @_cgset.command(name="rating")
    async def _rating(self, ctx: commands.Context, rating: Ratings):
        """
        Set rating for the games.
        """
        await self.config.guild(ctx.guild).rating.set(rating.lower())  # type: ignore
        await ctx.send(
            f"Rating set to **{rating.upper()}**.",
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
