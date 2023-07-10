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
import contextlib
import datetime
import logging
import os
import random
from contextlib import suppress
from io import BytesIO
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Final, List, Literal, Optional, Union

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
from .converters import EmojiConverter
from .game import Game
from .utils import _cooldown, _get_attachments, exceptions
from .views import JoinGameView

log: logging.Logger = logging.getLogger("red.seina.battleroyale")


def game_tool(ctx: commands.Context) -> ModuleType:
    from battleroyale import game

    return game


class BattleRoyale(commands.Cog):
    """Play Battle Royale with your friends!"""

    __version__: Final[str] = "0.1.2"
    __author__: Final[str] = humanize_list(["inthedark.org", "MAX", "AAA3A", "sravan"])

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

        self.games: Dict[discord.Message, Game] = {}

        self.backgrounds_path: Path = bundled_data_path(self) / "backgrounds"
        self.config: Config = Config.get_conf(self, identifier=14, force_registration=True)

        self.log: logging.LoggerAdapter[logging.Logger] = logging.LoggerAdapter(
            log, {"version": self.__version__}
        )

        default_user: Dict[str, int] = {
            "games": 0,
            "wins": 0,
            "kills": 0,
            "deaths": 0,
        }
        default_guild: Dict[str, int] = {
            "prize": 100,
        }
        default_global: Dict[str, Union[int, str, Dict[str, int]]] = {
            "wait": 120,
            "battle_emoji": "⚔️",
            "cooldown": 60,
        }

        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

        self.cache: Dict[str, Image.Image] = {}

        self._cooldown: Optional[int] = None

        for k, v in {"br": (lambda x: self), "brgame": game_tool}.items():
            with suppress(RuntimeError):
                self.bot.add_dev_env_value(k, v)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    async def red_delete_data_for_user(self, **kwargs: Any):
        """Nothing to delete."""
        return

    async def add_stats_to_leaderboard(
        self,
        _type: Literal["games", "wins", "kills", "deaths"],
        users: List[discord.Member],
    ) -> None:
        for user in users:
            count = await self.config.user(user).get_raw(_type)
            await self.config.user(user).set_raw(_type, value=count + 1)

    async def cog_load(self) -> None:
        self._cooldown: int = await self.config.cooldown()

    @exceptions
    async def generate_image(
        self, user_1: discord.Member, user_2: discord.Member, to_file: bool = True
    ) -> Union[discord.File, Image.Image]:
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

    async def _get_content_from_url(self, url: str) -> bytes:
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
        self, ctx: commands.Context, preferred_filename: Optional[str] = None
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
            filename = f"{preferred_filename}.{ext}"
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
        await ctx.send(f"Backgorund `{f}` been removed.")

    @bank.is_owner_if_bank_global()
    @setbattleroyale.command(name="prize")
    async def _prize(self, ctx: commands.Context, amount: commands.Range[int, 10, 2**30]):
        """Changes the prize amount."""
        currency = await bank.get_currency_name(ctx.guild)
        await self.config.guild(ctx.guild).prize.set(amount)
        await ctx.send(f"Prize set to {amount} {currency}.")

    @commands.is_owner()
    @setbattleroyale.command(name="emoji")
    async def _emoji(self, ctx: commands.Context, emoji: EmojiConverter):
        """
        Set an emoji to be used with Battle Royale.
        """
        if not emoji:
            await self.config.battle_emoji.set("⚔️")
            return await ctx.send("I have reset the battle royale emoji!")
        await self.config.battle_emoji.set(emoji.as_emoji())
        await ctx.send(f"Set the battle royale emoji to {emoji.as_emoji()}")

    @commands.is_owner()
    @setbattleroyale.command(name="wait")
    async def _wait(self, ctx: commands.Context, time: commands.Range[int, 10, 200]):
        """Changes the wait time before battle starts."""
        await self.config.wait.set(time)
        await ctx.send(f"Wait time set to {time} seconds.")

    @commands.is_owner()
    @setbattleroyale.command(name="cooldown")
    async def _battleset_cooldown(
        self, ctx: commands.Context, per: commands.Range[int, 60, 2**50]
    ):
        """
        Set the coooldown amount.
        """
        await self.config.cooldown.set(per)
        await ctx.send(f"Cooldown set to {per} seconds.")

    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    @setbattleroyale.command(name="settings", aliases=["view", "ss", "showsettings"])
    async def _settings(self, ctx: commands.Context):
        """View current settings."""
        guild_data = await self.config.guild(ctx.guild).all()
        global_data = await self.config.all()
        prize = guild_data["prize"]
        wait = global_data["wait"]
        emoji = global_data["battle_emoji"]
        cooldown = global_data["cooldown"]
        embed = discord.Embed(
            title="Battle Royale Settings",
            color=await ctx.embed_color(),
            description=(
                f"**Prize:** {prize}"
                f"\n**Wait:** {wait} seconds"
                f"\n**Emoji:** {emoji}"
                f"\n**Cooldown:** {cooldown}"
            ),
        )
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.group(aliases=["br"], invoke_without_command=True)
    @commands.dynamic_cooldown(_cooldown, commands.BucketType.guild)
    async def battleroyale(
        self, ctx: commands.Context, delay: commands.Range[int, 10, 20] = 10, skip: bool = False
    ):
        """
        Battle Royale with other members!

        **Parameters:**
        - `delay`: min 10, max 20.
        - `skip`: will skip to results.
        """
        WAIT_TIME = await self.config.wait()
        emoji = await self.config.battle_emoji()

        embed: discord.Embed = discord.Embed(
            title="Battle Royale",
            color=await ctx.embed_color(),
        )
        join_view: JoinGameView = JoinGameView(emoji, timeout=WAIT_TIME)
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        endtime = now + datetime.timedelta(seconds=WAIT_TIME)
        embed.description = f"- Starting <t:{int(endtime.timestamp())}:R>.\n- Click the `Join Game` button to join the game."
        embed.set_thumbnail(url=SWORDS)
        join_view._message = await ctx.send(embed=embed, view=join_view)
        await asyncio.sleep(WAIT_TIME)
        await join_view.on_timeout()

        players: List[discord.Member] = list(join_view.players)
        if len(players) < 3:
            embed.description = (
                f"Not enough players to start. (need at least 3, {len(players)} found)."
            )
            self.battleroyale.reset_cooldown(ctx)
            with contextlib.suppress(discord.NotFound, discord.HTTPException):
                return await join_view._message.edit(embed=embed, view=None)

        game = Game(cog=self, delay=delay, skip=skip)
        self.games[join_view._message] = game
        try:
            await game.start(ctx, players=players, original_message=join_view._message)
        except Exception as e:
            self.log.exception("Something went wrong while starting the game.", exc_info=True)

    @battleroyale.command()
    @commands.dynamic_cooldown(_cooldown, commands.BucketType.guild)
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
        users: List[discord.Member] = random.sample(list(ctx.guild.members), players - 1)
        player: List[discord.Member] = list(filter(lambda u: not u.bot, users))
        if ctx.author not in player:
            player.append(ctx.author)
        game = Game(cog=self, delay=delay, skip=skip)
        embed: discord.Embed = discord.Embed(
            title="Battle Royale",
            color=await ctx.embed_color(),
            description="Automated Battle Royale session starting...",
        )
        embed.set_thumbnail(url=SWORDS)
        message = await ctx.send(embed=embed)
        self.games[message] = game
        try:
            await game.start(ctx, players=player, original_message=message)
        except Exception as e:
            self.log.exception("Something went wrong while starting the game.", exc_info=True)
    
    @battleroyale.command(name="profile", aliases=["stats"])
    async def profile(self, ctx: commands.Context, *, user: Optional[discord.Member] = None):
        """
        Show your battle royale profile.
        """
        user = user or ctx.author
        data = await self.config.user(user).all()
        embed: discord.Embed = discord.Embed(
            title=f"{user.display_name}'s Profile",
            description=(
                "```prolog\n"
                f"Games : {data['games']} \n"
                f"Wins  : {data['wins']} \n"
                f"Kills : {data['kills']} \n"
                f"Deaths: {data['deaths']} \n"
                "```"
            ),
            color=await ctx.embed_color(),
        )
        await ctx.send(embed=embed)

    @battleroyale.command(name="leaderboard", aliases=["lb"])
    async def _leaderboard(
        self, ctx: commands.Context, sort_by: Literal["wins", "games", "kills"] = "wins"
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
        pages: List[discord.Embed] = []
        for page in pagify(description, page_length=4000):
            embed = discord.Embed(title="BattleRoyale Leaderboard", color=await ctx.embed_color())
            embed.description = page
            pages.append(embed)
        await SimpleMenu(
            pages=pages,
            disable_after_timeout=True,
            timeout=60,
        ).start(ctx)
