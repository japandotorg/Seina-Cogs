import functools
from typing import Callable, Dict, List, Optional, Union

import discord
from redbot.core import commands
from redbot.core.bot import Red


class BaseLanguageOptions:
    def __init__(self) -> None:
        self._options: List[discord.SelectOption] = [
            discord.SelectOption(
                label="English", description="Get English translation of this question."
            ),
            discord.SelectOption(
                label="Bengali",
                description="Get Bengali translation of this question.",
                value="bn",
            ),
            discord.SelectOption(
                label="German", description="Get German translation of this question.", value="de"
            ),
            discord.SelectOption(
                label="Spanish",
                description="Get Spanish translation of this question.",
                value="es",
            ),
            discord.SelectOption(
                label="French", description="Get French translation of this question.", value="fr"
            ),
            discord.SelectOption(
                label="Hindi", description="Get Hindi translation of this question.", value="hi"
            ),
            discord.SelectOption(
                label="Filipino",
                description="Get Filipino translation of this question.",
                value="tl",
            ),
        ]

    def _get_options(self) -> List[discord.SelectOption]:
        return self._options


class Select(discord.ui.Select):
    def __init__(
        self,
        callback: Callable[["Select", discord.Interaction], None],
    ) -> None:
        options: List[discord.SelectOption] = BaseLanguageOptions()._get_options()
        super().__init__(
            placeholder="Translations",
            options=options,
            max_values=1,
            min_values=1,
        )
        self.callback: functools.partial = functools.partial(callback, self)


class CGView(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        result: Dict[str, Union[str, Dict[str, str]]],
        member: Optional[discord.Member] = None,
        timeout: Optional[float] = 120.0,
    ) -> None:
        super().__init__(timeout=timeout)
        self._ctx: commands.Context = ctx
        self._result: Dict[str, Union[str, Dict[str, str]]] = result
        self._member: Optional[discord.Member] = member
        self._message: Optional[discord.Message] = None

        self.add_item(Select(self._callback))  # type: ignore

    async def on_timeout(self) -> None:
        for item in self.children:
            item: discord.ui.Item
            item.disabled = True  # type: ignore
        try:
            await self._message.edit(view=self)  # type: ignore
        except discord.HTTPException:
            pass

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if (
            self._member.id != interaction.user.id
            if self._member is not None
            else self._ctx.author.id != interaction.user.id
        ):
            await interaction.response.send_message(
                "You are not allowed to use this interaction", ephemeral=True
            )
            return False
        return True

    @staticmethod
    async def _callback(self: Select, interaction: discord.Interaction[Red]) -> None:  # type: ignore
        await interaction.response.defer()
        title = (
            f"{self.view._ctx.author} asked {self.view._member}"  # type: ignore
            if self.view._member is not None  # type: ignore
            else None
        )
        embed: discord.Embed = discord.Embed(
            title=title,
            description=self.view._result["question"] if self.values[0] == "English" else self.view._result["translations"][self.values[0]],  # type: ignore
            color=await self.view._ctx.embed_color(),  # type: ignore
        )
        embed.set_footer(
            text=f"Rating: {self.view._result['rating']} | ID: {self.view._result['id']}"  # type: ignore
        )
        await interaction.edit_original_response(embed=embed)
