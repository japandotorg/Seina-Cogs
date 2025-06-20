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
import datetime
import uuid
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    TypeAlias,
)

from pydantic import BaseModel
from pydantic.fields import Field

from .tagscript import (
    DEFAULT_NOTIFICATION_MESSAGE,
    DEFAULT_SETTINGS_MESSAGE,
    DEFAULT_THREAD_NAME,
    DEFAULT_TICKET_MESSAGE,
)

if TYPE_CHECKING:
    from .utils import TypedConfig


Styles: TypeAlias = Literal[
    "green",
    "success",
    "red",
    "danger",
    "gray",
    "grey",
    "secondary",
    "blurple",
    "primary",
]
Status: TypeAlias = Literal["idle", "accepted", "rejected"]
Events: TypeAlias = Literal["apply", "submit", "accept", "deny"]
Types: TypeAlias = Literal["text", "boolean", "choices"]


class Threads(BaseModel):
    toggle: bool = Field(default=True)
    custom: str = Field(default=DEFAULT_THREAD_NAME)


class Mentions(BaseModel):
    users: bool = Field(default=True)
    roles: bool = Field(default=False)
    everyone: bool = Field(default=False)


class Notifications(BaseModel):
    toggle: bool = Field(default=True)
    content: str = Field(default=DEFAULT_NOTIFICATION_MESSAGE)
    mentions: Mentions = Field(default_factory=lambda: Mentions())
    channels: List[int] = Field(default_factory=list)


class AppSettings(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=20)]
    description: Annotated[str, Field(min_length=1, max_length=120)]
    channel: Annotated[int, Field()]
    message: str = Field(default=DEFAULT_SETTINGS_MESSAGE)
    color: str = Field(default="#2f3136")
    open: bool = Field(default=True)
    cooldown: int = Field(default=0, lt=4320)  # minutes
    dm: bool = Field(default=False)
    thread: Threads = Field(default_factory=lambda: Threads())
    notifications: Notifications = Field(default_factory=lambda: Notifications())
    created_at: float = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).timestamp()
    )

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.created_at)


class EventRoles(BaseModel):
    type: Events
    mode: Literal["add", "remove"]
    roles: List[int] = Field(default_factory=list)


class Roles(BaseModel):
    blacklist: List[int] = Field(default_factory=list)
    whitelist: List[int] = Field(default_factory=list)
    events: List[EventRoles] = Field(default_factory=list)


class Tickets(BaseModel):
    category: Optional[int] = Field(default=None)
    message: str = Field(default=DEFAULT_TICKET_MESSAGE)  # fill later
    toggle: bool = Field(default=False)


class ChoiceButtonType(BaseModel):
    label: Optional[str] = Field(default=None)
    emoji: Optional[str] = Field(default=None)


class ChoiceButtons(BaseModel):
    yes: ChoiceButtonType = Field(
        default_factory=lambda: ChoiceButtonType(
            emoji="\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16}"
        )
    )
    no: ChoiceButtonType = Field(default_factory=lambda: ChoiceButtonType(emoji="\N{CROSS MARK}"))
    required: bool = Field(default=False)


class Buttons(BaseModel):
    label: Optional[str] = Field(default=None)
    emoji: str = Field(default="\N{TICKET}")
    style: Styles = Field(default="green")
    choice: ChoiceButtons = Field(default_factory=lambda: ChoiceButtons())


class Post(BaseModel):
    id: Annotated[int, Field()]
    channel: Annotated[int, Field()]


class Answer(BaseModel):
    question: Annotated[str, Field()]
    type: Types
    answer: Annotated[str, Field()]


class Response(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    user: Annotated[int, Field()]
    answers: List[Answer] = Field(default_factory=list)
    status: Status = Field(default="idle")
    created_at: float = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).timestamp()
    )
    ticket: Optional[int] = Field(default=None)
    mod: Optional[int] = Field(default=None)

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.created_at)


class Question(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=500)]
    type: Types = Field(default="text")
    required: bool = Field(default=True)
    choices: List[str] = Field(default_factory=list)
    other: bool = Field(default=False)


class Application(BaseModel):
    settings: AppSettings
    questions: List[Question] = Field(default_factory=list)
    roles: Roles = Field(default_factory=lambda: Roles())
    tickets: Tickets = Field(default_factory=lambda: Tickets())
    buttons: Buttons = Field(default_factory=lambda: Buttons())
    posts: List[Post] = Field(default_factory=list)
    responses: List[Response] = Field(default_factory=list)

    def __str__(self) -> str:
        return self.name

    def __len__(self) -> int:
        return len(self.responses)

    @property
    def name(self) -> str:
        return self.settings.name

    @property
    def description(self) -> str:
        return self.settings.description

    @classmethod
    def create_model(cls, *, name: str, description: str, channel: int) -> "Application":
        return cls(
            settings=AppSettings(
                name=name,
                description=description,
                channel=channel,
            ),
        )

    @classmethod
    async def from_json(cls, data: Annotated["TypedConfig", Dict[str, Any]]) -> "Application":
        return await asyncio.to_thread(cls.model_validate, data, strict=True)
