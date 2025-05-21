"""
MIT License

Copyright (c) 2023-present japandotorg

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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import discord
from redbot.core import commands
from redbot.core.bot import Red

if TYPE_CHECKING:
    from .core import AFK


def disable_items(self: discord.ui.View):
    for child in self.children:
        child: discord.ui.Item
        if hasattr(child, "disabled") and not (
            isinstance(child, discord.ui.Button) and child.style == discord.ButtonStyle.url
        ):
            child.disabled = True  # type: ignore


class CloseButton(discord.ui.Button):
    def __init__(self) -> None:
        super().__init__(style=discord.ButtonStyle.red, label="Close")

    async def callback(self, _: discord.Interaction[Red], /) -> None:
        await self.view._message.delete()  # type: ignore
        self.view.stop()  # type: ignore


class AFKView(discord.ui.View):
    def __init__(
        self, ctx: commands.Context, cog: "AFK", data: Dict, timeout: float = 60.0
    ) -> None:
        super().__init__(timeout=timeout)
        self.ctx: commands.Context = ctx
        self.cog: "AFK" = cog
        self.data: Dict = data
        self._message: Optional[discord.Message] = None
        self.add_item(CloseButton())

    async def on_timeout(self) -> None:
        try:
            await self._message.delete()  # type: ignore
        except discord.HTTPException:
            pass

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        if self.ctx.author.id != interaction.user.id:
            await interaction.response.send_message(
                "You're not allowed to interact with this message.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Show Pings", style=discord.ButtonStyle.green)
    async def _callback(self, interaction: discord.Interaction[Red], _: discord.ui.Button, /):
        if len(self.data["pings"]) == 0:
            return await interaction.response.send_message(
                "You did not recieve any pings while you were AFK!",
                ephemeral=True,
            )
        else:
            await self.cog._ping_list(interaction, self.data)


class ViewDisableOnTimeout(discord.ui.View):
    def __init__(self, **kwargs: Any) -> None:
        self.message: Optional[discord.Message] = None
        self.ctx: commands.Context = kwargs.pop("ctx", None)
        self.timeout_message: str = kwargs.pop("timeout_message", None)
        super().__init__(**kwargs)

    async def on_timeout(self) -> None:
        if self.message:
            disable_items(self)
            await self.message.edit(view=self)
            if self.timeout_message and self.ctx:
                await self.ctx.send(self.timeout_message)

        self.stop()


class PaginatorButton(discord.ui.Button):
    def __init__(
        self,
        *,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        label: Optional[str] = None,
    ) -> None:
        super().__init__(style=discord.ButtonStyle.green, label=label, emoji=emoji)


class ForwardButton(PaginatorButton):
    def __init__(self, emoji: Optional[str] = "▶️") -> None:
        super().__init__(emoji=emoji)

    async def callback(self, interaction: discord.Interaction[Red], /) -> None:
        if self.view.index == len(self.view.contents) - 1:  # type: ignore
            self.view.index = 0  # type: ignore
        else:
            self.view.index += 1  # type: ignore

        await self.view.edit_message(interaction)  # type: ignore


class BackwardButton(PaginatorButton):
    def __init__(self, emoji: Optional[str] = "◀️") -> None:
        super().__init__(emoji=emoji)

    async def callback(self, interaction: discord.Interaction[Red], /) -> None:
        if self.view.index == 0:  # type: ignore
            self.view.index = len(self.view.contents) - 1  # type: ignore
        else:
            self.view.index -= 1  # type: ignore

        await self.view.edit_message(interaction)  # type: ignore


class LastItemButton(PaginatorButton):
    def __init__(self, emoji: Optional[str] = "⏩") -> None:
        super().__init__(emoji=emoji)

    async def callback(self, interaction: discord.Interaction[Red], /) -> None:
        self.view.index = len(self.view.contents) - 1  # type: ignore

        await self.view.edit_message(interaction)  # type: ignore


class FirstItemButton(PaginatorButton):
    def __init__(self, emoji: Optional[str] = "⏪") -> None:
        super().__init__(emoji=emoji)

    async def callback(self, interaction: discord.Interaction[Red], /) -> None:
        self.view.index = 0  # type: ignore

        await self.view.edit_message(interaction)  # type: ignore


class PageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.gray, disabled=True)

    def _change_label(self):
        self.label = f"Page {self.view.index + 1}/{len(self.view.contents)}"  # type: ignore


class PaginatorSelect(discord.ui.Select):
    def __init__(self, *, placeholder: str = "Select an item:", length: int):
        options = [
            discord.SelectOption(
                label=f"{i+1}",
                value=i,  # type: ignore
                description=f"Go to page {i+1}",
            )
            for i in range(length)
        ]
        super().__init__(options=options, placeholder=placeholder)

    async def callback(self, interaction: discord.Interaction[Red], /) -> None:
        self.view.index = int(self.values[0])  # type: ignore

        await self.view.edit_message(interaction)  # type: ignore


class AFKPaginator(ViewDisableOnTimeout):
    def __init__(
        self,
        context: commands.Context,
        contents: Union[List[str], List[discord.Embed]],
        interaction: discord.Interaction[Red],
        timeout: Optional[int] = 60,
        use_select: Optional[bool] = False,
    ) -> None:
        super().__init__(timeout=timeout, ctx=context, timeout_message=None)

        self.ctx = context
        self.contents = contents
        self.interaction = interaction
        self.use_select = use_select
        self.index = 0

        if not all(isinstance(x, discord.Embed) for x in contents) and not all(
            isinstance(x, str) for x in contents
        ):
            raise TypeError("All pages must be of the same type. Either a string or an embed.")

        if self.use_select and len(self.contents) > 1:
            self.add_item(PaginatorSelect(placeholder="Select a page:", length=len(contents)))

        buttons_to_add = (
            [FirstItemButton, BackwardButton, PageButton, ForwardButton, LastItemButton]
            if len(self.contents) > 2
            else [BackwardButton, PageButton, ForwardButton] if not len(self.contents) == 1 else []
        )
        for i in buttons_to_add:
            self.add_item(i())

        self.update_items()

    def update_items(self) -> None:
        for i in self.children:
            if isinstance(i, PageButton):
                i._change_label()
                continue

            elif self.index == 0 and isinstance(i, FirstItemButton):
                i.disabled = True
                continue

            elif self.index == len(self.contents) - 1 and isinstance(i, LastItemButton):
                i.disabled = True
                continue

            i.disabled = False  # type: ignore

    async def start(self) -> None:
        if isinstance(self.contents[self.index], discord.Embed):
            embed = self.contents[self.index]
            content = ""
        elif isinstance(self.contents[self.index], str):
            embed = None
            content = self.contents[self.index]
        await self.interaction.response.send_message(
            content=content, embed=embed, view=self, ephemeral=True  # type: ignore
        )
        self.message = await self.interaction.original_response()

    async def edit_message(self, inter: discord.Interaction[Red], /) -> None:
        if isinstance(self.contents[self.index], discord.Embed):
            embed = self.contents[self.index]
            content = ""
        elif isinstance(self.contents[self.index], str):
            embed = None
            content = self.contents[self.index]

        self.update_items()
        await inter.response.edit_message(content=content, embed=embed, view=self)  # type: ignore
