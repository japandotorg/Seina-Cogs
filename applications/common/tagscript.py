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

from typing import TYPE_CHECKING, Any, Callable, Dict, Final, List

import discord
import TagScriptEngine as tse
from redbot.core.utils.chat_formatting import box
from TagScriptEngine.interface import SimpleAdapter

if TYPE_CHECKING:
    from ..core import Applications
    from .models import Application, AppSettings, Response
    from .utils import GuildInteraction


TAGSCRIPT: Final[int] = 10_000


DEFAULT_SETTINGS_MESSAGE: Final[
    str
] = """
{embed({
    "title": "{settings(description)}",
    "color": "{settings(color)}",
    "description": "Fill this application to apply as a {settings(name)} in {guild(name)}.",
    "footer": {
        "text": "Click below to apply to this application!"
    },
    "fields": [
        {
            "name": "Response Count",
            "value": "{responses}",
            "inline": false
        }
    ]
})}
"""
DEFAULT_TICKET_MESSAGE: Final[
    str
] = """
{embed({
    "title": "{member(name)}'s Application Ticket!",
    "color": "{settings(color)}",
    "description": "Please wait patiently for the staff."
})}
"""
DEFAULT_NOTIFICATION_MESSAGE: Final[
    str
] = """
{embed({
    "description": "New application submitted by {member(name)} for application **{settings(name)}** with response id {id}",
    "color": "{settings(color)}"
})}
"""
DEFAULT_THREAD_NAME: Final[str] = "Response {id}"


BLOCKS: List[tse.Block] = [
    tse.MathBlock(),
    tse.RandomBlock(),
    tse.RangeBlock(),
    tse.StrfBlock(),
    tse.AssignmentBlock(),
    tse.FiftyFiftyBlock(),
    tse.LooseVariableGetterBlock(),
    tse.SubstringBlock(),
    tse.EmbedBlock(),
    tse.URLEncodeBlock(),
]


DEFAULT_ADAPTERS: Callable[  # noqa: E731
    [discord.Guild, discord.Member, "AppSettings"], Dict[str, tse.Adapter]
] = lambda guild, user, sett: {
    "user": tse.MemberAdapter(user),
    "member": tse.MemberAdapter(user),
    "guild": tse.GuildAdapter(guild),
    "server": tse.GuildAdapter(guild),
    "settings": SettingsAdapter(sett),
    "time": tse.StringAdapter(sett.time.strftime("%d:%m:%Y-%H:%M:%S")),
    "timestamp": tse.IntAdapter(sett.time.timestamp()),
}


async def threads(
    cog: "Applications",
    interaction: "GuildInteraction",
    *,
    app: "Application",
    response: "Response",
    default: str = DEFAULT_THREAD_NAME,
) -> Dict[str, Any]:
    adapters: Dict[str, tse.Adapter] = DEFAULT_ADAPTERS(
        interaction.guild, interaction.user, app.settings
    )
    adapters.update(
        **{
            "id": tse.StringAdapter(response.id),
        }
    )
    kwargs: Dict[str, Any] = await cog.manager.process_tagscript(
        app.settings.thread.custom, adapters, escape=(True, True)
    )
    if not kwargs:
        await cog.manager.edit_thread_settings(
            interaction.guild.id,
            name=app.name.lower(),
            toggle=True,
            value=default or DEFAULT_THREAD_NAME,
        )
        kwargs: Dict[str, Any] = await cog.manager.process_tagscript(
            default or DEFAULT_THREAD_NAME, adapters
        )
    return kwargs


async def notifications(
    cog: "Applications",
    interaction: "GuildInteraction",
    *,
    app: "Application",
    response: "Response",
    default: str = DEFAULT_NOTIFICATION_MESSAGE,
) -> Dict[str, Any]:
    adapters: Dict[str, tse.Adapter] = DEFAULT_ADAPTERS(
        interaction.guild, interaction.user, app.settings
    )
    adapters.update(
        **{
            "id": tse.StringAdapter(response.id),
            "app": SettingsAdapter(app.settings),
            "color": tse.StringAdapter(app.settings.color),
        }
    )
    kwargs: Dict[str, Any] = await cog.manager.process_tagscript(
        app.settings.notifications.content, adapters
    )
    if not kwargs:
        await cog.manager.edit_notification_settings(
            interaction.guild.id,
            name=app.settings.name.lower(),
            type="content",
            value=default or DEFAULT_NOTIFICATION_MESSAGE,
        )
        kwargs: Dict[str, Any] = await cog.manager.process_tagscript(
            default or DEFAULT_NOTIFICATION_MESSAGE, adapters
        )
    return kwargs


async def messages(
    cog: "Applications",
    interaction: "GuildInteraction",
    *,
    app: "Application",
    default: str = DEFAULT_SETTINGS_MESSAGE,
) -> Dict[str, Any]:
    adapters: Dict[str, tse.Adapter] = {
        "settings": SettingsAdapter(app.settings),
        "guild": tse.GuildAdapter(interaction.guild),
        "server": tse.GuildAdapter(interaction.guild),
        "responses": tse.IntAdapter(len(app.responses)),
    }
    kwargs: Dict[str, Any] = await cog.manager.process_tagscript(app.settings.message, adapters)
    if not kwargs:
        await cog.manager.edit_setting_for(
            interaction.guild.id,
            name=app.name.lower(),
            object="message",
            value=default or DEFAULT_SETTINGS_MESSAGE,
        )
        kwargs: Dict[str, Any] = await cog.manager.process_tagscript(
            default or DEFAULT_SETTINGS_MESSAGE, adapters
        )
    return kwargs


class SettingsAdapter(SimpleAdapter["AppSettings"]):
    def __init__(self, base: "AppSettings") -> None:
        super().__init__(base=base)

    def update_attributes(self) -> None:
        settings: "AppSettings" = self.object
        self._attributes.update(
            {
                "name": settings.name,
                "description": settings.description,
                "color": settings.color,
                "status": settings.open,
                "cooldown": settings.cooldown,
                "created": int(settings.created_at),
                "thread": "{}\n{}".format(
                    "Threads enabled" if settings.thread.toggle else "Threads disabled",
                    box(settings.thread.custom, lang="json"),
                ),
            }
        )

    def get_value(self, ctx: tse.Verb) -> str:
        should_escape: bool = False
        if ctx.parameter is None:
            return_value: str = self.object.name
        else:
            try:
                value: Any = self._attributes[ctx.parameter]
            except KeyError:
                return  # pyright: ignore[reportReturnType]
            if isinstance(value, tuple):
                value, should_escape = value
            return_value: str = (
                str(value) if value else None
            )  # pyright: ignore[reportAssignmentType]
        return tse.escape_content(return_value) if should_escape else return_value
