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

import asyncio
import datetime
import logging
import os
import random
import typing
from io import BytesIO
from pathlib import Path

import aiohttp
import discord
import prettytable as pt
from PIL import Image
from redbot.core import Config, bank, commands
from redbot.core.bot import Red
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import box, humanize_list, pagify
from redbot.core.utils.views import SimpleMenu

from .constants import SWORDS
from .game import Game
from .utils import _get_attachments
from .views import JoinGameView

log: logging.Logger = logging.getLogger("red.seina.battleroyale")


class BattleRoyale(commands.Cog):
    """Play Battle Royale with your friends!"""

    __version__ = "0.1.0"
    __author__ = humanize_list(["inthedark.org", "MAX", "AAA3A", "sravan"])

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.games: typing.Dict[discord.Message, Game] = {}

        self.backgrounds_path: Path = bundled_data_path(self) / "backgrounds"
        self.config: Config = Config.get_conf(self, identifier=14, force_registration=True)
        self.battle_royale_default_user: typing.Dict[str, int] = {
            "games": 0,
            "wins": 0,
            "kills": 0,
            "deaths": 0,
        }
        self.battle_royale_default_guild: typing.Dict[str, int] = {
            "prize": 100,
        }
        self.config.register_user(**self.battle_royale_default_user)
        self.config.register_guild(**self.battle_royale_default_guild)

        self.cache: typing.Dict[str, Image.Image] = {}

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    async def red_delete_data_for_user(self, **kwargs: typing.Any):
        """Nothing to delete."""
        return

    async def add_stats_to_leaderboard(
        self,
        _type: typing.Literal["games", "wins", "kills", "deaths"],
        users: typing.List[discord.Member],
    ) -> None:
        for user in users:
            count = await self.config.user(user).get_raw(_type)
            await self.config.user(user).set_raw(_type, value=count + 1)

    async def generate_image(
        self, user_1: discord.Member, user_2: discord.Member, to_file: bool = True
    ) -> typing.Union[discord.File, Image.Image]:
        backgrounds = os.listdir(self.backgrounds_path)
        background = random.choice(backgrounds)
        with open(self.backgrounds_path / background, mode="rb") as f:
            background_bytes = f.read()
        img = Image.open(BytesIO(background_bytes))
        img = img.convert("RGBA")
        avatar_1 = Image.open(BytesIO(await self._get_content_from_url(user_1.display_avatar.url)))
        avatar_1 = avatar_1.resize((400, 400))
        img.paste(
            avatar_1,
            ((0 + 30), (int(img.height / 2) - 200), (0 + 30 + 400), (int(img.height / 2) + 200)),
        )
        avatar_2 = Image.open(BytesIO(await self._get_content_from_url(user_2.display_avatar.url)))
        avatar_2 = avatar_2.resize((400, 400))
        img.paste(
            avatar_2,
            (
                (int(img.width) - 30 - 400),
                (int(img.height / 2) - 200),
                (int(img.width) - 30),
                (int(img.height / 2) + 200),
            ),
        )
        swords_bytes = await self._get_content_from_url(SWORDS)
        swords = Image.open(BytesIO(swords_bytes))
        swords = swords.convert("RGBA")
        for i in range(swords.width):
            for j in range(swords.height):
                r, g, b, a = swords.getpixel((i, j))
                if r == 0 and g == 0 and b == 0:
                    swords.putpixel((i, j), (r, g, b, 0))
        swords = swords.resize((300, 300))
        img.paste(
            swords,
            (
                (int(img.width / 2) - 150),
                (int(img.height / 2) - 150),
                (int(img.width / 2) + 150),
                (int(img.height / 2) + 150),
            ),
            mask=swords,
        )
        if not to_file:
            return img
        buffer = BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return discord.File(buffer, filename="image.png")

    async def _get_content_from_url(self, url: str) -> typing.Union[bytes, Image.Image]:
        if url in self.cache:
            return self.cache[url]
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                self.cache[url] = await r.content.read()
        return self.cache[url]

    @commands.group(aliases=["battleset"])
    async def setbattleroyale(self, ctx: commands.Context):
        """
        Configuration commands for BattleRoyale.
        """

    @commands.is_owner()
    @setbattleroyale.command(name="backgroundpath", aliases=["path"])
    async def _get_background_path(self, ctx: commands.Context):
        """
        Get folder path for this cog's default backgrounds.
        """
        path: str = os.path.join(self.backgrounds_path)
        await ctx.send(f"Your default background folder path is:\n- `{path}`")

    @commands.is_owner()
    @setbattleroyale.command(name="addbackground", aliases=["ab"])
    async def _add_background(
        self, ctx: commands.Context, preferred_filename: typing.Optional[str] = None
    ):
        """
        Add a custom background to the cog from discord. If several backgrounds are saved, the cog will select one at random.

        **Parameters:**
        - `preferred_filaname`: Your preferred file name.

        **Note:**
        - Do not include the file extension in the filaname, it'll be added automatically.
        """
        content = _get_attachments(ctx)
        if not content:
            raise commands.UserFeedbackCheckFailure("I was unable to find any attachments.")
        url = content[0].url
        filename = content[0].filename
        valid_extensions = ["png", "jpg", "jpeg"]
        if all(ext == filename.split(".")[-1].lower() for ext in valid_extensions):
            raise commands.UserFeedbackCheckFailure(
                f"This is not a valid format, must be one of the following extensions: {humanize_list(valid_extensions)}."
            )
        ext = filename.split(".")[-1].lower()
        try:
            bytes_file = await self._get_content_from_url(url)
        except Exception:
            raise commands.UserFeedbackCheckFailure("I was unable to get the file from Discord.")
        if preferred_filename:
            filename = f"{preferred_filename}{ext}"
        filepath = os.path.join(self.backgrounds_path, filename)
        with open(filepath, "wb") as f:
            f.write(bytes_file)
        await ctx.send(f"Your custom background has been saved as `{filename}`.")

    @setbattleroyale.command(name="removebackground", aliases=["rb"])
    async def _remove_background(self, ctx: commands.Context, filename: str):
        """
        Remove a background from the cog's backgrounds folder.
        """
        path = os.path.join(self.backgrounds_path)
        for f in os.listdir(path):
            if filename.lower() in f.lower():
                break
        else:
            raise commands.UserFeedbackCheckFailure(
                "I could not find any background images with that name."
            )
        file = os.path.join(path, f)
        try:
            os.remove(file)
        except OSError as exc:
            await ctx.send(f"Could not delete file: {str(exc)}.")
        await ctx.send(f"Backgorund has {f} been removed.")

    @commands.admin_or_permissions(manage_guild=True)
    @setbattleroyale.command(name="prize")
    async def _prize(self, ctx: commands.Context, amount: commands.Range[int, 10, 2**30]):
        """Changes the wait time before a race starts."""
        currency = await bank.get_currency_name(ctx.guild)
        await self.config.guild(ctx.guild).prize.set(amount)
        await ctx.send(f"Prize set to {amount} {currency}.")

    @commands.guild_only()
    @commands.group(aliases=["br"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def battleroyale(
        self, ctx: commands.Context, delay: commands.Range[int, 10, 20] = 10, skip: bool = False
    ):
        """
        Battle Royale with other members!

        **Parameters:**
        - `delay`: min 10, max 20.
        - `skip`: will skip to results.
        """
        WAIT_TIME = 120

        embed: discord.Embed = discord.Embed(
            title="Battle Royale",
            color=await ctx.embed_color(),
        )
        join_view: JoinGameView = JoinGameView(self, ctx, timeout=WAIT_TIME)
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        endtime = now + datetime.timedelta(seconds=WAIT_TIME)
        embed.description = f"- Starting <t:{int(endtime.timestamp())}:R>.\n- Click the `Join Game` button to join the game."
        embed.set_image(url=SWORDS)
        join_view._message = await ctx.send(embed=embed, view=join_view)
        await asyncio.sleep(WAIT_TIME)
        await join_view.on_timeout()

        players: typing.List[discord.Member] = list(join_view.players)
        if len(players) < 3:
            embed.description = (
                f"Not enough players to start. (need at least 3, {len(players)} found)."
            )
            return await join_view._message.edit(embed=embed, view=None)

        game = Game(cog=self, delay=delay, skip=skip)
        self.games[join_view._message] = game
        await game.start(ctx, players=players, original_message=join_view._message)

    @battleroyale.command()
    async def auto(
        self,
        ctx: commands.Context,
        players: commands.Range[int, 10, 100] = 30,
        delay: commands.Range[int, 10, 20] = 10,
        skip: bool = False,
    ):
        """
        Battle Royale with random players from your server.

        **Parameters**
        - `players`: how many players you want to join.
        - `delay`: min 10, max 20.
        - `skip`: will skip to results.
        """
        users: typing.List[discord.Member] = random.sample(list(ctx.guild.members), players - 1)
        player: typing.List[discord.Member] = list(filter(lambda u: not u.bot, users))
        player.append(ctx.author)
        game = Game(cog=self, delay=delay, skip=skip)
        embed: discord.Embed = discord.Embed(
            title="Battle Royale",
            color=await ctx.embed_color(),
            description="Automated Battle Royale session starting...",
        )
        embed.set_image(url=SWORDS)
        message = await ctx.send(embed=embed)
        self.games[message] = game
        await game.start(ctx, players=player, original_message=message)

    #@battleroyale.command()
    #async def profile(self, ctx: commands.Context, *, user: discord.Member = None):
    #    """Show your profile.

    #    **Parameters:**
    #    - `user`: The user to show the profile of.
    #    """
    #    user = user or ctx.author
    #    data = await self.config.user(user).all()
    #    await ctx.send(data)

    @battleroyale.command(name="leaderboard", aliases=["lb"])
    async def _leaderboard(
        self, ctx: commands.Context, sort_by: typing.Literal["wins", "games", "kills"] = "wins"
    ):
        """Show the leaderboard.

        **Parameters:**
        - `sort_by`: `wins`, `games` or `kills`.
        """
        data = await self.config.all_users()
        if not data:
            return await ctx.send("No one has played yet.")
        leaderboard = sorted(data.items(), key=lambda x: x[1][sort_by], reverse=True)
        leaderboard = leaderboard[:10]
        table = pt.PrettyTable()
        table.field_names = ["#", "User", "Wins", "Games", "Kills", "Deaths"]
        for index, (user_id, user_data) in enumerate(leaderboard, start=1):
            if (user := ctx.bot.get_user(int(user_id))) is None:
                continue
            table.add_row(
                row=[
                    index,
                    user.display_name,
                    user_data["wins"],
                    user_data["games"],
                    user_data["kills"],
                    user_data["deaths"],
                ]
            )
        description = box(table.get_string(), lang="sml")
        pages: typing.List[discord.Embed] = []
        for page in pagify(description, page_length=4000):
            embed = discord.Embed(title="BattleRoyale Leaderboard", color=await ctx.embed_color())
            embed.description = page
            pages.append(embed)
        await SimpleMenu(
            pages=pages,
            disable_after_timeout=True,
            timeout=60,
        ).start(ctx)
