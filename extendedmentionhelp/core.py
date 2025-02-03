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

# The inspiration of this cog was taken from the now archived https://github.com/Obi-Wan3/OB13-Cogs/tree/main/mentionhelp

import random
import re
from datetime import timedelta
from typing import Any, Dict, Final, List, Optional, Tuple, Union, cast

import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config, Group
from redbot.core.utils.antispam import AntiSpam
from redbot.core.utils.chat_formatting import box, humanize_list

from ._tagscript import TagScriptConverter, message, process_tagscript


class ExtendedMentionHelp(commands.Cog):
    """
    Customizable Extended Mention Help.

    Set a custom message to be sent on bot mention.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.1"

    __intervals: Final[List[Tuple[timedelta, int]]] = [
        (timedelta(seconds=10), 2),
        (timedelta(minutes=1), 10),
        (timedelta(hours=1), 50),
        (timedelta(days=1), 250),
    ]

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, 69_420_666, force_registration=True)
        default_guild: Dict[str, bool] = {"toggle": True}
        default_global: Dict[str, Union[bool, str, Dict[str, bool]]] = {
            "toggle": True,
            "message": message,
            "antispam": {
                "toggle": True,
                "suppress": False,
            },
        }
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

        self.spam: Dict[int, AntiSpam] = {}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{humanize_list(self.__author__)}**",
        ]
        return "\n".join(text)

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        if await cast(Group, self.config.antispam).toggle():
            if message.author.id not in self.spam:
                self.spam[message.author.id] = AntiSpam(self.__intervals)
            if self.spam[message.author.id].spammy:
                if await cast(Group, self.config.antispam).suppress():
                    return
                raise commands.UserFeedbackCheckFailure(
                    "You're temporarily blocked from using the mention help trigger."
                )
        if message.author.bot or not await self.config.toggle():
            return
        if not await self.bot.allowed_by_whitelist_blacklist(message.author):
            return
        if (
            message.guild
            and not message.channel.permissions_for(message.guild.me).send_messages
            and (
                await self.bot.cog_disabled_in_guild(self, message.guild)
                or not await self.config.guild(message.guild).toggle()
            )
        ):
            return
        pattern: re.Pattern[str] = re.compile(
            rf"^<@!?{cast(discord.ClientUser, self.bot.user).id}>$"
        )
        if not pattern.match(message.content):
            return
        prefixes: List[str] = sorted(await self.bot.get_prefix(message), key=len)
        invite: str = await self.bot.get_invite_url()
        kwargs: Dict[str, Any] = await process_tagscript(
            await self.config.message(),
            {
                "random_prefix": tse.StringAdapter(random.choice(prefixes)),
                "prefix": tse.StringAdapter(prefixes[0]),
                "prefixes": tse.StringAdapter(humanize_list(prefixes)[:200]),
                "color": tse.StringAdapter(str(await self.bot.get_embed_color(message.channel))),
                "invite": tse.StringAdapter(invite),
            },
        )
        if not kwargs:
            await self.config.message.clear()
            kwargs: Dict[str, Any] = await process_tagscript(
                message,
                {
                    "random_prefix": tse.StringAdapter(random.choice(prefixes)),
                    "prefix": tse.StringAdapter(prefixes[0]),
                    "prefixes": tse.StringAdapter(humanize_list(prefixes)),
                    "color": tse.StringAdapter(
                        str(await self.bot.get_embed_color(message.channel))
                    ),
                    "invite": tse.StringAdapter(invite),
                },
            )
        if (
            kwargs.get("embed", None)
            and message.guild
            and not message.channel.permissions_for(message.guild.me).embed_links
        ):
            return
        kwargs["reference"] = message.to_reference(fail_if_not_exists=False)
        kwargs["allowed_mentions"] = discord.AllowedMentions(
            everyone=False, roles=False, users=False, replied_user=False
        )
        if await cast(Group, self.config.antispam).toggle():
            self.spam[message.author.id].stamp()
        await message.channel.send(**kwargs)

    @commands.group(name="mentionhelp", aliases=["extendedmentionhelp"])
    async def _mention_help(self, _: commands.Context):
        """Send a message when a user mentions the bot (with no other text)."""

    @commands.is_owner()
    @_mention_help.command(name="global")
    async def _mention_help_global(self, ctx: commands.Context, true_or_false: bool):
        """Toggle Extended Mention Help globally."""
        await self.config.toggle.set(true_or_false)
        await ctx.tick()

    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    @_mention_help.command(name="toggle", aliases=["server", "guild"])
    async def _mention_help_guild(self, ctx: commands.GuildContext, true_or_false: bool):
        """Toggle Extended Mention Help in this server."""
        await self.config.guild(ctx.guild).toggle.set(true_or_false)
        await ctx.tick()

    @commands.is_owner()
    @_mention_help.command(name="message")
    async def _message(
        self, ctx: commands.Context, *, message: Optional[TagScriptConverter] = None
    ):
        """
        Set the Extended Mention Help message.

        The Extended Mention Help message supports TagScript blocks which can
        customize the message and even add an embed!
        [View the TagScript documentation here.](https://cogs.melonbot.io/tags/)

        **Variables**:
        `{prefix}` - Shortest available prefix of [botname].
        `{prefixes}` - All avialable prefixes of [botname].
        `{random_prefix}` - Random configured prefix of [botname].
        `{color}` - [botname]'s default embed color.
        `{invite}` - Invite link for [botname]. Can be configured via `[p]inviteset`.

        **Blocks**:
        `embed` - [Embed to be sent for the Extended Mention Help message](https://cogs.melonbot.io/tags/parsings/#embed-block)

        **Examples:**
        > `[p]mentionhelp message My prefixes are {prefixes}!`
        > `[p]mentionhelp message {embed(description):My prefixes are {prefixes}!}`
        """
        if message is None:
            await self.config.message.clear()
            await ctx.send("Cleared the mention help message.")
            return
        await self.config.message.set(message)
        await ctx.send(
            "Changed the mentionhelp message:\n{}".format(box(str(message), lang="json")),
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.is_owner()
    @_mention_help.group(name="antispam")
    async def _mention_help_anti_spam(self, _: commands.Context):
        """Configure the anti spam module for Extended Mention Help."""

    @_mention_help_anti_spam.command(name="toggle")  # type: ignore
    async def _mention_help_anti_spam_toggle(self, ctx: commands.Context, true_or_false: bool):
        """Toggle the anti spam module for Extended Mention Help."""
        async with self.config.antispam() as antispam:
            antispam["toggle"] = true_or_false
        await ctx.tick()

    @_mention_help_anti_spam.command(name="suppress")  # type: ignore
    async def _mention_help_anti_spam_suppress(self, ctx: commands.Context, true_or_false: bool):
        """
        Toggle suppression of the error message raised when the anti spam module is
        triggered by the user due to spam.
        """
        async with self.config.antispam() as antispam:
            antispam["suppress"] = true_or_false
        await ctx.tick()

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @_mention_help.command(name="settings", aliases=["showsettings", "show", "ss"])
    async def _mention_help_settings(self, ctx: commands.Context):
        """
        View the Extended Mention Help Settings!
        """
        config: Dict[str, Union[bool, str, Dict[str, bool]]] = await self.config.all()
        antispam: Dict[str, bool] = cast(Dict[str, bool], config["antispam"])
        embed: discord.Embed = discord.Embed(
            title="Extended Mention Help Settings",
            color=await ctx.embed_color(),
            description=(
                "**Global Toggle**: {}\n"
                "**Anti Spam Toggle**: {}\n"
                "**Anti Spam Suppress**: {}\n"
            ).format(config["toggle"], antispam["toggle"], antispam["suppress"]),
        )
        embed.add_field(
            name="**Message**:",
            value=box(str(config["message"]), lang="json"),
            inline=False,
        )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
