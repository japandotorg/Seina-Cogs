"""
MIT License

Copyright (c) 2024-present japandotorg

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

import logging
from collections.abc import Collection
from typing import Dict, Final, List, Optional, Union, cast

import discord
from redbot.core import Config, app_commands, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .abc import CompositeMetaClass
from .cache import Cache
from .settings import SettingsCommands
from .utils import SEINA, guild_only_and_has_embed_links
from .views import CommandView, UIView

log: logging.Logger = logging.getLogger("red.seina.info.core")

OLD_USERINFO_COMMAND = discord.utils.MISSING
OLD_CINFO_COMMAND = discord.utils.MISSING


class Info(commands.Cog, SettingsCommands, metaclass=CompositeMetaClass):
    """
    Custom info commands.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.2"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )

        seina: bool = (
            self.bot.owner_ids is not None
            and isinstance(self.bot.owner_ids, Collection)
            and SEINA in list(self.bot.owner_ids)
        )
        _defaults: Dict[
            str,
            Dict[
                str,
                Union[bool, Optional[int], Dict[str, Optional[int]], Dict[str, Dict[str, int]]],
            ],
        ] = {
            "special": {},
            "status": {
                "device": {
                    "mobile_online": None,
                    "mobile_idle": None,
                    "mobile_dnd": None,
                    "mobile_offline": None,
                    "web_online": None,
                    "web_idle": None,
                    "web_dnd": None,
                    "web_offline": None,
                    "desktop_online": None,
                    "desktop_idle": None,
                    "desktop_dnd": None,
                    "desktop_offline": None,
                },
                "online": 859980175588589587 if seina else None,
                "away": 859980300977045534 if seina else None,
                "dnd": 859980375882858516 if seina else None,
                "offline": 859981174007791616 if seina else None,
                "streaming": 933084283197870140 if seina else None,
            },
            "badge": {
                "staff": 934503593678094457 if seina else None,
                "early_supporter": 934504215500423209 if seina else None,
                "verified_bot_developer": 894188093647781958 if seina else None,
                "active_developer": 1101083614587912293 if seina else None,
                "bug_hunter": 872500602108788828 if seina else None,
                "bug_hunter_level_2": 872500552481792000 if seina else None,
                "partner": 934504341858029658 if seina else None,
                "verified_bot": 934504704619196456 if seina else None,
                "hypesquad": 934504003230892102 if seina else None,
                "hypesquad_balance": 934503920552800256 if seina else None,
                "hypesquad_bravery": 934503780031021076 if seina else None,
                "hypesquad_brilliance": 934503837841121320 if seina else None,
                "nitro": 263382460224634880 if seina else None,
                "discord_certified_moderator": (907486308006510673 if seina else None),
                "bot_http_interactions": 1135879666251595817 if seina else None,
            },
            "settings": {
                "select": {
                    "roles": 1261166986050932758 if seina else None,
                    "home": 1047886542376538143 if seina else None,
                    "avatar": 934507937228017745 if seina else None,
                    "banner": 934508352971603998 if seina else None,
                    "gavatar": 1261167779957047337 if seina else None,
                    "perms": 934503593678094457 if seina else None,
                },
                "downloader": False,
            },
        }
        self.config.register_global(**_defaults)

        self.cache: Cache = Cache(self)

        self.user_info_context: app_commands.ContextMenu = app_commands.ContextMenu(
            name="Get User's Info!", callback=self._user_info_context
        )
        self.user_info_context.add_check(guild_only_and_has_embed_links)
        self.bot.tree.add_command(self.user_info_context)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    async def chunk(self, guild: discord.Guild) -> None:
        if guild.chunked is False and self.bot.intents.members:
            await guild.chunk(cache=True)

    async def cog_unload(self) -> None:
        global OLD_USERINFO_COMMAND
        if OLD_USERINFO_COMMAND is not discord.utils.MISSING:
            try:
                self.bot.remove_command("userinfo")
            except Exception as error:
                log.exception(
                    "Something went wrong removing the `userinfo` command.", exc_info=error
                )
            self.bot.add_command(OLD_USERINFO_COMMAND)
        if (command := OLD_CINFO_COMMAND) is not discord.utils.MISSING:
            if not ("cinfo" in (aliases := list(command.aliases)) and "cinfo" == command.name):
                aliases.append("cinfo")
        self.bot.tree.remove_command("Get User's Info!", type=discord.AppCommandType.user)

    async def _callback(self, ctx: commands.GuildContext, member: discord.Member) -> None:
        await self.chunk(ctx.guild)
        async with ctx.typing():
            fetched: discord.User = await self.bot.fetch_user(member.id)
            view: UIView = UIView(ctx, member, self.cache, (fetched.banner, member.guild_avatar))
            embed: discord.Embed = await view._make_embed()
        _out: discord.Message = await ctx.send(
            embed=embed,
            view=view,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
        view._message = _out

    @commands.guild_only()
    @commands.has_permissions(embed_links=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="userinfo", aliases=["ui"])
    async def _user_info(
        self, ctx: commands.GuildContext, *, member: Optional[discord.Member] = None
    ):
        """Check user's info, defaults to author."""
        await self._callback(ctx, member if member else ctx.author)

    @commands.is_owner()
    @commands.has_permissions(embed_links=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="commandinfo", aliases=["cinfo"])
    async def _command_info(self, ctx: commands.Context, *, command: commands.CommandConverter):
        """
        View detailed information about a command.
        """
        async with ctx.typing():
            view: CommandView = CommandView(ctx, command)
            embeds: List[discord.Embed] = []
            embeds.append(await view._make_embed())
            if self.cache.get_downloader_info() and (embed := await view._get_downloader_info()):
                embeds.append(embed)
        _out: discord.Message = await ctx.send(
            embeds=embeds,
            view=view,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
        view._message = _out

    async def _user_info_context(
        self, interaction: discord.Interaction[Red], member: discord.Member
    ) -> None:
        ctx: commands.Context = await commands.Context.from_interaction(interaction)
        await self._callback(ctx, member)


async def setup(bot: Red) -> None:
    if userinfo := bot.get_command("userinfo"):
        global OLD_USERINFO_COMMAND
        OLD_USERINFO_COMMAND = cast(commands.Command, bot.remove_command(userinfo.qualified_name))
    if command := bot.get_command("cinfo"):
        global OLD_CINFO_COMMAND
        OLD_CINFO_COMMAND = cast(commands.Command, command)
        if "cinfo" in (aliases := list(command.aliases)):
            aliases.remove("cinfo")
        elif command.name == "cinfo":
            if "channelinfo" in (a := list(command.aliases)):
                a.remove("channelinfo")
            command.name = "channelinfo"
    await bot.add_cog(Info(bot))
