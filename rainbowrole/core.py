import logging
from typing import (
    Optional,
    Union,
)

import discord
from discord.ext import tasks
from redbot.core.bot import Red # type: ignore
from redbot.core import commands, Config # type: ignore

log: logging.Logger = logging.getLogger("red.seinacogs.rainbowrole")

COLORS = [
    (255, 62, 62),
    (255, 147, 62),
    (255, 215, 62),
    (133, 255, 62),
    (56, 255, 202),
    (56, 167, 255),
    (173, 56, 255),
    (243, 56, 255),
]

class RainbowRole(commands.Cog):
    """
    Create and manage a Rainbow Role in your server.
    """
    
    __version__ = "0.1.0"
    __author__ = "inthedark.org#0666"
    
    def __init__(
        self,
        bot: Red
    ):
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=759180080328081450, force_registration=True)
        self.log = logging.LoggerAdapter(log, {"version": self.__version__})
        
        default_guild = {
            "rainbow_role": None,
            "toggled": False,
        }
        
        self.config.register_guild(**default_guild)
        
        self.color = 0
        self.change_color.start()
        
    def format_help_for_context(self, ctx: commands.Context):
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{self.__author__}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)
    
    @tasks.loop(seconds=90.0)
    async def change_color(self):
        """
        The task that is responsible for the color change every x seconds.
        """
        for guild in self.bot.guilds:
            
            toggle = self.config.guild(guild).toggle()
            if not toggle:
                return
            
            rainbow_role = self.config.guild(guild).rainbow_role()
            if rainbow_role:
                try:
                    await rainbow_role.edit(
                        color=discord.Colour.from_rgb(
                            COLORS[self.color][0],
                            COLORS[self.color][1],
                            COLORS[self.color][2],
                        )
                    )
                except:
                    self.log.info("Oops! Something went wrong.", exc_info=True)
                    
        self.color = self.color + 1 if self.color + 1 <= 7 else 0
        
    @change_color.before_loop
    async def before_oscallha(self):
        await self.bot.wait_until_red_ready()
        
    def cog_unload(self):
        self.bot.loop.create_task(self.change_color.stop())
    
    @commands.group()
    @commands.guildowner_or_permissions(administrator=True)
    async def set(self, ctx: commands.Context):
        """Group commands for the rainbow role settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send_help("set")
    
    @set.command()
    @commands.guildowner_or_permissions(administrator=True)
    async def toggle(
        self, 
        ctx: commands.Context, 
        true_or_false: Optional[bool] = None
    ):
        """
        Toggle the rainbow role task.
        """
        if true_or_false is None:
            await ctx.send("The `true_or_false` option is a required argument.")
            
        await self.config.guild(ctx.guild).toggle(true_or_false)
        return await ctx.tick()
    
    @set.command()
    @commands.guildowner_or_permissions(administrator=True)
    async def role(
        self,
        ctx: commands.Context,
        role: Optional[Union[discord.Role, int]] = None,
    ):
        """
        Set your rainbow role using this command.
        """
        role = ctx.guild.get_role(getattr(role, "id", role))
        await self.config.guild(ctx.guild).rainbow_role.set(role.id) # type: ignore
        await ctx.tick()
        await ctx.send(f"Rainbow role set to `{role}`")
        