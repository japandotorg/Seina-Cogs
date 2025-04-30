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
from typing import Any, Dict, List, Union

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.views import (
    _NavigateButton,
    _SimplePageSource,
    _StopButton,
)

from .constants import NavigationEmojis


class EmojiMenu(discord.ui.View):
    def __init__(
        self, pages: List[Union[str, discord.Embed]], timeout: float = 120.0
    ) -> None:
        super().__init__(timeout=timeout)
        self._source: _SimplePageSource = _SimplePageSource(items=pages)
        self.current_page: int = 0

        self.ctx: commands.Context = discord.utils.MISSING
        self._message: discord.Message = discord.utils.MISSING

        self.force_left_button: _NavigateButton = _NavigateButton(
            discord.ButtonStyle.grey,
            NavigationEmojis.FORCE_LEFT_ARROW,
            direction=0,
        )
        self.left_button: _NavigateButton = _NavigateButton(
            discord.ButtonStyle.grey, NavigationEmojis.LEFT_ARROW, direction=-1
        )
        self.cancel_button: _StopButton = _StopButton(
            discord.ButtonStyle.red, NavigationEmojis.CANCEL
        )
        self.right_button: _NavigateButton = _NavigateButton(
            discord.ButtonStyle.grey, NavigationEmojis.RIGHT_ARROW, direction=1
        )
        self.force_right_button: _NavigateButton = _NavigateButton(
            discord.ButtonStyle.grey,
            NavigationEmojis.FORCE_RIGHT_ARROW,
            direction=self.source.get_max_pages(),
        )
        if self.source.is_paginating():
            self.add_item(self.force_left_button)
            self.add_item(self.left_button)
            self.add_item(self.cancel_button)
            self.add_item(self.right_button)
            self.add_item(self.force_right_button)

    @property
    def source(self) -> _SimplePageSource:
        return self._source

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True  # pyright: ignore[reportAttributeAccessIssue]

        if self._message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)

    async def interaction_check(
        self, interaction: discord.Interaction[Red]
    ) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You're not allowed to use this button.", ephemeral=True
            )
            return False
        return True

    async def get_page(self, number: int) -> Dict[str, Any]:
        try:
            page: List[Union[str, discord.Embed]] = await self.source.get_page(
                number
            )
        except IndexError:
            self.current_page: int = 0
            page: List[Union[str, discord.Embed]] = await self.source.get_page(
                self.current_page
            )
        value: Union[str, discord.Embed] = await self.source.format_page(
            self, page
        )
        ret: Dict[str, Any] = {"view": self}
        if isinstance(value, dict):
            ret.update(value)  # pyright: ignore[reportCallIssue]
        elif isinstance(value, str):
            ret.update({"content": value, "embed": None})
        elif isinstance(value, discord.Embed):  # pyright: ignore[reportUnnecessaryIsInstance]
            ret.update({"embed": value, "content": None})
        return ret

    async def start(
        self, ctx: commands.Context, ephemeral: bool = False
    ) -> None:
        self.ctx: commands.Context = ctx
        kwargs: Dict[str, Any] = await self.get_page(self.current_page)
        self._message: discord.Message = await ctx.send(
            **kwargs, ephemeral=ephemeral
        )
