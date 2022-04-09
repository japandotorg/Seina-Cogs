import discord
from redbot.core import commands

from .tio import Tio

class Compiler(commands.Cog):
    """
    Runs code using the TIO api.
    """
    
    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"
    
    def __init__(self, bot):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: {humanize_list(self.__author__)}",
        ]
        return "\n".join(text)
    
    @commands.command(
        name = "compile",
        aliases = [
            "run"
        ]
    )
    async def execute_code(self, ctx, lang: str, *args):
        """
        Runs code in 600+ languages.
        
        `[p]compile <language> <code>` 
        
        PLEASE NOTE: due to discord.py limitations, 
        if you would like to run code that has double brackets - 
        " in it, you must type a \ flipped backslash in front of it.
        """
        query = " ".join(args[:])
        
        query = query.replace(("```" + lang), "")
        
        if lang == "python3":
            query = query.replace('"', "'")
            query = query.replace("```python", "")
            
        query = query.replace("`", "")
        query = query.strip()
        query = query.replace("\\n", ";")
        
        site = Tio()
        request = site.new_request(lang, query)
        
        embed = discord.Embed(
            title=f"{lang} code evaluation",
            color=await ctx.embed_color(),
        )
        embed.add_field(name="**Result**", value=site.send(request))
        embed.set_footer(text="Powered by TIO.RUN")
        
        await ctx.send(embed=embed)
