import re
import molmass # type: ignore

import discord
from redbot.core.bot import Red # type: ignore
from redbot.core import commands # type: ignore

class Chemistry(commands.Cog):
    """
    Chemistry inside discord >.<
    """
    
    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"
    
    def __init__(self, bot: Red):
        self.bot: Red = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return

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
    async def _molar_mass(self, ctx: commands.Context, *, formula):
        """
        Calculates the molar mass of a chemical formula.
        """
        try:
            mass_pattern = re.compile(r"mass: (\S+)\n")
            mass_analyzed = molmass.analyze(formula)
            avg, mono, nom, mean = re.findall(mass_pattern, mass_analyzed)
            
            embed: discord.Embed = discord.Embed(
                title=f"Molar mass for {formula} (in g/mol)",
                description=(
                    f"Average mass: `{avg}`\n"
                    f"Monoisotopic mass: `{mono}`\n"
                    f"Nominal mass: `{nom}`\n"
                    f"Mean mass: `{mean}`"
                ),
                color=await ctx.embed_color()
            )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            await ctx.send("This does not appear to be a valid Chemical. Please check your input.")
            