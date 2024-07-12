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

import contextlib
import datetime
import logging
from typing import Any, Dict, Final, List, Literal, Optional, Tuple, Union, cast

import discord
import TagScriptEngine as tse
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config, Group, Value
from redbot.core.utils.views import SimpleMenu
from redbot.core.utils.chat_formatting import box, pagify, humanize_list

from ._tagscript import (
    PollAdapter,
    PollAnswerAdapter,
    TagScriptConverter,
    _default_add,
    _default_remove,
    process_tagscript,
)
from .converters import OptionConverter, PollConverter, QuestionConverter
from .utils import ordinal
from .views import DisableOnTimeoutView, PollAnswerButton

log: logging.Logger = logging.getLogger("red.seina.discordpolls.core")


class DiscordPolls(commands.Cog):
    """Manage And Log Builtin Discord Polls."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        _default: Dict[str, Dict[str, Union[bool, Union[Optional[int], Dict[str, str]]]]] = dict(
            log=dict(
                toggle=False,
                channel=None,
                message=dict(
                    add=_default_add,
                    remove=_default_remove,
                ),
            )
        )
        self.config.register_guild(**_default)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def get_or_fetch_guild(self, id: int) -> discord.Guild:
        if (guild := self.bot.get_guild(id)) is not None:
            return guild
        return await self.bot.fetch_guild(id)

    async def get_or_fetch_guild_channel(
        self, guild: discord.Guild, id: int
    ) -> Union[discord.abc.GuildChannel, discord.Thread]:
        if (channel := guild.get_channel(id)) is not None:
            return channel
        return await guild.fetch_channel(id)

    async def _send_response(
        self,
        channel: discord.TextChannel,
        member: discord.Member,
        answer: discord.PollAnswer,
        **kwargs: Any,
    ) -> None:
        if not (
            (message := kwargs.get("message", None))
            and (default := kwargs.get("default", None))
            and (value := kwargs.get("value", None))
        ):
            raise commands.BadArgument("`message`, `default` and `value` are required kwargs.")
        voters: List[Union[discord.User, discord.Member]] = [
            voter async for voter in answer.voters()
        ]
        _kwargs: Dict[str, Any] = process_tagscript(
            message,
            dict(
                poll=PollAdapter(answer.poll),
                answer=PollAnswerAdapter(answer, voters),
                member=tse.MemberAdapter(member),
                color=tse.StringAdapter(await self.bot.get_embed_color(channel)),
                time=tse.IntAdapter(int(discord.utils.utcnow().timestamp())),
            ),
        )
        if not _kwargs:
            await cast(Value, value).clear()
            _kwargs: Dict[str, Any] = process_tagscript(
                default,
                dict(
                    poll=PollAdapter(answer.poll),
                    answer=PollAnswerAdapter(answer, voters),
                    member=tse.MemberAdapter(member),
                    color=tse.StringAdapter(await self.bot.get_embed_color(member)),
                    time=tse.IntAdapter(int(discord.utils.utcnow().timestamp())),
                ),
            )
        _kwargs["allowed_mentions"] = discord.AllowedMentions.none()
        try:
            await channel.send(**_kwargs)
        except (discord.Forbidden, discord.HTTPException) as error:
            log.debug("Unable to send polling logs.", exc_info=error)

    @commands.Cog.listener()
    async def on_raw_poll_vote_add(self, payload: discord.RawPollVoteActionEvent):
        if not (guild := await self.get_or_fetch_guild(payload.guild_id)):
            return
        config: Dict[str, Union[bool, Union[Optional[int], Dict[str, str]]]] = (
            await self.config.guild(guild).log()
        )
        if not config.get("toggle", False):
            return
        if not (user := await self.bot.get_or_fetch_member(guild, payload.user_id)):
            return
        if not (log_chan_id := config.get("channel", None)):
            return
        me: discord.Member = await self.bot.get_or_fetch_member(
            guild, cast(discord.ClientUser, self.bot.user).id
        )
        if not (
            (channel := await self.get_or_fetch_guild_channel(guild, payload.channel_id))
            and channel.permissions_for(me).read_message_history
            and channel.permissions_for(me).view_channel
            and isinstance(channel, (discord.TextChannel, discord.Thread))
        ):
            return
        if not (log_chan := await self.get_or_fetch_guild_channel(guild, log_chan_id)):
            return
        if not (
            (message := await channel.fetch_message(payload.message_id)) and (poll := message.poll)
        ):
            return
        if not (answer := poll.get_answer(payload.answer_id)):
            return
        await self._send_response(
            log_chan,
            user,
            answer,
            message=cast(Dict[str, str], config["message"]).get("add", _default_add),
            default=_default_add,
            value=cast(Group, cast(Group, self.config.guild(guild).log).message).add,
        )

    @commands.Cog.listener()
    async def on_raw_poll_vote_remove(self, payload: discord.RawPollVoteActionEvent):
        if not (guild := await self.get_or_fetch_guild(payload.guild_id)):
            return
        config: Dict[str, Union[bool, Union[Optional[int], Dict[str, str]]]] = (
            await self.config.guild(guild).log()
        )
        if not config.get("toggle", False):
            return
        if not (user := await self.bot.get_or_fetch_member(guild, payload.user_id)):
            return
        if not (log_chan_id := config.get("channel", None)):
            return
        me: discord.Member = await self.bot.get_or_fetch_member(
            guild, cast(discord.ClientUser, self.bot.user).id
        )
        if not (
            (channel := await self.get_or_fetch_guild_channel(guild, payload.channel_id))
            and channel.permissions_for(me).read_message_history
            and channel.permissions_for(me).view_channel
            and isinstance(channel, (discord.TextChannel, discord.Thread))
        ):
            return
        if not (log_chan := await self.get_or_fetch_guild_channel(guild, log_chan_id)):
            return
        if not (
            (message := await channel.fetch_message(payload.message_id)) and (poll := message.poll)
        ):
            return
        if not (answer := poll.get_answer(payload.answer_id)):
            return
        await self._send_response(
            log_chan,
            user,
            answer,
            message=cast(Dict[str, str], config["message"]).get("remove", _default_remove),
            default=_default_remove,
            value=cast(Group, cast(Group, self.config.guild(guild).log).message).remove,
        )

    @commands.guild_only()
    @commands.group(name="discordpolls", aliases=["discordpoll", "dpoll"])
    async def _poll(self, _: commands.GuildContext):
        """Base command to manage polls."""

    @_poll.command(name="create")
    @commands.cooldown(1, 30, commands.BucketType.channel)
    @commands.has_permissions(send_polls=True)
    @commands.bot_has_permissions(send_polls=True)
    async def _poll_create(
        self,
        ctx: commands.GuildContext,
        *,
        question: QuestionConverter,
        options: commands.Greedy[OptionConverter],
        duration: commands.Range[int, 1, 3] = 12,
        multiple: bool = False,
    ):
        """
        Create a poll.

        **Arguments**:
        - `question :` may be separated by a `;` and have no space.
        - `options  :` may be separated by a `|` and have no space.
        - `duration :` duration of the poll, can only be hours (default: 12).
        - `multiple :` allow/deny multiple selection (default: False).
        """
        if len(options) > 10:
            raise commands.BadArgument("Discord polls only support 10 or lesser arguments.")
        dt: datetime.timedelta = datetime.timedelta(hours=duration)
        q, q_emoji = cast(Tuple[str, Optional[discord.PartialEmoji]], question)
        media: discord.PollMedia = discord.PollMedia(text=q, emoji=q_emoji)
        poll: discord.Poll = discord.Poll(
            media, dt, multiple=multiple, layout_type=discord.PollLayoutType.default
        )
        for string, emoji in cast(List[Tuple[str, Optional[discord.PartialEmoji]]], options):
            poll.add_answer(text=string, emoji=emoji)
        await ctx.send(poll=poll)

    @_poll.command(name="end", aliases=["stop"])
    async def _poll_end(self, ctx: commands.Context, poll: PollConverter):
        """
        End a poll owned by [botname].

        **Arguments**:
        - `poll :` the message with a poll attached (must be owned by [botname]).
        """
        if (message := poll.message) and message.author.id != ctx.me.id:
            raise commands.BadArgument("Cannot end polls not authored by the bot.")
        await poll.end()
        await ctx.tick(message="Ended the poll.")

    @_poll.command(name="answer", aliases=["option"])
    async def _answer(
        self,
        ctx: commands.Context,
        poll: PollConverter,
        number: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ):
        """
        View info a specific answer of a poll.

        **Arguments**:
        - `poll   :` the message with a poll attached.
        - `number :` the answer number/id.
        """
        if not (answer := poll.get_answer(id=number)):
            raise commands.BadArgument("This poll only has {} answers.".format(len(poll.answers)))
        users: List[Union[discord.User, discord.Member]] = [
            voter async for voter in answer.voters()
        ]
        string: str = "\n".join(
            [
                "`{0} `: {1.mention} (`{1.id}`)".format(
                    idx + 1,
                    user,
                )
                for idx, user in enumerate(users)
            ]
        )
        pages: List[str] = list(pagify(string, page_length=1024))
        embeds: List[discord.Embed] = []
        for idx, page in enumerate(pages):
            embed: discord.Embed = discord.Embed(
                title="{} Answer!".format(ordinal(number).upper()),
                color=await ctx.embed_color(),
                url=poll.message.jump_url if poll.message else None,
                description=(
                    """
                `Question :` {}\n
                `Answer   :` {}\n
                `Emoji    :` {}\n
                `Votes    :` {}\n
                `Voted    :` {}\n
                """.format(
                        poll.question,
                        answer.text.strip(),
                        emoji if (emoji := answer.emoji) else "None",
                        ul if (ul := len(users)) >= (vc := answer.vote_count) else vc,
                        True if ctx.author in users else answer.self_voted,
                    )
                ),
            )
            embed.add_field(name="Voters:", value=page, inline=False)
            embed.set_footer(text="Page {}/{}".format(idx, len(pages)))
            embeds.append(embed)
        await SimpleMenu(embeds, disable_after_timeout=True).start(ctx)

    @_poll.command(name="answers", aliases=["options"])
    async def _poll_answers(self, ctx: commands.Context, poll: PollConverter):
        """
        View all the answers of a poll.

        **Arguments**:
        - `poll :` the message with a poll attached.
        """
        if not (answers := poll.answers):
            raise commands.BadArgument("Poll does not have any answers.")
        view: DisableOnTimeoutView = DisableOnTimeoutView(ctx)
        counter: int = 1
        for idx, answer in enumerate(answers):
            if idx > 4:
                counter: int = 2
            view.add_item(PollAnswerButton(ctx, answer, row=counter))
        users: List[Union[discord.User, discord.Member]] = [
            voter async for voter in answers[0].voters()
        ]
        embed: discord.Embed = discord.Embed(
            title="{} Answer!".format(ordinal(answers[0].id).upper()),
            color=await ctx.embed_color(),
            url=poll.message.jump_url if poll.message else None,
            description=(
                """
                `Question :` {}\n
                `Answer   :` {}\n
                `Emoji    :` {}\n
                `Votes    :` {}\n
                `Voted    :` {}\n
                """.format(
                    poll.question,
                    answers[0].text.strip(),
                    emoji if (emoji := answers[0].emoji) else "None",
                    ul if (ul := len(users)) >= (vc := answers[0].vote_count) else vc,
                    True if ctx.author in users else answers[0].self_voted,
                )
            ),
        )
        string: str = "\n".join(
            [
                "`{0} `: {1.mention} (`{1.id}`)".format(
                    idx + 1,
                    user,
                )
                for idx, user in enumerate(users)
            ]
        )
        for idx, page in enumerate(list(pagify(string, page_length=1024))):
            if idx > 24:
                continue
            embed.add_field(name="Voters:", value=page, inline=False)
        embed.set_footer(text="Page: {}/{}.".format(answers[0].id, len(answers)))
        await ctx.send(
            embed=embed,
            view=view,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @_poll.command(name="giveroles", aliases=["roles", "role"])
    @commands.bot_has_permissions(manage_roles=True)
    @commands.admin_or_permissions(administrator=True)
    @commands.cooldown(1, 120, commands.BucketType.guild)
    async def _poll_give_roles(
        self,
        ctx: commands.GuildContext,
        poll: PollConverter,
        number: Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        *roles: discord.Role,
    ):
        """
        Mass apply role to all the voters of a specific answer in a poll.

        **Arguments**:
        - `poll   :` the message with a poll attached.
        - `number :` the answer number/id.
        - `roles  :` roles to be applied.
        """
        async with ctx.typing():
            if not (answer := poll.get_answer(id=number)):
                raise commands.BadArgument(
                    "This poll only has {} answers.".format(len(poll.answers))
                )
            counter: int = 0
            members: List[Union[discord.User, discord.Member]] = [
                voter async for voter in answer.voters()
            ]
            for member in members:
                if isinstance(member, discord.User):
                    continue
                for role in roles:
                    if not ctx.author._roles.has(role.id):
                        with contextlib.suppress(discord.HTTPException):
                            await member.add_roles(role)
                            counter += 1
        await ctx.send(
            (
                """
                Added {} roles to {} user{}.\n
                Question: {}.
                """.format(
                    len(roles), counter, "s" if counter > 1 else "", poll.question
                )
            )
        )

    @commands.admin_or_permissions(administrator=True)
    @_poll.group(name="log", aliases=["logging"])
    async def _poll_log(self, _: commands.GuildContext):
        """
        Logging Configuration Commands For Polls.
        """

    @cast(commands.Group, _poll_log).command(name="toggle")
    async def _poll_log_toggle(self, ctx: commands.GuildContext, true_or_false: bool):
        """
        Toggle poll logging in this server.
        """
        await cast(Group, self.config.guild(ctx.guild).log).toggle.set(true_or_false)
        await ctx.send(
            "Logging is not {} in this server.".format("enabled" if true_or_false else "disabled")
        )

    @cast(commands.Group, _poll_log).command(name="channel")
    async def _poll_log_channel(
        self, ctx: commands.GuildContext, channel: Optional[discord.TextChannel] = None
    ):
        """
        Configure the logging channel.
        """
        if not channel:
            await cast(Group, self.config.guild(ctx.guild).log).channel.clear()
            await ctx.send("Cleared the logging channel.")
            return
        await cast(Group, self.config.guild(ctx.guild).log).channel.set(channel.id)
        await ctx.send("Logging channel set to {}.".format(channel.jump_url))

    @cast(commands.Group, _poll_log).command(name="message")
    async def _poll_log_message(
        self,
        ctx: commands.GuildContext,
        type: Literal["add", "remove"],
        *,
        message: Optional[TagScriptConverter] = None,
    ):
        """
        Configure the poll logging message.

        [Docs WIP]
        """
        if type.lower() == "add":
            if not message:
                await cast(
                    Group, cast(Group, self.config.guild(ctx.guild).log).message
                ).add.clear()
                await ctx.send(
                    "Logging message for on vote add was reset to default.\n{}".format(
                        box(_default_add, lang="json")
                    )
                )
                return
            await cast(Group, cast(Group, self.config.guild(ctx.guild).log).message).add.set(
                message
            )
            await ctx.send(
                "Logging message for on vote add was configured to:\n{}".format(
                    box(str(message), lang="json")
                )
            )
        elif type.lower() == "remove":
            if not message:
                await cast(
                    Group, cast(Group, self.config.guild(ctx.guild).log).message
                ).remove.clear()
                await ctx.send(
                    "Logging message for on vote remove was reset to default.\n{}".format(
                        box(_default_remove, lang="json")
                    )
                )
                return
            await cast(Group, cast(Group, self.config.guild(ctx.guild).log).message).remove.set(
                message
            )
            await ctx.send(
                "Logging message for on vote remove was configured to:\n{}".format(
                    box(str(message), lang="json")
                )
            )
        else:
            raise commands.UserFeedbackCheckFailure("Invalid type. Available: `add` or `remove`.")

    @cast(commands.Group, _poll_log).command(
        name="settings", aliases=["showsettings", "show", "ss"]
    )
    async def _poll_log_settings(self, ctx: commands.GuildContext):
        """
        View the settings for poll logging.
        """
        config: Dict[str, Union[bool, Union[Optional[int], Dict[str, str]]]] = (
            await self.config.guild(ctx.guild).log()
        )
        embed: discord.Embed = discord.Embed(
            title="Poll Logging Settings!",
            color=await ctx.embed_color(),
            description=(
                """
                **Toggle** : {}\n
                **Channel**: {}\n 
                """.format(
                    config.get("toggle", False),
                    (
                        channel.mention
                        if (channel := ctx.guild.get_channel(config.get("channel", None)))
                        else None
                    ),
                )
            ),
        )
        embed.add_field(
            name="On Vote Add:",
            value=box(cast(Dict[str, str], config["message"]).get("add", _default_add)),
            inline=False,
        )
        embed.add_field(
            name="On Vote Remove:",
            value=box(cast(Dict[str, str], config["message"]).get("remove", _default_remove)),
            inline=False,
        )
        embed.set_thumbnail(url=icon.url if (icon := ctx.guild.icon) else None)
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
