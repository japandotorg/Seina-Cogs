"""
MIT License

Copyright (c) 2022-present japandotorg

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

from __future__ import annotations

import io
import aiohttp
import logging
from tabulate import tabulate
from typing import Literal, Union, Dict, Any
from playwright.async_api import async_playwright

import discord
from pygicord import Paginator
from redbot.core.bot import Red # type: ignore
from redbot.core import commands, Config # type: ignore
from redbot.core.i18n import Translator, cog_i18n # type: ignore

BaseCog = getattr(commands, "Cog", object)

log: logging.Logger = logging.getLogger("red.seinacogs.tools")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

_: Translator = Translator("SeinaTools", __file__)

@cog_i18n(_)
class SeinaTools(BaseCog):
    """
    Owner configuration tools for [botname].
    """
    
    __author__ = "inthedark.org#0666"
    __version__ = "0.1.0"
    
    def __init__(self, bot: Red):
        self.bot: Red = bot
        
        self.config: Config = Config.get_conf(
            self, identifier=666, force_registration=True
        )
        
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        
        default_global = {
            "embed": False
        }
        self.config.register_global(**default_global)
        
    async def red_get_data_for_user(self, *, user_id: int):
        """
        Nothing to get.
        """
        return {}
        
    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int):
        """
        Nothing to delete.
        """
        return {}
    
    def format_help_for_context(self, ctx: commands.Context):
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{self.__author__}**",
            f"Cog Version: **{self.__cog_version__}**"
        ]
        return "\n".join(text)
    
    async def _seinatools_error(self, ctx: commands.Context, error):
        if error.__cause__:
            cause = error.__cause__
            log.exception(f"SeinaTools :: Errored :: \n{error}\n{cause}\n")
        else:
            cause = error
            log.exception(f"SeinaTools :: Errored :: \n{cause}\n")
            
    @commands.is_owner()
    @commands.command(name="spy")
    async def _spy(
        self,
        ctx: commands.Context,
        guild: Union[discord.Guild, int] = None,
        channel_member: str = None,
    ):
        """
        Yet another fun spy command.
        """
        guild = guild or ctx.guild
        channel_member = channel_member or "members"
        
        URL = "https://discord.com/api/guilds/{guild.id if isinstance(guild, discord.Guild) else guild}/widget.json"
        data = await self.session.get(URL)
        
        json: Dict[str, typing.Any] = await data.json()
        
        if "message" in json:
            return await ctx.reply(f"{ctx.author.mention} can not spy that server.")
        
        name = json["name"]
        id_ = json["id"]
        instant_invite = json["instant_invite"]
        presence_count = json["presence_count"]
        
        embed: discord.Embed = discord.Embed(
            title=name,
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at,
        )
        
        if instant_invite:
            embed.url = instant_invite
            
        embed.set_footer(text=f"{id_}")
        embed.description = f"**Presence Count:** {presence_count}"
        
        embed_list = [embed]
        
        for channel in json["channels"]:
            embed_chan = discord.Embed(
                title=channel["name"],
                description=f"**Position:** {channel['position']}",
                color=ctx.author.color,
                timestamp=ctx.message.created_at,
            ).set_footer(text=channel["id"])

            embed_list.append(embed_chan)
            
        embed_list_member = [embed]
        
        for member in json["members"]:
            id_ = member["id"]
            username = member["username"]
            discriminator = member["discriminator"]
            avatar_url = member["avatar_url"]
            status = member["status"]
            vc = member["channel_id"] if "channel_id" in member else None
            suppress = member["suppress"] if "suppress" in member else None
            self_mute = member["self_mute"] if "self_mute" in member else None
            self_deaf = member["self_deaf"] if "self_deaf" in member else None
            deaf = member["deaf"] if "deaf" in member else None
            mute = member["mute"] if "mute" in member else None

            em = (
                discord.Embed(
                    title=f"Username: {username}#{discriminator}",
                    color=ctx.author.color,
                    timestamp=ctx.message.created_at,
                )
                .set_footer(text=f"{id_}")
                .set_thumbnail(url=avatar_url)
            )
            em.description = f"**Status:** {status.upper()}\n**In VC?** {bool(vc)} ({f'<#{str(vc)}>' if vc else None})"
            
        if vc:
            em.add_field(name="VC Channel ID", value=str(vc), inline=True)
            em.add_field(name="Suppress?", value=suppress, inline=True)
            em.add_field(name="Self Mute?", value=self_mute, inline=True)
            em.add_field(name="Self Deaf?", value=self_deaf, inline=True)
            em.add_field(name="Deaf?", value=deaf, inline=True)
            em.add_field(name="Mute?", value=mute, inline=True)
            
        embed_list_member.append(em)
        
        if channel_member.lower() in ("channels",):
            paginator = Paginator(pages=embed_list)
            await paginator.start(ctx=ctx)
        elif channel_member.lower() in ("members",):
            paginator = Paginator(pages=embed_list_member)
            await paginator.start(ctx=ctx)
        else:
            return
        
    @commands.is_owner()
    @commands.group(name="botstatset")
    async def _botstatset(self, ctx: commands.Context):
        """
        Settings for the botstat command.
        """
        pass
    
    @commands.is_owner()
    @_botstatset.command(name="embed")
    async def _embed(self, ctx: commands.Context, true_or_false: bool):
        """
        Toggle whether botstats should use embeds.
        """
        await self.config.embed.set(true_or_false)
        return await ctx.tick()
        
    @commands.is_owner()
    @commands.command(name="botstat")
    async def _botstat(self, ctx: commands.Context):
        """
        Yet another botstat command for [botname].
        """
        table = tabulate(
            (
                ("Guilds", len(self.bot.guilds)),
                ("Channels", len(tuple(self.bot.get_all_channels()))),
                ("Users", sum(len(i.members) for i in self.bot.guilds)),
                ("DMs", len(self.bot.private_channels)),
                ("Latency", str(round(self.bot.latency * 1000, 2)) + "ms"),
                ("Cogs", len(self.bot.cogs)),
                ("Commands", len(tuple(self.bot.walk_commands())))
            ),
            tablefmt="fancy_grid",
        )
        
        embedded = await self.config.embed()
        
        if embedded:
            return await ctx.send(
                embed=discord.Embed(
                    title=f"{ctx.me.name} Stats",
                    description=table,
                    color=await ctx.embed_color(),
                )
            )
        else:
            return await ctx.send(table)
        
    @commands.is_owner()
    @commands.command(name="screenshot", aliases=["ss"])
    async def _screenshot(self, ctx: commands.Context, url: str, wait: Optional[int] = None):
        """
        Screenshots a given url directly inside discord.
        """
        async with ctx.typing():
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(channel="chrome")
                
                page = await browser.new_page(
                    color_scheme="dark",
                    screen={
                        "width": 1920,
                        "height": 1080,
                    },
                    viewport={
                        "width": 1920,
                        "height": 1080,
                    }
                )
                
                await page.goto(url)
                
                if wait != None:
                    await page.wait_for_timeout(wait)
                    
                img_bytes = await page.screenshot()
        
                file_ = io.BytesIO(img_bytes)
                file_.seek(0)
                file = discord.File(file_, "screenshot.png")
                file_.close()
        
        await ctx.send(file=file)
