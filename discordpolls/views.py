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
from typing import Any, List, Union, cast

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.tree import RedTree

from .utils import ordinal


class DisableOnTimeoutView(discord.ui.View):
    def __init__(self, ctx: commands.Context, *, timeout: float = 160.0) -> None:
        super().__init__(timeout=timeout)
        self._message: discord.Message = discord.utils.MISSING
        self.ctx: commands.Context = ctx
        self.tree: RedTree = ctx.bot.tree

    async def _check(self, interaction: discord.Interaction[Red]) -> bool:
        if self.ctx.author.id != interaction.user.id:
            await self.tree._send_from_interaction(
                interaction,
                "You're not allowed to interact with this message.",
                reference=(
                    None
                    if not (message := interaction.message)
                    else message.to_reference(fail_if_not_exists=False)
                ),
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return False
        return True

    async def on_timeout(self) -> None:
        if self._message is not discord.utils.MISSING:
            for item in self.children:
                item: discord.ui.Item["DisableOnTimeoutView"]
                if hasattr(item, "style"):
                    item.style = discord.ButtonStyle.gray  # type: ignore
                if hasattr(item, "disabled"):
                    item.disabled = True  # type: ignore
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)


class PollAnswerButton(discord.ui.Button[DisableOnTimeoutView]):
    def __init__(self, ctx: commands.Context, answer: discord.PollAnswer, **kwargs: Any) -> None:
        super().__init__(
            style=discord.ButtonStyle.green,
            label=str(answer.id),
            emoji=emoji if (emoji := answer.emoji) else None,
            **kwargs,
        )
        self.ctx: commands.Context = ctx
        self.bot: Red = cast(Red, ctx.bot)
        self.answer: discord.PollAnswer = answer

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        users: List[Union[discord.User, discord.Member]] = [
            voter async for voter in self.answer.voters()
        ]
        embed: discord.Embed = discord.Embed(
            title="{}".format(ordinal(self.answer.id).upper()),
            color=await self.ctx.embed_color(),
            url=self.answer.poll.message.jump_url if self.answer.poll.message else None,
            description=(
                """
                `Question :` {}
                `Answer   :` {}
                `Emoji    :` {}
                `Votes    :` {}
                `Voted    :` {}
                """.format(
                    self.answer.poll.question,
                    self.answer.text.strip(),
                    emoji if (emoji := self.answer.emoji) else "None",
                    ul if (ul := len(users)) >= (vc := self.answer.vote_count) else vc,
                    (
                        True
                        if interaction.user.id in [user.id for user in users]
                        else self.answer.self_voted
                    ),
                )
            ),
        )
        embed.add_field(
            name="Voters:",
            value="\n".join(
                [
                    "`{0} `: {1.mention} (`{1.id}`)".format(
                        idx + 1,
                        user,
                    )
                    for idx, user in enumerate(users)
                ],
            )[:1024],
        )
        embed.set_footer(text="Page: {}/{}".format(self.answer.id, len(self.answer.poll.answers)))
        with contextlib.suppress(discord.HTTPException):
            await interaction.edit_original_response(embed=embed)
