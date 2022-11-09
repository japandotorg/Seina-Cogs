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
import logging
import shlex
import subprocess
import sys
from typing import Any, Dict, Literal, Optional, Union

import aiohttp
import discord
from playwright.async_api import async_playwright  # type: ignore
from pygicord import Paginator  # type: ignore
from redbot.core import Config, commands  # type: ignore
from redbot.core.bot import Red  # type: ignore
from redbot.core.i18n import Translator, cog_i18n  # type: ignore
from redbot.core.utils.chat_formatting import box  # type: ignore
from redbot.core.utils.predicates import MessagePredicate  # type: ignore
from tabulate import tabulate

from .ansi import EightBitANSI

BaseCog = getattr(commands, "Cog", object)

log: logging.Logger = logging.getLogger("red.seinacogs.tools")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

_: Translator = Translator("SeinaTools", __file__)


@cog_i18n(_)
class SeinaTools(BaseCog):  # type: ignore
    """
    Owner configuration tools for [botname].
    """

    __author__ = "inthedark.org#0666"
    __version__ = "0.1.0"

    def __init__(self, bot: Red):
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, identifier=666, force_registration=True)

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        default_global = {"embed": False, "notice": False}
        self.config.register_global(**default_global)

        self.sessions = {}

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
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def _seinatools_error(self, ctx: commands.Context, error):
        if error.__cause__:
            cause = error.__cause__
            log.exception(f"SeinaTools :: Errored :: \n{error}\n{cause}\n")
        else:
            cause = error
            log.exception(f"SeinaTools :: Errored :: \n{cause}\n")

    async def initialize(self):
        await self.bot.wait_until_red_ready()
        keys = await self.bot.get_shared_api_tokens("removebg")
        token = keys.get("api_key")
        if not token:
            if not await self.config.notice():
                await self.bot.send_to_owners(
                    "Thanks for installing my utility cog."
                    "This cog has a removebackground command which uses "
                    "an api key from the <https://www.remove.bg/> website. "
                    "You can easily get the api key from <https://www.remove.bg/api#remove-background>.\n"
                    "This is how you can add the api key - `[p]set api removebg api_key,key`"
                )
                await self.config.notice.set(True)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @commands.is_owner()
    @commands.command(name="spy")
    async def _spy(
        self,
        ctx: commands.Context,
        guild: Union[discord.Guild, int] = None,  # type: ignore
        channel_member: str = None,  # type: ignore
    ):
        """
        Yet another fun spy command.
        """
        guild = guild or ctx.guild
        channel_member = channel_member or "members"

        URL = f"https://discord.com/api/guilds/{guild.id if isinstance(guild, discord.Guild) else guild}/widget.json"
        data = await self.session.get(URL)

        json: Dict[str, Any] = await data.json()

        if "message" in json:
            return await ctx.reply(f"{ctx.author.mention} can not spy that server")

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
                    color=await ctx.embed_color(),
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
        table = box(
            tabulate(
                (
                    (
                        EightBitANSI.paint_red("Guild"),
                        EightBitANSI.paint_white(len(self.bot.guilds)),  # type: ignore
                    ),
                    (
                        EightBitANSI.paint_red("Channels"),
                        EightBitANSI.paint_white(len(tuple(self.bot.get_all_channels()))),  # type: ignore
                    ),
                    (
                        EightBitANSI.paint_red("Users"),
                        EightBitANSI.paint_white(sum(len(i.members) for i in self.bot.guilds)),  # type: ignore
                    ),
                    (
                        EightBitANSI.paint_red("DMs"),
                        EightBitANSI.paint_white(len(self.bot.private_channels)),  # type: ignore
                    ),
                    (
                        EightBitANSI.paint_red("Latency"),
                        EightBitANSI.paint_white(str(round(self.bot.latency * 1000, 2)) + "ms"),
                    ),
                    (EightBitANSI.paint_red("Cogs"), EightBitANSI.paint_white(len(self.bot.cogs))),  # type: ignore
                    (
                        EightBitANSI.paint_red("Commands"),
                        EightBitANSI.paint_white(len(tuple(self.bot.walk_commands()))),  # type: ignore
                    ),
                ),
                tablefmt="fancy_grid",
            ),
            lang="ansi",
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
    @commands.command(
        name="screenshot", aliases=["ss"]
    )  # https://discord.com/channels/133049272517001216/133251234164375552/941197661426565150
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
                    },
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

    @commands.is_owner()
    @commands.command(name="removebackground", aliases=["removebg", "rembg"])
    async def _remove_background(self, ctx: commands.Context, *, url: str):
        """
        Remove background from image url.
        """
        keys = await self.bot.get_shared_api_tokens("removebg")
        token = keys.get("api_key")

        if not token:
            await ctx.send("You have not provided an api key yet.")
        else:
            async with self.session.get(url) as response:
                data = io.BytesIO(await response.read())

            resp = await self.session.post(
                "https://api.remove.bg/v1.0/removebg",
                data={"size": "auto", "image_file": data},
                headers={"X-Api-Key": f"{token}"},
            )

            img = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(img, "nobg.png"))

    @commands.group(
        name="git",
        aliases=["githubcli", "gitcli"],
        invoke_without_command=True,
        hidden=True,
    )
    @commands.is_owner()
    async def _git_cli(
        self,
        ctx: commands.Context,
    ):
        """
        Open an interactive GIT.
        """
        if ctx.channel.id in self.sessions:
            if self.sessions[ctx.channel.id]:
                await ctx.send(
                    "Already running a GIT session in this channel. Exit it with `quit`."
                )
            else:
                await ctx.send(
                    "Already running a GIT session in this channel. Resume the GIT with `{}git resume.`".format(
                        ctx.clean_prefix
                    )
                )
            return

        self.sessions[ctx.channel.id] = True

        await ctx.send(
            "Enter git commands to execute or equivalent. `exit()` or `quit` to exit. `{}git pause` to pause.".format(
                ctx.clean_prefix
            )
        )

        while True:
            response = await self.bot.wait_for("message", check=MessagePredicate.regex(r"^`", ctx))

            if not self.sessions[ctx.channel.id]:
                continue

            cleaned = response.content  # type: ignore

            if cleaned in ("quit", "exit", "exit()"):
                await ctx.send("Exiting.")
                del self.sessions[ctx.channel.id]
                break

            if sys.platform == "win32":
                process = subprocess.run(
                    "git " + response[4:],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.stdout, process.stderr
            else:
                process = await asyncio.create_subprocess_exec(
                    "git", *shlex.split(resp[4:]), stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

            stdout = stdout.decode()
            stderr = stderr.decode()

            response = ""

            await ctx.send(
                "```diff\n{}\n{}```".format(
                    stdout.replace("```", "`\u200b`\u200b`"),
                    stderr.replace("```", "`\u200b`\u200b`"),
                )
            )

        await ctx.send("You have successfully left the GIT cli.")

    @_git_cli.command(name="pause", aliases=["resume"])
    async def _pause(self, ctx: commands.Context, toggle: Optional[bool] = None):
        """
        Pause/resumes the GIT running in the current channel.
        """
        if ctx.channel.id not in self.sessions:
            await ctx.send("There is no currently running GIT session in this channel.")
            return

        if toggle is None:
            toggle = not self.sessions[ctx.channel.id]
        self.sessions[ctx.channel.id] = toggle

        if toggle:
            await ctx.send("The GIT session in this channel has been resumed.")
        else:
            await ctx.send("The GIT session in this channel is not paused.")
