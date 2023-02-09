import re
from io import BytesIO
from typing import Any, Dict, Final, List, Pattern

import discord
import molmass  # type: ignore
from redbot.core import commands  # type: ignore
from redbot.core.bot import Red  # type: ignore


class Chemistry(commands.Cog):
    """
    Chemistry inside discord >.<
    """

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.1"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Any = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    @commands.command(name="molarmass", aliases=["molar", "mm"])
    async def _molar_mass(self, ctx: commands.Context, *, formula) -> None:
        """
        Calculates the molar mass of a chemical formula.
        """
        try:
            mass_pattern: Pattern[str] = re.compile(r"mass: (\S+)\n")
            mass_analyzed: str = molmass.analyze(formula)
            avg, mono, nom, mean = re.findall(mass_pattern, mass_analyzed)

            embed: discord.Embed = discord.Embed(
                title=f"Molar mass for {formula} (in g/mol)",
                description=(
                    f"Average mass: `{avg}`\n"
                    f"Monoisotopic mass: `{mono}`\n"
                    f"Nominal mass: `{nom}`\n"
                    f"Mean mass: `{mean}`"
                ),
                color=await ctx.embed_color(),
            )

            await ctx.send(embed=embed)

        except (TypeError, IndexError, ValueError):
            await ctx.send("This does not appear to be a valid Chemical. Please check your input.")
