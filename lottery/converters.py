from typing import TYPE_CHECKING, Dict, List, Union, cast

import discord
from redbot.core import app_commands, commands
from redbot.core.bot import Red

if TYPE_CHECKING:
    from .core import Lottery


if TYPE_CHECKING:
    RoleOrUserConverter = Union[discord.Role, discord.Member]
else:

    class RoleOrUserConverter(commands.Converter[Union[discord.Role, discord.Member]]):
        @classmethod
        async def convert(
            cls, ctx: commands.GuildContext, argument: str
        ) -> Union[discord.Role, discord.Member]:
            try:
                obj: Union[discord.Role, discord.Member] = await commands.RoleConverter().convert(
                    ctx, argument
                )
            except commands.RoleNotFound:
                try:
                    obj: Union[discord.Role, discord.Member] = (
                        await commands.MemberConverter().convert(ctx, argument)
                    )
                except commands.MemberNotFound:
                    raise commands.BadArgument(
                        "Could not find user or role with argument '{}'.".format(argument)
                    )
                else:
                    return obj
            else:
                return obj


class LotteryTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction[Red], value: str) -> str:
        cog: "Lottery" = cast("Lottery", interaction.client.get_cog("Lottery"))
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = (
            await cog.manager.get_guild(interaction.guild)
        )
        if value.lower() not in config:
            await interaction.response.send_message(
                "No lottery with name `{}` exists.".format(value.lower())
            )
            raise app_commands.UserFeedbackCheckFailure()
        return value.lower()

    async def autocomplete(
        self, interaction: discord.Interaction[Red], value: str
    ) -> List[app_commands.Choice[str]]:
        cog: "Lottery" = cast("Lottery", interaction.client.get_cog("Lottery"))
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = (
            await cog.manager.get_guild(interaction.guild)
        )
        return [
            app_commands.Choice(name=name, value=name)
            for name in list(config.keys())
            if value.lower() in name.lower()
        ][:25]
