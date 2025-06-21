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

import asyncio
import contextlib
from typing import (
    TYPE_CHECKING,
    Any,
    DefaultDict,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import discord
import TagScriptEngine as tse
from discord.ext.commands import converter
from redbot.core import commands
from redbot.core.config import Config
from redbot.core.utils import AsyncIter

from .exceptions import (
    ApplicationDoesNotExist,
    DuplicateApplicationError,
    NoQuestionsConfiguredError,
    TooManyQuestionsError,
)
from .models import (
    Application,
    EventRoles,
    Events,
    Question,
    Response,
    Styles,
    Threads,
)
from .tagscript import BLOCKS, DEFAULT_NOTIFICATION_MESSAGE, DEFAULT_THREAD_NAME
from .utils import (
    ChoiceButtons,
    ChoiceButtonType,
    Mentions,
    Notifications,
    TypedConfig,
    Voters,
    VoterSettings,
)

if TYPE_CHECKING:
    from ..core import Applications


class ApplicationManager:
    def __init__(self, cog: "Applications") -> None:
        self.cog: "Applications" = cog
        self.config: Config = cog.config
        self.cache: DefaultDict[int, Dict[str, Application]] = cog.cache

        self.engine: tse.AsyncInterpreter = tse.AsyncInterpreter(BLOCKS)

        self.lock: asyncio.Lock = asyncio.Lock()
        self.task: asyncio.Task[None] = discord.utils.MISSING

    def initialize(self) -> None:
        if self.task is discord.utils.MISSING:
            self.task: asyncio.Task[None] = asyncio.create_task(self.populate())

    def close(self) -> None:
        if self.task is not discord.utils.MISSING:
            self.task.cancel()

    async def process_tagscript(
        self,
        content: str,
        variables: Dict[str, tse.Adapter] = {},
        *,
        escape: Tuple[bool, bool] = (False, False),
    ) -> Dict[str, Any]:
        output: tse.Response = await self.engine.process(content, variables)
        kwargs: Dict[str, Any] = {}

        @staticmethod
        def format(content: str, *, mentions: bool, markdown: bool) -> str:
            if markdown:
                content: str = discord.utils.escape_markdown(content)
            if mentions:
                content: str = discord.utils.escape_mentions(content)
            return content[:2000]

        if body := output.body:
            mentions, markdown = escape
            kwargs["content"] = format(body, mentions=mentions, markdown=markdown)
        if embed := output.actions.get("embed"):
            kwargs["embed"] = embed
        return kwargs

    async def populate(self) -> None:
        await self.do_migrate()
        await self.lock.acquire()
        config: Dict[int, Dict[str, Dict[str, TypedConfig]]] = await self.config.all_guilds()
        async for _id, data in AsyncIter(config.items()):
            async for name, app in AsyncIter(data["apps"].items()):
                instance: Application = await Application.from_json(app)
                self.cache.setdefault(_id, {}).setdefault(name, instance)
        self.lock.release()

    async def do_migrate(self) -> None:
        await self.lock.acquire()
        config: Dict[int, Dict[str, Dict[str, TypedConfig]]] = await self.config.all_guilds()
        async for _id, data in AsyncIter(config.items()):
            async for _, app in AsyncIter(data["apps"].items()):
                with contextlib.suppress(KeyError):
                    if isinstance(app["settings"]["thread"], bool):
                        app["settings"]["thread"] = {
                            "toggle": app["settings"]["thread"],
                            "custom": DEFAULT_THREAD_NAME,
                        }
                app["buttons"].setdefault(
                    "choice",
                    ChoiceButtons(
                        yes=ChoiceButtonType(
                            label=None,
                            emoji="\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16}",
                        ),
                        no=ChoiceButtonType(label=None, emoji="\N{CROSS MARK}"),
                        required=False,
                    ),
                )
                app["settings"].setdefault(
                    "notifications",
                    Notifications(
                        toggle=True,
                        content=DEFAULT_NOTIFICATION_MESSAGE,
                        mentions=Mentions(users=True, roles=False, everyone=False),
                        channels=[],
                    ),
                ).setdefault("channels", [])
                app["settings"].setdefault(
                    "voters",
                    VoterSettings(
                        threshold=0,
                        up="\N{UPWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}",
                        down="\N{DOWNWARDS BLACK ARROW}\N{VARIATION SELECTOR-16}",
                        null="\N{NO ENTRY SIGN}",
                    ),
                )
                async for resp in AsyncIter(app["responses"]):
                    resp.setdefault("voters", Voters(up=[], down=[], null=[]))
            await self.config.guild_from_id(_id).apps.set(data["apps"])
        self.lock.release()

    async def get_application(self, guild: int, *, name: str) -> Application:
        cache: Dict[str, Application] = self.cache.setdefault(guild, {})
        if name.lower() not in cache.keys():
            raise ApplicationDoesNotExist("Application with that name does not exist.")
        app: "Application" = cache[name.lower()]
        return app

    @staticmethod
    async def get_response_from_application(app: Application, *, response: str) -> Response:
        async for resp in AsyncIter(app.responses):
            if resp.id == response:
                respo: Response = resp
                break
        else:
            raise commands.CheckFailure()
        return respo

    @staticmethod
    async def get_event_roles_from_application(
        app: Application, *, type: Events
    ) -> Optional[EventRoles]:
        return await discord.utils.get(AsyncIter(app.roles.events), type=type.lower())

    @staticmethod
    async def manage_event_roles(*, member: discord.Member, event: EventRoles) -> None:
        if event.mode.lower() == "add":
            if not event.roles:
                return
            with contextlib.suppress(discord.HTTPException):
                await member.add_roles(
                    *event.roles,
                    reason="[Applications] added '{0}' roles to {1.display_name} ({1.id})".format(
                        event.type.lower(), member
                    ),
                )
        elif event.mode.lower() == "remove":
            if not event.roles:
                return
            with contextlib.suppress(discord.HTTPException):
                await member.remove_roles(
                    *event.roles,
                    reason="[Applications] removed '{0}' roles from {1.display_name} ({1.id})".format(
                        event.type.lower(), member
                    ),
                )

    async def get_response(self, guild: int, *, name: str, response: str) -> Response:
        try:
            app: Application = await self.get_application(guild, name=name)
        except ApplicationDoesNotExist:
            raise commands.CheckFailure()
        return await self.get_response_from_application(app, response=response)

    async def get_all_applications(self, guild: int) -> List[Application]:
        cache: Dict[str, Application] = self.cache.setdefault(guild, {})
        return [app for app in cache.values()]

    async def create(self, guild: int, name: str, description: str, channel: int) -> Application:
        cache: Dict[str, Application] = self.cache.setdefault(guild, {})
        if name.lower() in cache.keys():
            raise DuplicateApplicationError("An application with this name already exists.")
        app: Application = Application.create_model(
            name=name, description=description, channel=channel
        )
        self.cache.setdefault(guild, {}).setdefault(name.lower(), app)
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app

    async def delete(self, guild: int, name: str) -> None:
        try:
            del self.cache[guild][name.lower()]
        except KeyError:
            try:
                async with self.config.guild_from_id(guild).apps() as apps:
                    del apps[name.lower()]
            except KeyError:
                raise ApplicationDoesNotExist("Application with that name does not exist.")

    async def edit_setting_for(
        self,
        guild: int,
        *,
        name: str,
        object: Literal["channel", "message", "color", "open", "cooldown", "dm"],
        value: Union[str, int, float, bool],
    ) -> Application:
        app: Application = await self.get_application(guild, name=name)
        setattr(app.settings, object, value)
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app

    async def edit_thread_settings(
        self,
        guild: int,
        *,
        name: str,
        toggle: bool,
        value: Optional[str] = None,
    ) -> Application:
        app: Application = await self.get_application(guild, name=name)
        if value is None:
            value: Optional[str] = app.settings.thread.custom
        thread: Threads = Threads(toggle=toggle, custom=value)
        setattr(app.settings, "thread", thread)
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app

    async def edit_notification_settings(
        self,
        guild: int,
        *,
        name: str,
        type: Literal["toggle", "content", "channel", "users", "roles", "everyone"],
        value: Union[str, bool],
    ) -> Application:
        app: Application = await self.get_application(guild, name=name)
        if type.lower() == "toggle":
            value: Union[str, bool] = converter._convert_to_bool(value)
            setattr(app.settings.notifications, type.lower(), value)
        elif type.lower() == "channel":
            channels: List[str] = str(value).split(",")
            for channel in channels:
                with contextlib.suppress(ValueError):
                    if int(channel) in app.settings.notifications.channels:
                        app.settings.notifications.channels.remove(int(channel))
                    else:
                        app.settings.notifications.channels.append(int(channel))
        elif type.lower() in ["users", "roles", "everyone"]:
            value: Union[str, bool] = converter._convert_to_bool(value)
            setattr(app.settings.notifications.mentions, type.lower(), value)
        else:
            setattr(app.settings.notifications, type.lower(), value)
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app

    async def edit_button_settings(
        self,
        guild: int,
        *,
        name: str,
        object: Literal["label", "emoji", "style"],
        value: Union[str, Styles, Literal[0], None],
    ) -> Application:
        app: Application = await self.get_application(guild, name=name)
        setattr(app.buttons, object, value)
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app

    async def toggle_tickets(self, guild: int, *, name: str, toggle: bool) -> Application:
        app: Application = await self.get_application(guild, name=name)
        app.tickets.toggle = toggle
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app

    async def question_add(
        self,
        guild: int,
        *,
        name: str,
        question: str,
        type: Literal["text", "boolean", "attachment", "choices"] = "text",
        required: bool = True,
        position: int = 0,
    ) -> Tuple[Application, Question]:
        cache: Dict[str, Application] = self.cache.setdefault(guild, {})
        if name.lower() not in cache.keys():
            raise ApplicationDoesNotExist("Application with that name does not exist.")
        app: "Application" = cache[name.lower()]
        if position < 0:
            raise NoQuestionsConfiguredError("Cannot have a position below 1.")
        if position > 1 and len(app.questions) < 1:
            raise NoQuestionsConfiguredError(
                "There are no questions configured in this application."
            )
        if len(app.questions) >= 10:
            raise TooManyQuestionsError(
                "An application can only have 10 questions attached to it."
            )
        ques: Question = Question(text=question, type=type, required=required)
        if type.lower() != "choices":
            if position == 0:
                app.questions.append(ques)
            else:
                app.questions.insert(position - 1, ques)
            async with self.config.guild_from_id(guild).apps() as apps:
                apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app, ques

    async def question_remove(
        self, guild: int, name: str, position: int
    ) -> Tuple[Application, Question]:
        cache: Dict[str, Application] = self.cache.setdefault(guild, {})
        if name.lower() not in cache.keys():
            raise ApplicationDoesNotExist("Application with that name does not exist.")
        app: "Application" = cache[name.lower()]
        if len(app.questions) < 1:
            raise NoQuestionsConfiguredError(
                "There are no questions configured in this application."
            )
        if position < 1 and len(app.questions) < position and position > 10:
            raise TooManyQuestionsError("Question does not exist in the application.")
        question: Question = app.questions[position - 1]
        app.questions.pop(position - 1)
        async with self.config.guild_from_id(guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        return app, question
