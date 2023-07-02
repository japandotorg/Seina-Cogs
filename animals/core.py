"""
MIT License

Copyright (c) 2023-present japandotorg

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

import io
import logging
from typing import Any, Dict, Final, Literal, Optional

import aiohttp
import discord
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.utils.views import SetApiView

from .api import AnimalAPI, CatAPI, DogAPI

log: logging.Logger = logging.getLogger("red.seina.animals")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]


class Animals(commands.Cog):
    """
    Random animals!
    """

    __author__: Final[str] = humanize_list(["inthedark.org"])
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=69420, force_registration=True)
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

        default_global: Dict[str, bool] = {
            "notice": False,
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
            f"Author: **{self.__author__}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    async def initialize(self) -> None:
        await self.bot.wait_until_red_ready()
        keys = await self.bot.get_shared_api_tokens("thecaptapi")
        other_keys = await self.bot.get_shared_api_tokens("thedogapi")
        try:
            token = keys.get("api_key")
            other_token = other_keys.get("api_key")
            if not token or not other_token:
                if not await self.config.notice():
                    try:
                        await self.bot.send_to_owners(
                            "Thanks for installing my animals cog. \n"
                            "This cog uses `thedogapi` & `thecatapi` respectively. \n"
                            "Make sure to configure them (check `[p]cat creds` & `[p]dog creds`) "
                            "if you want to use the `[p]cat` & `[p]dog` commands. \n"
                            "- `thedogapi`: <https://www.thedogapi.com> \n"
                            "- `thecatapi`: <https://www.thecatapi.com> \n"
                        )
                        await self.config.notice.set(True)
                    except (discord.NotFound, discord.HTTPException):
                        log.exception("Failed to send the notice message!")
        except Exception:
            log.exception("Error starting the cog.", exc_info=True)

    async def cog_unload(self) -> None:
        await self.session.close()

    @commands.group(name="cat", invoke_without_command=True)
    async def _cat(self, ctx: commands.Context, *, breed: Optional[str] = None):
        """
        Random cats!

        **Arguments**
        - `breed`: specific breed of the cat, check `[p]cat breeds` for more info.
        """
        if not ctx.invoked_subcommand:
            await ctx.typing()
            image, name, details = await CatAPI(ctx, self.session).image(breed)  # type: ignore
            if not image:
                return await ctx.reply(
                    embeds=[
                        discord.Embed(
                            description=(
                                "Invalid breed, use the `{ctx.clean_prefix}cat breeds` "
                                "command for the valid breeds."
                            ),
                            color=await ctx.embed_color(),
                        )
                    ],
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
            embed: discord.Embed = discord.Embed(
                color=await ctx.embed_color(),
                description=details,
            )
            embed.set_image(url=image)
            embed.set_author(name=name)
            await ctx.reply(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )

    @_cat.command(name="breeds")
    async def _cat_breeds(self, ctx: commands.Context):
        """
        List of cat breeds.
        """
        pages, breed_count = await CatAPI(ctx, self.session).breeds()  # type: ignore
        embeds = []
        for page in pages:
            embed = discord.Embed(title=f"There are {breed_count} cat breeds!")
            embed.description = page
            embeds.append(embed)
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, timeout=60.0)

    @_cat.command(name="creds", aliases=["setapikey", "setapi"])
    async def _cat_creds(self, ctx: commands.Context):
        """
        Instructions to set `thecatapi` API token.
        """
        message = (
            "1. Go to the <https://www.thecatapi.com> website and "
            "request for an api key. \n"
            "2. Copy your api key into the button or: \n"
            "`{prefix}set api thecatapi api_key,<your_api_key_here>.` \n"
        ).format(prefix=ctx.prefix)
        keys = {"api_key": ""}
        view = SetApiView("thecatapi", keys)
        if await ctx.embed_requested():
            embed: discord.Embed = discord.Embed(
                description=message, color=await ctx.embed_color()
            )
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(message, view=view)

    @commands.group(name="dog", invoke_without_command=True)
    async def _dog(self, ctx: commands.Context, *, breed: Optional[str] = None):
        """
        Random dogs!

        **Arguments**
        - `breed`: specific breed of the dog, check `[p]dog breeds` for more info.
        """
        if not ctx.invoked_subcommand:
            await ctx.typing()
            image, name, details = await DogAPI(ctx, self.session).image(breed)  # type: ignore
            if not image:
                return await ctx.reply(
                    embeds=[
                        discord.Embed(
                            description=(
                                "Invalid breed, use the `{ctx.clean_prefix}dog breeds` "
                                "command for the valid breeds."
                            ),
                            color=await ctx.embed_color(),
                        )
                    ],
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )
            embed: discord.Embed = discord.Embed(
                color=await ctx.embed_color(),
                description=details,
            )
            embed.set_image(url=image)
            embed.set_author(name=name)
            await ctx.reply(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )

    @_dog.command(name="breeds")
    async def _dog_breeds(self, ctx: commands.Context):
        """
        List of dog breeds.
        """
        pages, breed_count = await DogAPI(ctx, self.session).breeds()  # type: ignore
        embeds = []
        for page in pages:
            embed = discord.Embed(title=f"There are {breed_count} dog breeds!")
            embed.description = page
            embeds.append(embed)
        await menu(ctx, pages=embeds, controls=DEFAULT_CONTROLS, timeout=60.0)

    @_dog.command(name="creds", aliases=["setapikey", "setapi"])
    async def _dog_creds(self, ctx: commands.Context):
        """
        Instructions to set `thedogapi` API token.
        """
        message = (
            "1. Go to the <https://www.thedogapi.com> website and "
            "request for an api key. \n"
            "2. Copy your api key into the button or: \n"
            "`{prefix}set api thedogapi api_key,<your_api_key_here>.` \n"
        ).format(prefix=ctx.prefix)
        keys = {"api_key": ""}
        view = SetApiView("thedogapi", keys)
        if await ctx.embed_requested():
            embed: discord.Embed = discord.Embed(
                description=message, color=await ctx.embed_color()
            )
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(message, view=view)

    @commands.command(name="bear")
    async def bear(self, ctx: commands.Context):
        """
        Random bears!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("bear")
        image = await AnimalAPI(self.session).image("bear")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="bird")
    async def bird(self, ctx: commands.Context):
        """
        Random birds!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("bird")
        image = await AnimalAPI(self.session).image("bird")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="dolphin")
    async def _dolphin(self, ctx: commands.Context):
        """
        Random dolphins!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("dolphin")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
        ).set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="duck")
    async def _duck(self, ctx: commands.Context):
        """
        Random ducks!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("duck")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="elephant")
    async def _elephant(self, ctx: commands.Context):
        """
        Random elephants!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("elephant")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="fox")
    async def _fox(self, ctx: commands.Context):
        """
        Random foxes!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("fox")
        image = await AnimalAPI(self.session).image("fox")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="giraffe")
    async def _giraffe(self, ctx: commands.Context):
        """
        Random giraffes!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("giraffe")
        image = await AnimalAPI(self.session).image("giraffe")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="hippo")
    async def _hippo(self, ctx: commands.Context):
        """
        Random hippos!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("hippo")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="horse")
    async def _horse(self, ctx: commands.Context):
        """
        Random horses!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("horse")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="killerwhale")
    async def _killerwhale(self, ctx: commands.Context):
        """
        Random killer whales!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("killerwhale")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="koala")
    async def _koala(self, ctx: commands.Context):
        """
        Random koalas!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("koala")
        image = await AnimalAPI(self.session).image("koala")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="lion")
    async def _lion(self, ctx: commands.Context):
        """
        Random lions!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("lion")
        image = await AnimalAPI(self.session).image("lion")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="panda")
    async def _panda(self, ctx: commands.Context):
        """
        Random pandas!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("panda")
        image = await AnimalAPI(self.session).image("panda")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="pig")
    async def _pig(self, ctx: commands.Context):
        """
        Random pigs!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("pig")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="redpanda")
    async def _redpanda(self, ctx: commands.Context):
        """
        Random red pandas!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("redpanda")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="shark")
    async def _shark(self, ctx: commands.Context):
        """
        Random sharks!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).image("shark")
        image = await AnimalAPI(self.session).image("shark")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="snake")
    async def _snake(self, ctx: commands.Context):
        """
        Random snakes!
        """
        await ctx.typing()
        description = await AnimalAPI(self.session).fact("snake")
        image = await AnimalAPI(self.session).image("snake")
        embed: discord.Embed = discord.Embed(
            color=await ctx.embed_color(),
            description=description,
        )
        embed.set_image(url=image)
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="spider")
    async def _spider(self, ctx: commands.Context):
        """
        Random spiders!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("spider")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.command(name="turtle")
    async def _turtle(self, ctx: commands.Context):
        """
        Random turtles!
        """
        await ctx.typing()
        image = await AnimalAPI(self.session).image("turtle")
        embed: discord.Embed = discord.Embed(color=await ctx.embed_color()).set_image(
            url=image
        )
        await ctx.reply(
            embed=embed,
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
