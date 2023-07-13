import functools
from typing import Any, Dict, List, Optional, Union

import discord


class BaseLanguageOptions:
    def __init__(self) -> None:
        self._options: List[discord.SelectOption] = [
            discord.SelectOption(
                label="Bengali", description="Get Bengali translation of this question."
            ),
            discord.SelectOption(
                label="German", description="Get German translation of this question."
            ),
            discord.SelectOption(
                label="Spanish", description="Get Spanish translation of this question."
            ),
            discord.SelectOption(
                label="French", description="Get French translation of this question."
            ),
            discord.SelectOption(
                label="Hindi", description="Get Hindi translation of this question."
            ),
            discord.SelectOption(
                label="Filipino", description="Get Filipino translation of this question."
            ),
        ]

    def _get_options(self) -> List[discord.SelectOption]:
        return self._options


class Select(discord.ui.Select):
    def __init__(
        self,
        callback: Any,
    ) -> None:
        options = BaseLanguageOptions()._get_options()
        super().__init__(
            placeholder="Translations",
            options=options,
            max_values=1,
            min_values=1,
        )
        self.callback = functools.partial(callback, self)


class CGView(discord.ui.View):
    def __init__(
        self,
        result: Dict[str, Union[str, Dict[str, str]]],
        color: Union[int, discord.Color],
        timeout: float = 120.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self._result: Dict[str, Union[str, Dict[str, str]]] = result
        self._color: Union[int, discord.Color] = color
        self._message: Optional[discord.Message] = None

        self.add_item(Select(self._callback))

    async def on_timeout(self) -> None:
        for item in self.children:
            item: discord.ui.Item
            item.disabled = True  # type: ignore
        try:
            await self._message.edit(view=self)  # type: ignore
        except discord.HTTPException:
            pass

    @staticmethod
    async def _callback(self: Select, interaction: discord.Interaction) -> None:  # type: ignore
        await interaction.response.defer()
        if self.values[0] == "Bengali":
            embed: discord.Embed = discord.Embed(
                description=self.view._result["translations"]["bn"],  # type: ignore
                color=self.view._color,  # type: ignore
            )
            embed.set_footer(
                text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
            )
            await interaction.edit_original_response(embed=embed)
        elif self.values[0] == "German":
            embed: discord.Embed = discord.Embed(
                description=self.view._result["translations"]["de"],  # type: ignore
                color=self.view._color,  # type: ignore
            )
            embed.set_footer(
                text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
            )
            await interaction.edit_original_response(embed=embed)
        elif self.values[0] == "Spanish":
            embed: discord.Embed = discord.Embed(
                description=self.view._result["translations"]["es"],  # type: ignore
                color=self.view._color,  # type: ignore
            )
            embed.set_footer(
                text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
            )
            await interaction.edit_original_response(embed=embed)
        elif self.values[0] == "French":
            embed: discord.Embed = discord.Embed(
                description=self.view._result["translations"]["fr"],  # type: ignore
                color=self.view._color,  # type: ignore
            )
            embed.set_footer(
                text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
            )
            await interaction.edit_original_response(embed=embed)
        elif self.values[0] == "Hindi":
            embed: discord.Embed = discord.Embed(
                description=self.view._result["translations"]["hi"],  # type: ignore
                color=self.view._color,  # type: ignore
            )
            embed.set_footer(
                text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
            )
            await interaction.edit_original_response(embed=embed)
        elif self.values[0] == "Filipino":
            embed: discord.Embed = discord.Embed(
                description=self.view._result["translations"]["tl"],  # type: ignore
                color=self.view._color,  # type: ignore
            )
            embed.set_footer(
                text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
            )
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.followup.send("Unrecognized option!", ephemeral=True)
