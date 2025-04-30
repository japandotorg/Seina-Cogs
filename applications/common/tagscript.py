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

from typing import TYPE_CHECKING, Any, Final, List

import TagScriptEngine as tse
from TagScriptEngine.interface import SimpleAdapter

if TYPE_CHECKING:
    from .models import AppSettings


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
    "description": "New application submitted by {member(name)} for application **{app}** with response id {id}",
    "color": "{color}"
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
