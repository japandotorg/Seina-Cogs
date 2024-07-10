import re
from typing import Any, Dict, List, Optional, Union, cast

import TagScriptEngine as tse

import discord
from redbot.core.bot import Red
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import humanize_list, box

from .views import URLButton
from ._tagscript import message, process_tagscript, TagScriptConverter


class MentionHelp(commands.Cog):
    """
    Customizable Mention Help

    Set a custom message to be sent on bot mention.
    """

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, 69_420_666, force_registration=True)
        default_guild: Dict[str, bool] = {"toggle": True}
        default_global: Dict[str, Union[bool, str, List[Dict[str, Union[str, bool, None]]]]] = {
            "toggle": True,
            "message": message,
            "buttons": [],
        }
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
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
        if not pattern.fullmatch(message.content.strip()) and cast(
            discord.ClientUser, self.bot.user
        ).id in [u.id for u in message.mentions]:
            return
        prefixes: List[str] = sorted(await self.bot.get_prefix(message), key=len)
        kwargs: Dict[str, Any] = await process_tagscript(
            await self.config.message(),
            {
                "prefix": tse.StringAdapter(prefixes[0]),
                "prefixes": tse.StringAdapter(humanize_list(prefixes)[:200]),
                "color": tse.StringAdapter(str(await self.bot.get_embed_color(message.channel))),
            },
        )
        if not kwargs:
            await self.config.message.clear()
            kwargs: Dict[str, Any] = await process_tagscript(
                message,
                {
                    "prefix": tse.StringAdapter(prefixes[0]),
                    "prefixes": tse.StringAdapter(humanize_list(prefixes)),
                    "color": tse.StringAdapter(
                        str(await self.bot.get_embed_color(message.channel))
                    ),
                },
            )
        if (
            kwargs["embed"]
            and message.guild
            and not message.channel.permissions_for(message.guild.me).embed_links
        ):
            return
        if buttons := cast(List[Dict[str, Union[str, bool, None]]], await self.config.buttons()):
            view: discord.ui.View = discord.ui.View(timeout=None)
            _kwargs: Dict[str, Union[str, bool, None]] = {}
            counter: int = 0
            for button in buttons:
                if counter >= 5:
                    break
                if (
                    not button.get("toggle", False)
                    or not button.get("name", None)
                    or not (url := button.get("url", None))
                ):
                    continue
                _kwargs["url"] = url
                _kwargs["label"] = button.get("label", None)
                _kwargs["emoji"] = button.get(
                    "emoji", button.get("emoji", "🔗") if _kwargs["label"] else None
                )
                view.add_item(URLButton(_kwargs))
                counter += 1
            kwargs["view"] = view
        kwargs["reference"] = message.to_reference(fail_if_not_exists=False)
        kwargs["allowed_mentions"] = discord.AllowedMentions(
            everyone=False, roles=False, users=[message.author.id], replied_user=False
        )
        await message.channel.send(**kwargs)

    @commands.group(name="mentionhelp")
    async def _mention_help(self, _: commands.Context):
        """Send a message when a user mentions the bot (with no other text)."""

    @commands.is_owner()
    @_mention_help.command(name="message")
    async def _message(
        self, ctx: commands.Context, *, message: Optional[TagScriptConverter] = None
    ):
        """Set the MentionHelp message."""
        if message is None:
            await self.config.message.clear()
            await ctx.send("Cleared the mention help message.")
            return
        await self.config.message.set(message)
        await ctx.send(
            "Changed the mentionhelp message:\n{}".format(box(str(message), lang="json"))
        )
