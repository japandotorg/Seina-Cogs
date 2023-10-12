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

import logging
import contextlib
from typing import Dict, Final, List, Optional, Union

import discord
from discord.ext.commands._types import Check
from redbot.core import Config, app_commands, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .constants import Endpoints, Ratings
from .http import TruthOrDareAPIClient
from .views import CGView

log: logging.Logger = logging.getLogger("red.seina.conversationgames")


def is_restricted() -> Check[commands.Context]:
    async def _predicate(ctx: commands.Context) -> bool:
        rating = await ctx.cog.config.guild(ctx.guild).rating()  # type: ignore
        if rating.lower() in ["pg", "pg13"]:
            return True
        elif ctx.channel.is_nsfw():  # type: ignore
            return True
        return False

    return commands.check(_predicate)


class ConversationGames(commands.Cog):
    """Conversation games"""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.2.5"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, identifier=69420, force_registration=True)
        default_guild: Dict[str, Ratings] = {
            "rating": "pg",
        }
        self.config.register_guild(**default_guild)

        if 759180080328081450 in self.bot.owner_ids:  # type: ignore
            with contextlib.suppress(RuntimeError, ValueError):
                self.bot.add_dev_env_value(self.__class__.__name__.lower(), lambda _: self)

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

    async def _api(
        self, ctx: commands.Context, request: Endpoints, member: Optional[discord.Member] = None
    ) -> None:
        title = f"{ctx.author.name} asked {member.name}" if member is not None else None
        async with TruthOrDareAPIClient() as client, ctx.typing():
            rating: Ratings = await self._get_rating(ctx.guild)  # type: ignore
            result: Dict[str, Union[str, Dict[str, str]]] = await client._request(request, rating)
            embed: discord.Embed = discord.Embed(
                title=title,
                description=result["question"],
                color=await ctx.embed_color(),
            )
            embed.set_footer(text=f"Rating: {result['rating']} | ID: {result['id']}")
            _view: CGView = CGView(ctx, result, member)
            _out: discord.Message = await ctx.send(
                embed=embed,
                view=_view,
                allowed_mentions=discord.AllowedMentions(replied_user=False),
                reference=ctx.message.to_reference(fail_if_not_exists=False),
            )
            _view._message = _out

    @is_restricted()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @app_commands.default_permissions(use_application_commands=True)
    @commands.hybrid_command(name="wouldyourather", aliases=["wyr"])
    async def _wyr(self, ctx: commands.Context):
        """
        Would you rather?
        """
        await self._api(ctx, "wyr")

    @is_restricted()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @app_commands.default_permissions(use_application_commands=True)
    @commands.hybrid_command(name="neverhaveiever", aliases=["nhie"])
    async def _nhie(self, ctx: commands.Context):
        """
        Never have I ever.
        """
        await self._api(ctx, "nhie")

    @is_restricted()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @app_commands.default_permissions(use_application_commands=True)
    @commands.hybrid_command(name="paranoia")
    async def _paranoia(self, ctx: commands.Context):
        """
        Paranoia questions.
        """
        await self._api(ctx, "paranoia")

    @is_restricted()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @app_commands.default_permissions(use_application_commands=True)
    @app_commands.describe(member="The member you want to ask question.")
    @commands.hybrid_command(name="truth")
    async def _truth(self, ctx: commands.Context, *, member: Optional[discord.Member] = None):
        """
        Truth questions, optionally ask truth questions to members!
        """
        await self._api(ctx, "truth", member)

    @is_restricted()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.guild)
    @app_commands.default_permissions(use_application_commands=True)
    @commands.hybrid_command(name="dare")
    @app_commands.describe(member="The member you want to ask question.")
    async def _dare(self, ctx: commands.Context, *, member: Optional[discord.Member] = None):
        """
        Dare questions, optionally ask dare questions to members!
        """
        await self._api(ctx, "dare", member)

    @commands.guild_only()
    @commands.group(name="cgset")  # type: ignore
    @commands.admin_or_permissions(manage_guild=True)
    async def _cgset(self, _: commands.Context):
        """
        Configurating options for Conversation Games.
        """

    @_cgset.command(name="rating")
    async def _rating(self, ctx: commands.Context, rating: Ratings):
        """
        Set rating for the games.

        Converting to R-Rating will disallow the commands from working in
        non-nsfw channels.
        """
        await self.config.guild(ctx.guild).rating.set(rating.lower())  # type: ignore
        await ctx.send(
            f"Rating set to **{rating.upper()}**.",
            allowed_mentions=discord.AllowedMentions(replied_user=False),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
        )
