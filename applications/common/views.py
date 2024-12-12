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

import re
import logging
import contextlib
from typing import TYPE_CHECKING, Any, List, Optional, Union, cast

import discord
from redbot.core.bot import Red
from redbot.core import commands
from redbot.core.utils.views import ConfirmView
from redbot.core.utils.chat_formatting import box

from ..common.utils import GuildInteraction
from .models import Application, ButtonSettings, Question, Styles

if TYPE_CHECKING:
    from ..core import Applications

log: logging.Logger = logging.getLogger("red.seina.applications.common.views")


class QuestionChoicesModel(discord.ui.Modal):
    choices: discord.ui.TextInput["QuestionChoicesView"] = discord.ui.TextInput(
        label="Choices",
        style=discord.TextStyle.long,
        placeholder=(
            "Enter your choices, each on a separate line. Maximum of 10. Example:\n"
            "Answer 1\n"
            "Answer 2\n"
            "Answer 3\n"
        ),
    )

    def __init__(self, *, application: Application, question: Question) -> None:
        super().__init__(title="Choices", custom_id="model:{}".format(id(question)))
        self.app: Application = application
        self.question: Question = question

    async def on_submit(self, interaction: discord.Interaction[Red]) -> None:
        await interaction.response.defer()
        questions: List[str] = self.choices.value.strip().splitlines()[:10]
        self.question.choices.extend(questions)
        view: ConfirmView = ConfirmView(interaction.user, disable_buttons=True)
        view.confirm_button.label = None
        view.confirm_button.emoji = "\N{HEAVY CHECK MARK}"
        view.dismiss_button.label = None
        view.dismiss_button.emoji = "\N{HEAVY MULTIPLICATION X}"
        embed: discord.Embed = discord.Embed(
            description=(
                "Do you want to include an `other` option?\n"
                "- Using an `other` option will add a text modal into the choices list."
            ),
            color=discord.Color.green(),
        )
        original: discord.InteractionMessage = await interaction.original_response()
        view.message = await original.channel.send(
            embed=embed,
            view=view,
            reference=original.to_reference(fail_if_not_exists=False),
        )
        await view.wait()
        if view.result:
            self.question.other = True
            await interaction.followup.send(
                "Successfully added an `other` option to the choices list!"
            )
        else:
            self.question.other = False
            await interaction.followup.send("Excluded an `other` option from the choices list!")
        self.stop()


class QuestionChoicesView(discord.ui.View):

    def __init__(
        self,
        user: discord.User,
        *,
        position: int,
        application: Application,
        question: Question,
        timeout: float = 120.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self.user: discord.User = user

        self.position: int = position
        self.application: Application = application
        self.question: Question = question

        self._message: discord.Message = discord.utils.MISSING

    async def on_timeout(self) -> None:
        for child in self.children:
            child: discord.ui.Item["QuestionChoicesView"]
            child.disabled = True  # type: ignore

        if self._message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You're not allowed to use this interaction!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Choices", style=discord.ButtonStyle.green)
    async def choices(self, interaction: discord.Interaction[Red], _: discord.ui.Button) -> None:
        modal: QuestionChoicesModel = QuestionChoicesModel(
            application=self.application, question=self.question
        )
        await interaction.response.send_modal(modal)
        if await modal.wait():
            return await interaction.followup.send(
                "Question was discarded because the choice submission timed out."
            )
        await self.on_timeout()
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            return
        if not self.question.choices:
            return await interaction.followup.send(
                "Something went wrong, failed to parse the answers.", ephemeral=True
            )
        if self.position == 0:
            self.application.questions.append(self.question)
        else:
            self.application.questions.insert(self.position - 1, self.question)
        async with cog.config.guild(interaction.guild).apps() as apps:
            apps.update(
                **{self.application.name.lower(): self.application.model_dump(mode="python")}
            )
        await interaction.followup.send(
            content="Successfully added the following choices -\n{}".format(
                box(
                    "\n".join(
                        [
                            "{}. {}".format(idx + 1, answer)
                            for idx, answer in enumerate(self.question.choices)
                        ]
                    ),
                    lang="sml",
                )
            )
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction[Red], _: discord.ui.Button) -> None:
        await interaction.response.send_message(
            "The question was successfully discarded.", ephemeral=True
        )
        await self.on_timeout()


class DynamicApplyButton(
    discord.ui.DynamicItem[discord.ui.Button["ApplicationView"]],
    template=r"guild:(?P<id>[0-9]+):app:(?P<name>[a-z\s]+)",
):
    def __init__(self, guild_id: int, name: str, **kwargs: Any) -> None:
        super().__init__(
            discord.ui.Button(**kwargs, custom_id="guild:{}:app:{}".format(guild_id, name)),
        )
        self.guild_id: int = guild_id
        self.name: str = name

    @staticmethod
    def format_style(data: Styles) -> discord.ButtonStyle:
        if data.lower() == "green":
            return discord.ButtonStyle.green
        elif data.lower() == "red":
            return discord.ButtonStyle.red
        elif data.lower() == "gray":
            return discord.ButtonStyle.gray
        elif data.lower() == "blurple":
            return discord.ButtonStyle.blurple
        else:
            return discord.ButtonStyle.green

    @classmethod
    async def from_custom_id(
        cls: type["DynamicApplyButton"],
        interaction: GuildInteraction,
        _: discord.ui.Item["ApplicationView"],
        match: re.Match[str],
    ) -> "DynamicApplyButton":
        guild_id: int = int(match["id"])
        name: str = str(match["name"])
        cog: Optional["Applications"] = interaction.client.get_cog("Applications")  # type: ignore
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            raise commands.CheckFailure()
        try:
            app: Application = cog.manager.cache[guild_id][name.lower()]
        except KeyError:
            raise commands.CheckFailure()
        data: ButtonSettings = app.buttons
        return cls(
            guild_id, name, style=cls.format_style(data.style), label=data.label, emoji=data.emoji
        )

    async def interaction_check(self, interaction: GuildInteraction) -> bool:
        cog: Optional["Applications"] = interaction.client.get_cog("Applications")  # type: ignore
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            await interaction.response.send_message(
                "Something went wrong, try again later!", ephemeral=True
            )
            return False
        try:
            app: Application = cog.manager.cache[self.guild_id][self.name.lower()]
        except KeyError:
            await interaction.response.send_message(
                "Could not find an application attached to this button!", ephemeral=True
            )
            return False
        if white := app.roles.whitelist:
            if interaction.user.id not in white:
                await interaction.response.send_message(
                    "You're not allowed to use this button.", ephemeral=True
                )
                return False
        elif black := app.roles.blacklist:
            if interaction.user.id in black:
                await interaction.response.send_message(
                    "You're not allowed to use this button.", ephemeral=True
                )
                return False
        return True

    async def callback(self, interaction: GuildInteraction) -> None:
        await interaction.response.defer()
        log.debug("deffered")
        cog: Optional["Applications"] = interaction.client.get_cog("Applications")  # type: ignore
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            return await interaction.followup.send(
                "No idea how this happened, but the application cog seems to be unloaded.",
                ephemeral=True,
            )
        try:
            app: Application = cog.manager.cache[self.guild_id][self.name.lower()]
        except KeyError:
            return await interaction.followup.send(
                "Could not find an application attached to this button!", ephemeral=True
            )
        interaction.client.dispatch("application_applied", interaction, app)
        log.debug("dispatched event on_application_applied")
        await interaction.followup.send(
            "Application started in DMs! {}".format(
                getattr(interaction.user.dm_channel, "jump_url", "#dms")
            ),
            ephemeral=True,
        )


class ApplicationView(discord.ui.View):
    def __init__(self, guild_id: int, name: str, **kwargs: Any) -> None:
        super().__init__(timeout=None)
        self.add_item(DynamicApplyButton(guild_id, name, **kwargs))


class SkipButton(discord.ui.Button[Union["ChoiceView", "CancelView", "PatchedConfirmView"]]):
    view: Union["ChoiceView", "CancelView", "PatchedConfirmView"]

    def __init__(self) -> None:
        super().__init__(label="Skip", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        self.view.cancel_or_skip(skip=True)
        await interaction.response.send_message("Skipped question!")
        self.view.stop()


class CancelButton(discord.ui.Button[Union["ChoiceView", "CancelView", "PatchedConfirmView"]]):
    view: Union["ChoiceView", "CancelView", "PatchedConfirmView"]

    def __init__(self) -> None:
        super().__init__(label="Cancel", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        self.view.cancel_or_skip(cancel=True)
        await interaction.response.send_message("Submission cancelled!")
        self.view.stop()


class ChoiceButton(discord.ui.Button["ChoiceView"]):
    label: str
    view: "ChoiceView"

    def __init__(self, label: str) -> None:
        super().__init__(label=label, style=discord.ButtonStyle.gray)

    async def callback(self, interaction: GuildInteraction) -> None:
        await interaction.response.defer()
        if self.view.answer is discord.utils.MISSING:
            self.view.answer = self.label
        self.view.stop()


class ChoiceView(discord.ui.View):
    def __init__(
        self, question: Question, *, required: bool = True, timeout: float = 60.0
    ) -> None:
        super().__init__(timeout=timeout)
        self.question: Question = question

        self.message: discord.Message = discord.utils.MISSING
        self.answer: str = discord.utils.MISSING
        self.cancel: bool = False
        self.skip: bool = False

        choices: List[str] = question.choices[:22]

        for choice in choices:
            self.add_item(ChoiceButton(choice))

        self.add_item(CancelButton())
        if not required:
            self.add_item(SkipButton())

    def cancel_or_skip(self, *, cancel: bool = False, skip: bool = False) -> None:
        self.cancel: bool = cancel
        self.skip: bool = skip

    async def on_timeout(self) -> None:
        for child in self.children:
            child: discord.ui.Item["ChoiceView"]
            child.disabled = True  # type: ignore

        if self.message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self.message.edit(view=self)


class CancelView(discord.ui.View):
    def __init__(self, *, required: bool = True, timeout: float = 60.0) -> None:
        super().__init__(timeout=timeout)
        self.message: discord.Message = discord.utils.MISSING
        self.cancel: bool = False
        self.skip: bool = False

        self.add_item(CancelButton())
        if not required:
            self.add_item(SkipButton())

    def cancel_or_skip(self, *, cancel: bool = False, skip: bool = False) -> None:
        self.cancel: bool = cancel
        self.skip: bool = skip

    async def on_timeout(self) -> None:
        for child in self.children:
            child: discord.ui.Item["CancelView"]
            child.disabled = True  # type: ignore

        if self.message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self.message.edit(view=self)


class PatchedConfirmView(ConfirmView):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cancel: bool = False
        self.skip: bool = False

    def cancel_or_skip(self, *, cancel: bool = False, skip: bool = False) -> None:
        self.cancel: bool = cancel
        self.skip: bool = skip
