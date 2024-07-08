import logging
from typing import Dict, Final, List, Optional, Union, cast

import discord
from redbot.cogs.mod.mod import Mod
from redbot.core import Config, app_commands, commands
from redbot.core.bot import Red
from redbot.core.errors import CogLoadError
from redbot.core.utils.chat_formatting import humanize_list

from .abc import CompositeMetaClass
from .cache import Cache
from .settings import SettingsCommands
from .utils import guild_only_and_has_embed_links
from .views import UIView

log: logging.Logger = logging.getLogger("red.seina.info.core")

OLD_USERINFO_COMMAND = discord.utils.MISSING


class Info(commands.Cog, SettingsCommands, metaclass=CompositeMetaClass):
    """
    Custom info commands.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        _defaults: Dict[
            str,
            Dict[str, Union[Optional[int], Dict[str, Optional[int]], Dict[str, Dict[str, int]]]],
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
                "online": None,
                "away": None,
                "dnd": None,
                "offline": None,
                "streaming": None,
            },
            "badge": {
                "staff": None,
                "early_supporter": None,
                "verified_bot_developer": None,
                "active_developer": None,
                "bug_hunter": None,
                "bug_hunter_level_2": None,
                "partner": None,
                "verified_bot": None,
                "hypesquad": None,
                "hypesquad_balance": None,
                "hypesquad_bravery": None,
                "hypesquad_brilliance": None,
                "nitro": None,
                "discord_certified_moderator": None,
                "bot_http_interactions": None,
            },
            "settings": {
                "select": {
                    "roles": None,
                    "home": None,
                    "avatar": None,
                    "banner": None,
                    "gavatar": None,
                }
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
        self.bot.tree.remove_command("Get User's Info!", type=discord.AppCommandType.user)

    async def _callback(self, ctx: commands.GuildContext, member: discord.Member) -> None:
        await self.chunk(ctx.guild)
        async with ctx.typing():
            view: UIView = UIView(ctx, member, self.cache)
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

    async def _user_info_context(
        self, interaction: discord.Interaction[Red], member: discord.Member
    ):
        ctx: commands.Context = await commands.Context.from_interaction(interaction)
        await self._callback(ctx, member)


async def setup(bot: Red) -> None:
    if Mod.__name__ not in bot.cogs:
        raise CogLoadError("The Mod cog is required to be loaded to use this cog.")
    global OLD_USERINFO_COMMAND
    OLD_USERINFO_COMMAND = cast(commands.Command, bot.remove_command("userinfo"))
    await bot.add_cog(Info(bot))
