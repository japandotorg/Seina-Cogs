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
import json
import logging
from datetime import datetime
from typing import Any, Dict, Final, List, Literal, Mapping, Optional, Union

import aiohttp
import discord
import jeyyapi  # type: ignore
from playwright.async_api import async_playwright  # type: ignore
from pygicord import Paginator  # type: ignore
from redbot.core import Config, commands  # type: ignore
from redbot.core.bot import Red  # type: ignore
from redbot.core.i18n import Translator, cog_i18n  # type: ignore
from redbot.core.utils.chat_formatting import box, humanize_list  # type: ignore
from redbot.core.utils.views import SetApiView  # type: ignore
from tabulate import tabulate

from .ansi import EightBitANSI
from .utils import CRATES_IO_LOGO, NPM_LOGO, RUBY_GEMS_LOGO, Emoji, EmojiConverter
from .views import SpotifyView

BaseCog = getattr(commands, "Cog", object)

log: logging.Logger = logging.getLogger("red.seinacogs.tools")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

_: Translator = Translator("SeinaTools", __file__)


@cog_i18n(_)
class SeinaTools(BaseCog):  # type: ignore
    """
    Utility tools for [botname].
    """

    __author__: Final[List[str]] = ["inthedark.org#0666"]
    __version__: Final[str] = "0.1.2"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.config: Config = Config.get_conf(self, identifier=666, force_registration=True)

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        self.spotify: jeyyapi.JeyyAPIClient = jeyyapi.JeyyAPIClient(session=self.session)

        default_global: Dict[str, Any] = {
            "embed": False,
            "notice": False,
            "emoji": {},
        }

        self.config.register_global(**default_global)

    async def red_get_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> Dict[str, io.BytesIO]:
        """
        Nothing to delete.
        """
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    async def red_delete_data_for_user(self, **kwargs: Any) -> Dict[str, io.BytesIO]:
        """
        Delete a user's personal data.
        No personal data is stored in this cog.
        """
        user_id: Any = kwargs.get("user_id")
        data: Final[str] = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": io.BytesIO(data.encode())}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def _seinatools_error(self, ctx: commands.Context, error) -> None:
        if error.__cause__:
            cause = error.__cause__
            log.exception(f"SeinaTools :: Errored :: \n{error}\n{cause}\n")
        else:
            cause = error
            log.exception(f"SeinaTools :: Errored :: \n{cause}\n")

    async def initialize(self) -> None:
        await self.bot.wait_until_red_ready()
        keys = await self.bot.get_shared_api_tokens("removebg")
        try:
            token = keys.get("api_key")
            if not token:
                if not await self.config.notice():
                    try:
                        await self.bot.send_to_owners(
                            "Thanks for installing my utility cog."
                            "This cog has a removebackground command which uses "
                            "an api key from the <https://www.remove.bg/> website. "
                            "You can easily get the api key from <https://www.remove.bg/api#remove-background>.\n"
                            "This is how you can add the api key - `[p]set api removebg api_key,key`"
                        )
                        await self.config.notice.set(True)
                    except (discord.NotFound, discord.HTTPException):
                        log.exception("Failed to send the notice message!")

        except Exception:
            log.exception("Error starting the cog.", exc_info=True)

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        pass

    async def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @staticmethod
    async def send_embed(ctx: commands.Context, embed: discord.Embed, **kwargs: Any):
        embed.set_author(name="Crates.io Index", icon_url=CRATES_IO_LOGO, url="https://crates.io/")
        embed.color = 0x2C4B2B
        kwargs["embed"] = embed
        await ctx.send(**kwargs)

    @commands.Cog.listener()
    async def on_red_api_tokens_update(
        self, service_name: str, api_tokens: Mapping[str, str]
    ) -> None:
        if service_name == "removebg":
            await self.cog_load()

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
    @commands.group(name="botstat", aliases=["botstatset"], invoke_without_command=True)
    async def _botstat(self, ctx: commands.Context, /):
        """
        Yet another botstat command for [botname].
        """
        if ctx.invoked_subcommand is None:
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
                            EightBitANSI.paint_white(
                                str(round(self.bot.latency * 1000, 2)) + "ms"
                            ),
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
    @_botstat.command(name="embed")
    async def _embed(self, ctx: commands.Context, true_or_false: bool):
        """
        Toggle whether botstats should use embeds.
        """
        await self.config.embed.set(true_or_false)
        return await ctx.tick()

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
    @commands.group(
        name="removebackground",
        aliases=["removebg", "rembg"],
        invoke_without_command=True,
    )
    @commands.bot_has_permissions(embed_links=True)
    async def _remove_background(self, ctx: commands.Context, *, url: str):
        """
        Remove background from image url.
        """
        if ctx.invoked_subcommand is None:
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

    @_remove_background.command(name="creds", aliases=["setapikey", "setapi"])
    async def _remove_background_creds(self, ctx: commands.Context):
        """
        Instructions to set the removebg API token.
        """
        message = (
            "1. Go to the remove.bg website and login with your account.\n"
            "(https://remove.bg)\n"
            "2. Go to the <https://www.remove.bg/api#api-changelog> page.\n"
            '3. Click "Get API Key".\n'
            '4. Click "+ New API key" if you don\'t already have one.\n'
            "5. Fill out the dialog with a key label of your choice.\n"
            "6. Copy your api key into:\n"
            "`{prefix}set api removebg api_key,<your_api_key_here>`.\n"
        ).format(prefix=ctx.prefix)
        keys = {"api_key": ""}
        view = SetApiView("removebg", keys)
        if await ctx.embed_requested():
            embed: discord.Embed = discord.Embed(
                description=message, color=await ctx.embed_color()
            )
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(message, view=view)

    perms: Dict[str, bool] = {"embed_links": True}

    @commands.has_permissions(**perms)
    @commands.bot_has_permissions(**perms)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.group(name="spotify", invoke_without_command=True)
    async def _spotify(self, ctx: commands.Context, user: Optional[discord.Member] = None) -> None:  # type: ignore
        """
        View the specified (defaults to author) user's now playing spotify status from their discord activity.
        """
        if ctx.invoked_subcommand is None:
            if not user:
                user: discord.Member = ctx.author

            async with ctx.channel.typing():
                spotify = discord.utils.find(
                    lambda pres: isinstance(pres, discord.Spotify), user.activities  # type: ignore
                )

                if spotify is None:
                    embed: discord.Embed = discord.Embed(
                        color=await ctx.embed_color(),
                        description=f"**{user}** is not listening to Spotify right now.",
                    )
                    return await ctx.send(embed=embed)

                image: io.BytesIO = await self.spotify.spotify_from_object(spotify)

            settings: Any = await self.config.all()
            emoji: Optional[Emoji] = Emoji.from_data(settings.get("emoji"))

            view: discord.ui.View = SpotifyView(
                label="Listen on Spotify",
                emoji=emoji.as_emoji(),  # type: ignore
                url=f"{spotify.track_url}",  # type: ignore
            )

            await ctx.send(
                f"{emoji.as_emoji()} **{user}** is listening to **{spotify.title}**!",  # type: ignore
                file=discord.File(image, "spotify.png"),
                view=view,
            )

    @_spotify.command(name="emoji")
    async def _spotify_embed(self, ctx: commands.Context, emoji: EmojiConverter) -> None:
        """Set an emoji to be used with the spotify command."""
        if not emoji:
            await self.config.emoji.clear()
            return await ctx.send("I have reset the spotify emoji!")
        await self.config.emoji.set(emoji.to_dict())
        await ctx.send(f"Set the spotify emoji to {emoji.as_emoji()}")

    @commands.has_permissions(**perms)
    @commands.bot_has_permissions(**perms)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.command(name="crates", aliases=["cargo", "rustpkg", "crate"])
    async def _cargo_crates(self, ctx: commands.Context, package_name: str) -> None:
        """
        Get information about a package in Crates.io.
        """
        url = f"https://crates.io/api/v1/crates/{package_name}"
        async with self.session.get(url) as response:
            if '"default": "Not Found"' in await response.text():
                embed: discord.Embed = discord.Embed(
                    description=f"There were no result for '{package_name}'"
                )
                return await self.send_embed(ctx, embed)
            else:
                foj: Dict[str, Any] = json.loads(await response.text())
        obj = foj
        foj = foj["crate"]
        if len(foj["description"]) != 0:
            embed: discord.Embed = discord.Embed(
                title=f'{foj["name"]} {foj["newest_version"]}',
                description=foj["description"].replace("![", "[").replace("]", ""),
            )
        else:
            embed: discord.Embed = discord.Embed(
                title=f'{foj["name"]} {foj["newest_version"]}',
            )
        embed.add_field(
            name="Project URLs",
            value=f"• **{foj['homepage']}**\n• **{foj['repository']}**\n• **{foj['documentation']}**",
            inline=False,
        )
        created_at = datetime.strptime(foj["created_at"][:-9], "%Y-%m-%dT%H:%M:%S.%f")
        if obj["categories"]:
            embed.add_field(
                name="Categories",
                value="\n".join(
                    f"`{i['category']}` (`{i['crates_cnt']}` crates)" for i in obj["categories"]
                ),
                inline=True,
            )
        if obj["keywords"]:
            embed.add_field(
                name="Keywords",
                value="\n".join(
                    f"`{i['id']}` (`{i['crates_cnt']}` crates)" for i in obj["keywords"]
                ),
                inline=True,
            )
        embed.add_field(
            name="Added at",
            value=f'{created_at.strftime("%a, %d %B %Y, %H:%M:%S")}',
            inline=False,
        )
        embed.add_field(
            name="Downloads",
            value=f"```prolog\nTotal Downloads  : {foj['downloads']:,}\nRecent Downloads : {foj['recent_downloads']:,}```",
            inline=False,
        )
        return await self.send_embed(ctx, embed)

    @commands.has_permissions(**perms)
    @commands.bot_has_permissions(**perms)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.command(name="npm", aliases=["node", "npmpkg", "nodepkg"])
    async def _node_module(self, ctx: commands.Context, module_name: str) -> None:
        """
        Get information about a node.js module.
        """
        url = f"https://registry.npmjs.org/{module_name}"
        async with self.session.get(url) as response:
            if "'error': 'Not Found'" in await response.text():
                embed: discord.Embed = discord.Embed(
                    description=f"There were no result for '{module_name}'.",
                    color=await ctx.embed_color(),
                )
                embed.set_author(
                    name="NPM Index",
                    icon_url=NPM_LOGO,
                    url="https://www.npmjs.com",
                )
                return await ctx.send(embed=embed)
            else:
                resp: Dict[str, Any] = json.loads(await response.text())
        if len(resp["description"]) != 0:
            embed: discord.Embed = discord.Embed(
                title=f"{resp['_id']} {sorted(resp['versions'])[-1]}",
                description=resp["description"].replace("![", "[").replace("]", ""),
                color=0xCC3534,
            )
        else:
            embed: discord.Embed = discord.Embed(
                title=f"{resp['_id']} {sorted(resp['versions'])[-1]}",
                color=0xCC3534,
            )
        embed.set_author(
            name="NPM Index",
            icon_url=NPM_LOGO,
            url="https://www.npmjs.com",
        )
        latest = sorted(resp["versions"])[-1]
        value = ""
        for number, maintainer in enumerate(resp["maintainers"], start=1):
            author = maintainer
            value += f"**{number}.** [{author.get('name')}]({author.get('url', 'https://github.com/')})\n"
        embed.add_field(name="Maintainers", value=value, inline=False)
        links = []
        if resp.get("homepage"):
            links.append(f'{resp["homepage"]}')
        if resp.get("bugs"):
            links.append(f'{resp["bugs"]["url"]}')
        github = resp["repository"]["url"][4:-4]
        links.append(f"{github}")
        links.append(f'{"https://npmjs.com/packages/" + resp["_id"]}')
        embed.add_field(
            name="Links",
            value="\n".join([f"• {key}" for key in links]),
            inline=False,
        )
        if resp.get("license"):
            embed.add_field(
                name="License",
                value=resp["license"],
                inline=False,
            )
        dependencies = list(resp["versions"][latest]["dependencies"])
        if dependencies:
            if len(dependencies) > 15:
                embed.add_field(
                    name="Dependencies",
                    value=len(dependencies),
                    inline=False,
                )
            elif len(dependencies) > 7:
                embed.add_field(
                    name="Dependencies",
                    value=", ".join(dependencies),
                    inline=False,
                )
            else:
                embed.add_field(
                    name="Dependencies",
                    value="\n".join(dependencies),
                    inline=False,
                )
        await ctx.send(embed=embed)

    @commands.has_permissions(**perms)
    @commands.bot_has_permissions(**perms)
    @commands.max_concurrency(1, per=commands.BucketType.user)
    @commands.command(name="ruby", aliases=["rubygem", "rubypkg", "rubygems"])
    async def _ruby_gems(self, ctx: commands.Context, package_name: str):
        """
        Get information about a rubygem package.
        """
        url = f"https://rubygems.org/api/v1/versions/{package_name}.json"
        async with self.session.get(url) as response:
            if "This rubygem could not be found." in await response.text():
                embed: discord.Embed = discord.Embed(
                    description=f"There were no result for '{package_name}'.",
                    color=await ctx.embed_color(),
                )
                embed.set_author(
                    name="RubyGems Index",
                    icon_url=RUBY_GEMS_LOGO,
                    url="https://rubygems.org/",
                )
                return await ctx.send(embed=embed)
            versions = json.loads(await response.text())
            version = versions[0]
        version_number = version["number"]
        number_url = (
            f"https://rubygems.org/api/v2/rubygems/{package_name}/versions/{version_number}.json"
        )
        async with self.bot.session.get(number_url) as response:
            resp: Dict[str, Any] = json.loads(await response.text())
        if len(resp["description"]) != 0:
            embed: discord.Embed = discord.Embed(
                title=f"{resp['name']} {resp['version']}",
                description=resp["description"].replace("![", "[").replace("]", ""),
                color=0xDE3F24,
            )
        else:
            embed: discord.Embed = discord.Embed(
                title=f"{resp['name']} {resp['version']}", color=0xDE3F24
            )
        embed.set_author(
            name="RubyGems Index",
            icon_url=RUBY_GEMS_LOGO,
            url="https://rubygems.org/",
        )
        embed.add_field(
            name="Summary",
            value=resp["summary"],
            inline=False,
        )
        created_at = datetime.strptime(resp["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        embed.add_field(
            name="Added at",
            value=f'{created_at.strftime("%a, %d %B %Y, %H:%M:%S")}',
            inline=False,
        )
        embed.add_field(
            name="Links",
            value=f"• {resp['homepage_url']}\n• {resp['source_code_uri']}\n• {resp['documentation_uri']}\n• {resp['project_uri']}",
            inline=False,
        )
        if not resp["dependencies"]["runtime"] is None:
            if len(resp["dependencies"]["runtime"]) > 15:
                embed.add_field(
                    name="Dependencies",
                    value=len(resp["requires_dist"]),
                    inline=False,
                )
            elif len(resp["dependencies"]["runtime"]) != 0:
                embed.add_field(
                    name=f"Dependencies ({len(resp['dependencies']['runtime'])})",
                    value="\n".join(
                        [i["name"] + i["requirements"] for i in resp["dependencies"]["runtime"]]
                    ),
                    inline=False,
                )
        embed.add_field(
            name="Downloads",
            value=(
                "```prolog\n"
                f"Total Downloads          : {resp['downloads']}\n"
                f"Latest Version Downloads : {resp['version_downloads']:,}\n",
                "```",
            ),
            inline=False,
        )
        await ctx.send(embed=embed)
