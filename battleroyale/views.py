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

import typing

import discord
from redbot.core import commands


__all__ = ("JoinGameView",)


class JoinGameView(discord.ui.View):
    def __init__(self, cog: commands.Cog, ctx: commands.Context, timeout: float = 120) -> None:
        self.cog: commands.Cog = cog
        self.ctx: commands.Context = ctx

        self.players: typing.List[discord.Member] = []

        super().__init__(timeout=timeout)
        self._message: discord.Message = None

    async def on_timeout(self) -> None:
        for item in self.children:
            item: discord.ui.Item
            item.disabled = True
        try:
            await self._message.edit(view=self)
        except discord.HTTPException:
            pass

    @discord.ui.button(label="Join Game", emoji="⚔", style=discord.ButtonStyle.danger)
    async def _callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if len(self.players) > 200:
            return await interaction.response.send_message(
                "The maximum number of 200 players has been reached.",
                ephemeral=True,
            )
        elif interaction.user in self.players:
            return await interaction.response.send_message(
                "You have already joined this game!",
                ephemeral=True,
            )
        else:
            self.players.append(interaction.user)
            await interaction.response.send_message(
                "You have joined this game!",
                ephemeral=True,
            )
