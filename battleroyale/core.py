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
from typing import Any, Coroutine, Dict, Final, List, Literal, Optional, Tuple, Union, cast

import aiohttp
import discord
import prettytable as pt
from PIL import Image, UnidentifiedImageError
from redbot.core import Config, bank, commands
from redbot.core.bot import Red
from redbot.core.data_manager import bundled_data_path, cog_data_path
from redbot.core.utils.chat_formatting import box, humanize_list, pagify
from redbot.core.utils.views import SimpleMenu

from .constants import EXP_MULTIPLIER, MAX_EXP, MIN_EXP, SWORDS
from .converters import EmojiConverter
from .game import Game
from .models._pillow import Canvas, Editor, Font
from .utils import (
    _cooldown,
    _get_attachments,
    exceptions,
    generate_max_exp_for_level,
    get_exp_percentage,
    guild_roughly_chunked,
    maybe_update_level,
    truncate,
)
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

        self.font_path: Path = bundled_data_path(self) / "fonts" / "ACME.ttf"
        self.backgrounds_path: Path = bundled_data_path(self) / "backgrounds"
        self.custom_backgrounds_path: Path = cog_data_path(self) / "backgrounds"

        self.log: logging.LoggerAdapter[logging.Logger] = logging.LoggerAdapter(
            log, {"version": self.__version__}
        )

        self.config: Config = Config.get_conf(self, identifier=14, force_registration=True)
        default_user: Dict[str, Union[int, str]] = {
            "games": 0,
            "wins": 0,
            "kills": 0,
            "deaths": 0,
            "exp": 0,
            "level": 1,
            "bio": "I'm just a plain human.",
        }
        default_guild: Dict[str, int] = {"prize": 100}
        default_global: Dict[str, Union[int, str, Dict[str, int]]] = {
            "wait": 120,
            "battle_emoji": "⚔️",
            "cooldown": 60,
        }
        self.config.register_user(**default_user)
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)

        self.cache: Dict[str, Image.Image] = {}

        self._cooldown: Optional[int] = None  # type: ignore

        for k, v in {"br": (lambda x: self), "brgame": game_tool}.items():
            with suppress(RuntimeError):
                self.bot.add_dev_env_value(k, v)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed: str = super().format_help_for_context(ctx) or ""
        n: str = "\n" if "\n\n" not in pre_processed else ""
        text: List[str] = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    async def red_delete_data_for_user(self, **kwargs: Any) -> None:
        """Nothing to delete."""
        return

    async def add_stats_to_leaderboard(
        self,
        _type: Literal["games", "wins", "kills", "deaths"],
        users: List[discord.Member],
    ) -> None:
        for user in users:
            count = await self.config.user(user).get_raw(_type)
            await self.config.user(user).set_raw(_type, value=int(count) + 1)

    async def add_exp_and_maybe_update_level(self, user: discord.User) -> None:
        config: Dict[str, Union[int, str]] = await self.config.user(user).all()
        _exp: int = cast(int, config["exp"])
        level: int = cast(int, config["level"])
        random_exp: int = random.randint(MIN_EXP, MAX_EXP)
        await self.config.user(user).exp.set(_exp + random_exp)
        max_exp_for_level: int = generate_max_exp_for_level(level, EXP_MULTIPLIER)
        if (new_level := maybe_update_level(_exp + random_exp, max_exp_for_level, level)) > level:
            await self.config.user(user).level.set(new_level)
            await self.config.user(user).exp.clear()

    async def cog_load(self) -> None:
        self._cooldown: int = await self.config.cooldown()

    @exceptions
    async def generate_image(
        self, user_1: discord.Member, user_2: discord.Member, to_file: bool = True
    ) -> Union[discord.File, Image.Image]:
        backgrounds: List[Path] = [
            self.backgrounds_path / background for background in os.listdir(self.backgrounds_path)
        ]
        if self.custom_backgrounds_path.exists():
            backgrounds.extend(
                [
                    self.custom_backgrounds_path / background
                    for background in os.listdir(self.custom_backgrounds_path)
                ]
            )
        while True:
            background: Path = random.choice(backgrounds)
            with open(background, mode="rb") as f:
                background_bytes = f.read()
            try:
                img: Image.Image = Image.open(BytesIO(background_bytes))
            except UnidentifiedImageError:
                continue
            else:
                break
        img: Image.Image = img.convert("RGBA")
        avatar_1: Image.Image = Image.open(BytesIO(await user_1.display_avatar.read()))
        avatar_1: Image.Image = avatar_1.resize((400, 400))
        img.paste(
            avatar_1,
            ((0 + 30), (int(img.height / 2) - 200), (0 + 30 + 400), (int(img.height / 2) + 200)),
        )
        avatar_2: Image.Image = Image.open(BytesIO(await user_2.display_avatar.read())).convert(
            "L"
        )
        avatar_2: Image.Image = avatar_2.resize((400, 400))
        img.paste(
            avatar_2,
            (
                (int(img.width) - 30 - 400),
                (int(img.height / 2) - 200),
                (int(img.width) - 30),
                (int(img.height / 2) + 200),
            ),
        )
        swords_bytes: Image.Image = await self._get_content_from_url(SWORDS)
        swords: Image.Image = Image.open(BytesIO(swords_bytes))
        swords: Image.Image = swords.convert("RGBA")
        for i in range(swords.width):
            for j in range(swords.height):
                r, g, b, a = cast(Tuple[float, ...], swords.getpixel((i, j)))
                if r == 0 and g == 0 and b == 0:
                    swords.putpixel((i, j), (r, g, b, 0))
        swords: Image.Image = swords.resize((300, 300))
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
        buffer: BytesIO = BytesIO()
        img.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return discord.File(buffer, filename="image.png")

    @exceptions
    async def generate_profile(
        self, user: discord.Member, *, to_file: bool = True
    ) -> Union[Editor, discord.File]:
        await self.add_exp_and_maybe_update_level(user)
        config: Dict[str, Union[str, int]] = await self.config.user(user).all()
        background: Editor = Editor(Canvas((800, 240), color="#2F3136"))
        profile: Editor = Editor(BytesIO(await user.display_avatar.read())).resize((200, 200))
        f40, f25, f20 = (
            Font(self.font_path, size=40),
            Font(self.font_path, size=25),
            Font(self.font_path, size=20),
        )
        background.paste(profile, (20, 20))
        background.text((240, 20), user.global_name, font=f40, color="white")
        background.text((240, 80), config["bio"], font=f20, color="white")
        background.text((250, 170), "Wins", font=f25, color="white")
        background.text((310, 155), str(config["wins"]), font=f40, color="white")
        background.rectangle((390, 170), 360, 25, outline="white", stroke_width=2)
        max_exp: int = generate_max_exp_for_level(config["level"], EXP_MULTIPLIER)
        background.bar(
            (394, 174),
            352,
            17,
            percentage=get_exp_percentage(config["exp"], max_exp),
            fill="white",
            stroke_width=2,
        )
        background.text(
            (390, 135),
            "Level: {:,}".format(config["level"]),
            font=f25,
            color="white",
        )
        background.text(
            (750, 135),
            "XP: {:,} / {:,}".format(config["exp"], max_exp),
            font=f25,
            color="white",
            align="right",
        )
        if not to_file:
            return background
        return discord.File(background.image_bytes, filename="profile.png")

    async def _get_content_from_url(self, url: str) -> Image.Image:
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
        path: str = os.path.join(self.custom_backgrounds_path)
        await ctx.send(f"Your default custom backgrounds folder path is:\n- `{path}`")

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
        filepath = os.path.join(self.custom_backgrounds_path, filename)
        with open(filepath, "wb") as f:
            f.write(bytes_file)
        await ctx.send(f"Your custom background has been saved as `{filename}`.")

    @commands.is_owner()
    @setbattleroyale.command(name="removebackground", aliases=["rb"])
    async def _remove_background(self, ctx: commands.Context, filename: str):
        """
        Remove a background from the cog's backgrounds folder.
        """
        path = self.custom_backgrounds_path
        if not path.exists() or not (custom_backgrounds := os.listdir(path)):
            raise commands.UserFeedbackCheckFailure(
                "I could not find any background images with that name."
            )
        for f in custom_backgrounds:
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

    @commands.is_owner()
    @setbattleroyale.command(name="listbackgrounds")
    async def _list_backgrounds(self, ctx: commands.Context):
        """
        List your cog's custom backgrounds.
        """
        path = self.custom_backgrounds_path
        if not path.exists() or not (custom_backgrounds := os.listdir(path)):
            raise commands.UserFeedbackCheckFailure("You don't have any custom background images.")
        await SimpleMenu(
            pages=[
                box(page, lang="py")
                for page in pagify(
                    "\n".join(f"- {custom_background}" for custom_background in custom_backgrounds)
                )
            ]
        ).start(ctx)

    @bank.is_owner_if_bank_global()
    @setbattleroyale.command(name="prize")
    async def _prize(self, ctx: commands.Context, amount: commands.Range[int, 10, 2**30]):
        """Changes the prize amount."""
        currency = await bank.get_currency_name(ctx.guild)
        await self.config.guild(ctx.guild).prize.set(amount)
        await ctx.send(f"Prize set to {amount} {currency}.")

    @commands.is_owner()
    @setbattleroyale.command(name="emoji")
    async def _emoji(self, ctx: commands.Context, emoji: EmojiConverter = None):
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
    @commands.dynamic_cooldown(_cooldown, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.channel)
    @commands.bot_has_permissions(embed_links=True)
    @commands.group(aliases=["br"], invoke_without_command=True)
    async def battleroyale(
        self,
        ctx: commands.GuildContext,
        delay: commands.Range[int, 10, 20] = 10,
        skip: bool = False,
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
            cast(commands.Command, self.battleroyale).reset_cooldown(ctx)
            with contextlib.suppress(discord.NotFound, discord.HTTPException):
                return await join_view._message.edit(embed=embed, view=None)

        game: Game = Game(cog=self, delay=delay, skip=skip)
        self.games[join_view._message] = game
        await game.start(ctx, players=players, original_message=join_view._message)

    @cast(commands.Group, battleroyale).command()
    async def auto(
        self,
        ctx: commands.GuildContext,
        players: commands.Range[int, 10, 100] = 30,
        delay: commands.Range[int, 10, 20] = 10,
        skip: bool = False,
    ):
        """
        Battle Royale with random players from your server.

        Command author is automatically added to the player queue.

        **Parameters**
        - `players`: how many players you want to join.
        - `delay`: min 10, max 20.
        - `skip`: will skip to results.
        """
        guild_members = list(ctx.guild.members)
        users: List[discord.Member] = random.sample(
            guild_members, min(players - 1, len(guild_members))
        )
        players: List[discord.Member] = list(filter(lambda u: not u.bot, users))
        if ctx.author not in players:
            players.append(ctx.author)
        game: Game = Game(cog=self, delay=delay, skip=skip)
        embed: discord.Embed = discord.Embed(
            title="Battle Royale",
            color=await ctx.embed_color(),
            description="Automated Battle Royale session starting...",
        )
        embed.set_thumbnail(url=SWORDS)
        message = await ctx.send(embed=embed)
        self.games[message] = game
        await game.start(ctx, players=players, original_message=message)

    @cast(commands.Group, battleroyale).command()
    async def role(
        self,
        ctx: commands.GuildContext,
        role: discord.Role,
        delay: commands.Range[int, 10, 20] = 10,
        skip: bool = False,
    ):
        """
        Battle Royale with members from a specific role in your server.

        Command author is automatically added to the player queue even if they don't have the role.

        **Parameters**
        - `role`: which role to add to the player queue.
        - `delay`: min 10, max 20.
        - `skip`: will skip to results.
        """
        if guild_roughly_chunked(ctx.guild) is False and self.bot.intents.members:
            await ctx.guild.chunk()
        if not role.members:
            await ctx.send(
                embed=discord.Embed(
                    description=f"**{role.name}** has no members.",
                    color=await ctx.embed_color(),
                ).set_thumbnail(url=SWORDS)
            )
            return
        users: List[discord.Member] = list(role.members)
        players: List[discord.Member] = list(filter(lambda u: not u.bot, users))
        if ctx.author not in players:
            players.append(ctx.author)
        if len(players) < 3:
            await ctx.send(
                embed=discord.Embed(
                    description=f"Not enough players in the role to start. (need at least 3, {len(players)} found).",
                    color=await ctx.embed_color(),
                ).set_thumbnail(url=SWORDS)
            )
            return
        game: Game = Game(cog=self, delay=delay, skip=skip)
        embed: discord.Embed = discord.Embed(
            title="Battle Royale",
            color=await ctx.embed_color(),
            description=f"Automated {role.mention} Battle Royale session starting...",
        )
        embed.set_thumbnail(url=SWORDS)
        message = await ctx.send(embed=embed)
        self.games[message] = game
        await game.start(ctx, players=players, original_message=message)

    @cast(commands.Group, battleroyale).group(
        name="profile", aliases=["stats"], invoke_without_command=True
    )
    async def profile(self, ctx: commands.GuildContext, *, user: Optional[discord.Member] = None):
        """
        Show your battle royale profile.

        - Use the `[p]br profile bio <message>` command to change the bio.
        """
        if not ctx.invoked_subcommand:
            async with ctx.typing():
                user = user or cast(discord.Member, ctx.author)
                file: Coroutine[Any, Any, discord.File] = await asyncio.to_thread(
                    self.generate_profile, user=user
                )
                await ctx.send(
                    files=[await file],
                    reference=ctx.message.to_reference(fail_if_not_exists=False),
                    allowed_mentions=discord.AllowedMentions(replied_user=False),
                )

    @profile.command(name="bio", aliases=["setbio", "bioset"])
    async def bio(self, ctx: commands.GuildContext, *, message: commands.Range[str, 1, 25]):
        """
        Change your default bio.
        """
        await self.config.user(ctx.author).bio.set(message)
        await ctx.send("Bio changed to '{}'.".format(message))

    @cast(commands.Group, battleroyale).command(name="leaderboard", aliases=["lb"])
    async def _leaderboard(
        self, ctx: commands.GuildContext, sort_by: Literal["wins", "games", "kills"] = "wins"
    ):
        """Show the leaderboard.

        **Parameters:**
        - `sort_by`: `wins`, `games` or `kills`.
        """
        data = await self.config.all_users()
        if not data:
            return await ctx.send("No one has played yet.")
        leaderboard = sorted(data.items(), key=lambda x: x[1][sort_by], reverse=True)
        table = pt.PrettyTable()
        table.title = "Battle Royale Leaderboard"
        table.field_names = ["#", "Games / Wins / Kills / Deaths", "User"]
        for index, (user_id, user_data) in enumerate(leaderboard, start=1):
            if (user := cast(discord.User, ctx.bot.get_user(int(user_id)))) is None:
                continue
            table.add_row(
                row=[
                    index,
                    "{} / {} / {} / {}".format(
                        user_data["games"],
                        user_data["wins"],
                        user_data["kills"],
                        user_data["deaths"],
                    ),
                    truncate(user.global_name, max=15),
                ]
            )
        string: str = table.get_string()
        pages: List[str] = []
        for page in pagify(string, page_length=2000):
            pages.append(box(page, lang="sml"))
        await SimpleMenu(
            pages=pages,
            disable_after_timeout=True,
            timeout=60,
        ).start(ctx)
