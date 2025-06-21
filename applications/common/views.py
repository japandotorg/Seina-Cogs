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
import logging
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    Union,
    cast,
)

import discord
from discord.ext.commands import converter
from redbot.core import app_commands, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box
from redbot.core.utils.views import ConfirmView, SimpleMenu

from ..common.exceptions import ApplicationError
from ..common.tagscript import messages
from .finders import EmojiFinder
from .models import (
    Application,
    Buttons,
    ChoiceButtons,
    Question,
    Response,
    Styles,
    Voters,
    VoterSettings,
)
from .utils import GuildInteraction

if TYPE_CHECKING:
    from ..core import Applications

log: logging.Logger = logging.getLogger("red.seina.applications.common.views")


class InteractionSimpleMenu(SimpleMenu):
    async def inter(
        self, interaction: discord.Interaction[Red], *, ephemeral: bool = True
    ) -> None:
        self._fallback_author_to_ctx: bool = False
        self.author: discord.abc.User = interaction.user
        kwargs: Dict[str, Any] = await self.get_page(self.current_page)
        self.message: discord.Message = await interaction.followup.send(
            **kwargs, ephemeral=ephemeral
        )


class ChooseChoicesModal(discord.ui.Modal):
    yl: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="yes label",
        style=discord.TextStyle.paragraph,
        placeholder="Specify the label for the `yes` button. (50 characters only)",
        max_length=50,
        required=False,
    )
    ye: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="yes emoji",
        style=discord.TextStyle.paragraph,
        placeholder="Specify the emoji for the `yes` button. (format - <a:name:id>)",
        required=False,
    )
    nl: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="no label",
        style=discord.TextStyle.paragraph,
        placeholder="Specify the label for the `no` button. (50 characters only)",
        required=False,
    )
    ne: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="no emoji",
        style=discord.TextStyle.paragraph,
        placeholder="Specify the emoji for the `no` button. (format - <a:name:id>)",
        required=False,
    )
    out: discord.ui.TextInput[discord.ui.View] = discord.ui.TextInput(
        label="timeout",
        style=discord.TextStyle.paragraph,
        placeholder=(
            "Specify if the application should automcatically close if no choices are submitted."
        ),
        required=False,
    )

    def __init__(self, user: discord.User, *, application: Application) -> None:
        super().__init__(title="Configure Boolean Buttons")
        self.user: discord.User = user
        self.app: Application = application

    @staticmethod
    async def tfn(self: discord.ui.View) -> None:
        for item in self.children:
            item: discord.ui.Item[discord.ui.View]
            item.disabled = True  # pyright: ignore[reportAttributeAccessIssue]
        with contextlib.suppress(discord.HTTPException):
            await cast(
                discord.Message,
                self._message,  # pyright: ignore[reportAttributeAccessIssue]
            ).edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You're not allowed to use this interaction!", ephemeral=True
            )
            return False
        return True

    @staticmethod
    def to_embed(app: Application) -> discord.Embed:
        embed: discord.Embed = discord.Embed(
            title="__**Boolean Button Settings**__",
            description=(
                "__**Required**__: {required}\n\n"
                "__**True**__\n"
                "- **label**: {yes.label}\n"
                "- **emoji**: {yes.emoji}\n"
                "\n"
                "__**False**__\n"
                "- **label**: {no.label}\n"
                "- **emoji**: {no.emoji}\n"
            ).format(
                required="Yes" if app.buttons.choice.required else "No",
                yes=app.buttons.choice.yes,
                no=app.buttons.choice.no,
            ),
            color=discord.Color.from_str(app.settings.color),
        )
        return embed

    async def on_submit(self, interaction: discord.Interaction[Red], /) -> None:
        await interaction.response.defer()
        if not interaction.guild:
            return await interaction.followup.send(
                "Something went wrong, try again later!", ephemeral=True
            )
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.exception(
                "Attempted to utilize a feature of the Applications cog while it is currently unloaded."
            )
            return await interaction.followup.send(
                "Something went wrong, try again later!", ephemeral=True
            )
        if not any(
            [
                (yl := self.yl._value),
                (ye := self.ye._value),
                (nl := self.nl._value),
                (ne := self.ne._value),
                (out := self.out._value),
            ]
        ):
            return await interaction.followup.send(
                "Submission terminated.",
                embed=self.to_embed(self.app).set_thumbnail(
                    url=getattr(interaction.guild.icon, "url", None)
                ),
            )
        choice: ChoiceButtons = self.app.buttons.choice
        yem, nem, tout = (
            cast(Union[str, discord.Emoji, None], None),
            cast(Union[str, discord.Emoji, None], None),
            cast(Optional[bool], None),
        )
        if ye:
            try:
                yem: Union[str, discord.Emoji, None] = await EmojiFinder().finder(interaction, ye)
            except commands.BadArgument as error:
                return await interaction.followup.send(error, ephemeral=True)
        if ne:
            try:
                nem: Union[str, discord.Emoji, None] = await EmojiFinder().finder(interaction, ne)
            except commands.BadArgument as error:
                return await interaction.followup.send(error, ephemeral=True)
        if out:
            try:
                tout: Optional[bool] = converter._convert_to_bool(out)
            except commands.BadArgument as error:
                return await interaction.followup.send(
                    "Expected boolean value, got {} instead.".format(str(error).lower()),
                    ephemeral=True,
                )
        if yl:
            choice.yes.label = yl
        if yem:
            choice.yes.emoji = str(yem)
        if nl:
            choice.no.label = nl
        if nem:
            choice.no.emoji = str(yem)
        if tout:
            choice.required = tout
        async with cog.config.guild(interaction.guild).apps() as apps:
            apps.update(**{self.app.name.lower(): self.app.model_dump(mode="python")})
        await interaction.followup.send(
            embed=self.to_embed(self.app).set_thumbnail(
                url=getattr(interaction.guild.icon, "url", None)
            )
        )


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

    def __init__(
        self,
        user: discord.User,
        *,
        application: Application,
        question: Question,
    ) -> None:
        super().__init__(title="Choices", custom_id="model:{}".format(id(question)))
        self.user: discord.User = user
        self.app: Application = application
        self.question: Question = question

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You're not allowed to use this interaction!", ephemeral=True
            )
            return False
        return True

    async def on_submit(self, interaction: discord.Interaction[Red], /) -> None:
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
            child.disabled = True  # pyright: ignore[reportAttributeAccessIssue]

        if self._message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "You're not allowed to use this interaction!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Choices", style=discord.ButtonStyle.green)
    async def choices(
        self,
        interaction: discord.Interaction[Red],
        _: discord.ui.Button["QuestionChoicesView"],
    ) -> None:
        modal: QuestionChoicesModel = QuestionChoicesModel(
            self.user, application=self.application, question=self.question
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
                "Something went wrong, failed to parse the answers.",
                ephemeral=True,
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
    async def cancel(
        self,
        interaction: discord.Interaction[Red],
        _: discord.ui.Button["QuestionChoicesView"],
    ) -> None:
        await interaction.response.send_message(
            "The question was successfully discarded.", ephemeral=True
        )
        await self.on_timeout()


class DynamicDMApplyButton(
    discord.ui.DynamicItem[discord.ui.Button[discord.ui.View]],
    template=r"message:(?P<id>[0-9]+):guild:(?P<guild>[0-9]+):app:(?P<name>[a-z\s]+)",
):
    def __init__(self, message_id: int, guild_id: int, name: str, **kwargs: Any) -> None:
        super().__init__(
            discord.ui.Button(
                **kwargs,
                custom_id="message:{}:guild:{}:app:{}".format(message_id, guild_id, name),
            )
        )
        self.message_id: int = message_id
        self.guild_id: int = guild_id
        self.name: str = name

    @staticmethod
    def format_style(data: Styles) -> discord.ButtonStyle:
        return getattr(discord.ButtonStyle, data.lower(), discord.ButtonStyle.blurple)

    @classmethod
    async def from_custom_id(
        cls: Type["DynamicDMApplyButton"],
        interaction: GuildInteraction,
        _: discord.ui.Item["ApplicationView"],
        match: re.Match[str],
    ) -> "DynamicDMApplyButton":
        message_id: int = int(match["id"])
        guild_id: int = int(match["guild"])
        name: str = str(match["name"])
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            raise app_commands.CheckFailure()
        try:
            app: Application = await cog.manager.get_application(guild_id, name=name.lower())
        except ApplicationError:
            raise app_commands.CheckFailure()
        data: Buttons = app.buttons
        return cls(
            message_id,
            guild_id,
            name,
            style=cls.format_style(data.style),
            label=data.label,
            emoji=data.emoji,
        )

    async def callback(self, interaction: discord.Interaction[Red]) -> None:
        await interaction.response.defer()
        guild: Optional[discord.Guild] = interaction.client.get_guild(self.guild_id)
        if not guild:
            return await interaction.followup.send("Uh oh, something went wrong, try again later!")
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            return await interaction.followup.send(
                "No idea how this happened, but the application cog seems to be unloaded.",
                ephemeral=True,
            )
        try:
            app: Application = await cog.manager.get_application(
                self.guild_id, name=self.name.lower()
            )
        except ApplicationError as error:
            return await interaction.followup.send(str(error), ephemeral=True)
        interaction.client.dispatch("application_applied", interaction, guild, app)
        with contextlib.suppress(discord.HTTPException):
            message: discord.Message = await cast(
                discord.DMChannel, interaction.channel
            ).fetch_message(self.message_id)
            self.item.disabled = True
            await message.edit(view=self.view)


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
        return getattr(discord.ButtonStyle, data.lower(), discord.ButtonStyle.green)

    @classmethod
    async def from_custom_id(
        cls: type["DynamicApplyButton"],
        interaction: GuildInteraction,
        _: discord.ui.Item["ApplicationView"],
        match: re.Match[str],
    ) -> "DynamicApplyButton":
        guild_id: int = int(match["id"])
        name: str = str(match["name"])
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            raise app_commands.CheckFailure()
        try:
            app: Application = await cog.manager.get_application(guild_id, name=name.lower())
        except ApplicationError:
            raise app_commands.CheckFailure()
        data: Buttons = app.buttons
        return cls(
            guild_id,
            name,
            style=cls.format_style(data.style),
            label=data.label,
            emoji=data.emoji,
        )

    async def edit(
        self,
        cog: "Applications",
        interaction: "GuildInteraction",
        *,
        application: Application,
    ) -> None:
        kwargs: Dict[str, Any] = await messages(cog, interaction, app=application)
        view: "ApplicationView" = ApplicationView(
            self.guild_id,
            self.name.lower(),
            label=application.buttons.label,
            emoji=application.buttons.emoji,
            style=self.format_style(application.buttons.style),
        )
        with contextlib.suppress(discord.HTTPException):
            await interaction.message.edit(**kwargs, view=view)

    async def interaction_check(self, interaction: GuildInteraction) -> bool:
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            await interaction.response.send_message(
                "Something went wrong, try again later!", ephemeral=True
            )
            return False
        try:
            app: Application = await cog.manager.get_application(
                self.guild_id, name=self.name.lower()
            )
        except ApplicationError as error:
            await interaction.followup.send(str(error), ephemeral=True)
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
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            return await interaction.followup.send(
                "No idea how this happened, but the application cog seems to be unloaded.",
                ephemeral=True,
            )
        try:
            app: Application = await cog.manager.get_application(
                self.guild_id, name=self.name.lower()
            )
        except ApplicationError as error:
            return await interaction.followup.send(str(error), ephemeral=True)
        interaction.client.dispatch("application_applied", interaction, interaction.guild, app)
        await interaction.followup.send(
            "Application started in DMs! {}".format(
                getattr(interaction.user.dm_channel, "jump_url", "#dms")
            ),
            ephemeral=True,
        )
        await self.edit(cog, interaction, application=app)


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
        self,
        question: Question,
        *,
        required: bool = True,
        timeout: float = 60.0,
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
            child.disabled = True  # pyright: ignore[reportAttributeAccessIssue]

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
            child.disabled = True  # pyright: ignore[reportAttributeAccessIssue]

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


class DynamicUpVoteButton(
    discord.ui.DynamicItem[discord.ui.Button[discord.ui.View]],
    template=r"app:up:(?P<name>[a-z\s]+):(?P<response>[a-zA-Z0-9_.-]+)",
):
    def __init__(self, name: str, response_id: str, *, emoji: str, label: str) -> None:
        super().__init__(
            discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.blurple,
                custom_id="app:up:{}:{}".format(name, response_id),
            )
        )
        self.name: str = name
        self.response_id: str = response_id

    @staticmethod
    def update_labels(voters: Voters, user: discord.Member) -> Literal["added", "removed"]:
        if user.id in voters.up:
            voters.up.remove(user.id)
            mode: str = "removed"
        elif user.id not in voters.up:
            voters.up.append(user.id)
            if user.id in voters.down:
                voters.down.remove(user.id)
            if user.id in voters.null:
                voters.null.remove(user.id)
            mode: str = "added"
        else:
            raise app_commands.UserFeedbackCheckFailure(
                "Uh oh! Something went wrong try again later"
            )
        return mode

    @classmethod
    async def from_custom_id(
        cls: Type["DynamicUpVoteButton"],
        interaction: GuildInteraction,
        _: discord.ui.Item[discord.ui.View],
        match: re.Match[str],
    ) -> "DynamicUpVoteButton":
        name: str = str(match["name"])
        response_id: str = str(match["response"])
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            raise app_commands.CheckFailure()
        try:
            app: Application = await cog.manager.get_application(
                interaction.guild.id, name=name.lower()
            )
        except ApplicationError:
            raise app_commands.CheckFailure()
        response: Response = await cog.manager.get_response_from_application(
            app, response=response_id
        )
        settings: VoterSettings = app.settings.voters
        voters: Voters = response.voters
        return cls(name, response_id, emoji=settings.up, label=str(len(voters.up)))

    async def callback(self, interaction: GuildInteraction) -> None:
        await interaction.response.defer()
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            return await interaction.followup.send(
                "No idea how this happened, but the application cog seems to be unloaded.",
                ephemeral=True,
            )
        try:
            app: Application = await cog.manager.get_application(
                interaction.guild.id, name=self.name.lower()
            )
        except ApplicationError as error:
            return await interaction.followup.send(str(error), ephemeral=True)
        response: Response = await cog.manager.get_response_from_application(
            app, response=self.response_id
        )
        voters: Voters = response.voters
        self.update_labels(voters, interaction.user)
        async with cog.config.guild_from_id(interaction.guild.id).apps() as apps:
            apps.update(**{self.name.lower(): app.model_dump(mode="python")})
        view: "VotersView" = VotersView(self.name, self.response_id, app.settings.voters, voters)
        with contextlib.suppress(discord.HTTPException):
            await interaction.message.edit(view=view)


class DynamicDownVoteButton(
    discord.ui.DynamicItem[discord.ui.Button[discord.ui.View]],
    template=r"app:down:(?P<name>[a-z\s]+):(?P<response>[a-zA-Z0-9_.-]+)",
):
    def __init__(self, name: str, response_id: str, *, emoji: str, label: str) -> None:
        super().__init__(
            discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.blurple,
                custom_id="app:down:{}:{}".format(name, response_id),
            )
        )
        self.name: str = name
        self.response_id: str = response_id

    @staticmethod
    def update_labels(voters: Voters, user: discord.Member) -> Literal["added", "removed"]:
        if user.id in voters.down:
            voters.down.remove(user.id)
            mode: str = "removed"
        elif user.id not in voters.down:
            voters.down.append(user.id)
            if user.id in voters.up:
                voters.up.remove(user.id)
            if user.id in voters.null:
                voters.null.remove(user.id)
            mode: str = "added"
        else:
            raise app_commands.UserFeedbackCheckFailure(
                "Uh oh! Something went wrong try again later"
            )
        return mode

    @classmethod
    async def from_custom_id(
        cls: Type["DynamicDownVoteButton"],
        interaction: GuildInteraction,
        _: discord.ui.Item[discord.ui.View],
        match: re.Match[str],
    ) -> "DynamicDownVoteButton":
        name: str = str(match["name"])
        response_id: str = str(match["response"])
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            raise app_commands.CheckFailure()
        try:
            app: Application = await cog.manager.get_application(
                interaction.guild.id, name=name.lower()
            )
        except ApplicationError:
            raise app_commands.CheckFailure()
        response: Response = await cog.manager.get_response_from_application(
            app, response=response_id
        )
        settings: VoterSettings = app.settings.voters
        voters: Voters = response.voters
        return cls(name, response_id, emoji=settings.down, label=str(len(voters.down)))

    async def callback(self, interaction: GuildInteraction) -> None:
        await interaction.response.defer()
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            return await interaction.followup.send(
                "No idea how this happened, but the application cog seems to be unloaded.",
                ephemeral=True,
            )
        try:
            app: Application = await cog.manager.get_application(
                interaction.guild.id, name=self.name.lower()
            )
        except ApplicationError as error:
            return await interaction.followup.send(str(error), ephemeral=True)
        response: Response = await cog.manager.get_response_from_application(
            app, response=self.response_id
        )
        voters: Voters = response.voters
        self.update_labels(voters, interaction.user)
        async with cog.config.guild_from_id(interaction.guild.id).apps() as apps:
            apps.update(**{self.name.lower(): app.model_dump(mode="python")})
        view: "VotersView" = VotersView(self.name, self.response_id, app.settings.voters, voters)
        with contextlib.suppress(discord.HTTPException):
            await interaction.message.edit(view=view)


class DynamicNullVoteButton(
    discord.ui.DynamicItem[discord.ui.Button[discord.ui.View]],
    template=r"app:null:(?P<name>[a-z\s]+):(?P<response>[a-zA-Z0-9_.-]+)",
):
    def __init__(self, name: str, response_id: str, *, emoji: str, label: str) -> None:
        super().__init__(
            discord.ui.Button(
                label=label,
                emoji=emoji,
                style=discord.ButtonStyle.blurple,
                custom_id="app:null:{}:{}".format(name, response_id),
            )
        )
        self.name: str = name
        self.response_id: str = response_id

    @staticmethod
    def update_labels(voters: Voters, user: discord.Member) -> Literal["added", "removed"]:
        if user.id in voters.null:
            voters.null.remove(user.id)
            mode: str = "removed"
        elif user.id not in voters.null:
            voters.null.append(user.id)
            if user.id in voters.up:
                voters.up.remove(user.id)
            if user.id in voters.down:
                voters.down.remove(user.id)
            mode: str = "added"
        else:
            raise app_commands.UserFeedbackCheckFailure(
                "Uh oh! Something went wrong try again later"
            )
        return mode

    @classmethod
    async def from_custom_id(
        cls: Type["DynamicNullVoteButton"],
        interaction: GuildInteraction,
        _: discord.ui.Item[discord.ui.View],
        match: re.Match[str],
    ) -> "DynamicNullVoteButton":
        name: str = str(match["name"])
        response_id: str = str(match["response"])
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            raise app_commands.CheckFailure()
        try:
            app: Application = await cog.manager.get_application(
                interaction.guild.id, name=name.lower()
            )
        except ApplicationError:
            raise app_commands.CheckFailure()
        response: Response = await cog.manager.get_response_from_application(
            app, response=response_id
        )
        settings: VoterSettings = app.settings.voters
        voters: Voters = response.voters
        return cls(name, response_id, emoji=settings.null, label=str(len(voters.null)))

    async def callback(self, interaction: GuildInteraction) -> None:
        await interaction.response.defer()
        cog: Optional["Applications"] = cast(
            Optional["Applications"], interaction.client.get_cog("Applications")
        )
        if not cog:
            log.error("No idea how this happened, but the application cog seems to be unloaded.")
            return await interaction.followup.send(
                "No idea how this happened, but the application cog seems to be unloaded.",
                ephemeral=True,
            )
        try:
            app: Application = await cog.manager.get_application(
                interaction.guild.id, name=self.name.lower()
            )
        except ApplicationError as error:
            return await interaction.followup.send(str(error), ephemeral=True)
        response: Response = await cog.manager.get_response_from_application(
            app, response=self.response_id
        )
        voters: Voters = response.voters
        self.update_labels(voters, interaction.user)
        async with cog.config.guild_from_id(interaction.guild.id).apps() as apps:
            apps.update(**{self.name.lower(): app.model_dump(mode="python")})
        view: "VotersView" = VotersView(self.name, self.response_id, app.settings.voters, voters)
        with contextlib.suppress(discord.HTTPException):
            await interaction.message.edit(view=view)


class VotersView(discord.ui.View):
    def __init__(
        self,
        name: str,
        response_id: str,
        settings: VoterSettings,
        voters: Voters,
    ) -> None:
        super().__init__(timeout=None)
        self.add_item(
            DynamicUpVoteButton(name, response_id, emoji=settings.up, label=str(len(voters.up)))
        )
        self.add_item(
            DynamicNullVoteButton(
                name,
                response_id,
                emoji=settings.null,
                label=str(len(voters.null)),
            )
        )
        self.add_item(
            DynamicDownVoteButton(
                name,
                response_id,
                emoji=settings.down,
                label=str(len(voters.down)),
            )
        )
