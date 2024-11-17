import asyncio
import contextlib
import random
from typing import TYPE_CHECKING, Dict, Iterable, List, Protocol, Tuple, Union, cast

import discord
from redbot.core import commands
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import pagify

from .converters import RoleOrUserConverter
from .utils import truncate

if TYPE_CHECKING:
    from .core import Lottery


class _Manager(Protocol):
    def __init__(self, cog: "Lottery") -> None: ...

    async def get_guild(
        self, guild: discord.Guild
    ) -> Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]]: ...

    async def roll(self, author: discord.Member, name: str) -> Tuple[str, int, int, int]: ...

    async def create(
        self, author: discord.Member, name: str, deputies: Iterable[RoleOrUserConverter] = []
    ) -> None: ...

    async def delete(self, guild: discord.Guild, name: str) -> None: ...

    async def info(self, ctx: commands.GuildContext, name: str) -> discord.Embed: ...

    async def tickets(self, ctx: commands.GuildContext) -> List[discord.Embed]: ...

    async def tickets_add(
        self, author: discord.Member, name: str, member: discord.Member, tickets: int = 1
    ) -> None: ...

    async def tickets_remove(
        self, author: discord.Member, name: str, member: discord.Member, tickets: int = 1
    ) -> None: ...

    async def tickets_list(self, ctx: commands.GuildContext, name: str) -> List[discord.Embed]: ...

    async def deputies(self, ctx: commands.GuildContext, name: str) -> List[str]: ...

    async def deputies_add(
        self, name: str, guild: discord.Guild, elements: Iterable[RoleOrUserConverter]
    ) -> None: ...

    async def deputies_remove(
        self, name: str, guild: discord.Guild, elements: Iterable[RoleOrUserConverter]
    ) -> None: ...


class LotteryManager(_Manager):
    def __init__(self, cog: "Lottery") -> None:
        self.cog: "Lottery" = cog
        self.config: Config = cog.config

    async def get_guild(
        self, guild: discord.Guild
    ) -> Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]]:
        return await self.config.guild(guild).lotteries()

    async def roll(self, author: discord.Member, name: str) -> Tuple[str, int, int, int]:
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            author.guild
        )
        if name.lower() not in config.keys():
            raise commands.CheckFailure()
        lottery: Dict[str, Union[int, Dict[str, int], List[int]]] = config[name.lower()]
        deputies: List[int] = cast(List[int], lottery["deputies"])
        if not author.guild_permissions.manage_guild and not (
            author.id == int(lottery["owner"])
            or author.id in deputies
            or any(deputy in list(author._roles) for deputy in deputies)
        ):
            raise commands.CheckFailure()
        tickets: Dict[str, int] = cast(Dict[str, int], lottery["users"])
        if not tickets:
            raise commands.UserFeedbackCheckFailure(
                "There are no tickets in the lottery `{}`.".format(name.lower())
            )
        total: int = sum(tickets.values())
        cumulative: List[int] = [0]
        for score in tickets.values():
            cumulative.append(cumulative[-1] + score)
        num: int = random.randint(1, total)
        left, right = 0, len(cumulative) - 1
        while left < right:
            mid: int = (left + right) // 2
            if cumulative[mid] < num:
                left: int = mid + 1
            else:
                right: int = mid
        index: int = left - 1
        winner: str = list(tickets.keys())[index]
        winner_score: int = tickets[winner]
        return winner, winner_score, index, len(tickets)

    async def create(
        self, author: discord.Member, name: str, deputies: Iterable[RoleOrUserConverter] = []
    ) -> None:
        lock: asyncio.Lock = self.config.guild(author.guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            author.guild
        )
        if name.lower() in config.keys():
            lock.release()
            raise commands.UserFeedbackCheckFailure(
                "There's already a lottery named `{}`.".format(name.lower())
            )
        config[name.lower()] = {
            "owner": author.id,
            "users": {},
            "created_at": int(discord.utils.utcnow().timestamp()),
            "deputies": [d.id for d in deputies],
        }
        await self.config.guild(author.guild).lotteries.set(config)
        lock.release()

    async def delete(self, guild: discord.Guild, name: str) -> None:
        lock: asyncio.Lock = self.config.guild(guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            guild
        )
        if name.lower() not in config.keys():
            lock.release()
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        with contextlib.suppress(KeyError):
            del config[name.lower()]
        await self.config.guild(guild).lotteries.set(config)
        lock.release()

    async def info(self, ctx: commands.GuildContext, name: str) -> discord.Embed:
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            ctx.guild
        )
        if name.lower() not in config.keys():
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        lottery: Dict[str, Union[int, Dict[str, int], List[int]]] = config[name.lower()]
        total: int = sum(list(cast(Dict[str, int], lottery["users"]).values()))
        embed: discord.Embed = discord.Embed(
            title="Lottery Info",
            color=await ctx.embed_color(),
            description=("**Name**: {}\n" "**Tickets**: {}\n" "**Created**: {}\n").format(
                name.lower(),
                total,
                "<t:{}:F>".format(lottery["created_at"]),
            ),
        )
        droles, dusers = [], []
        for item in list(lottery["deputies"]):
            try:
                obj: Union[discord.Role, discord.Member] = await cast(
                    commands.Converter[Union[discord.Role, discord.Member]], RoleOrUserConverter
                ).convert(ctx, str(item))
            except commands.BadArgument:
                continue
            else:
                if isinstance(obj, discord.Role):
                    droles.append("{0.mention} (`{0.id}`)".format(obj))
                elif isinstance(obj, discord.Member):
                    dusers.append("{0.mention} (`{0.id}`)".format(obj))
                else:
                    continue
        if droles:
            value: str = "\n".join(["{}. {}".format(idx + 1, d) for idx, d in enumerate(droles)])
            embed.add_field(
                name="Deputy Roles:",
                value=truncate(value, max=1000),
                inline=False,
            )
        if dusers:
            value: str = "\n".join(["{}. {}".format(idx + 1, d) for idx, d in enumerate(dusers)])
            embed.add_field(
                name="Deputy Users:",
                value=truncate(value, max=1000),
                inline=False,
            )
        return embed

    async def tickets(self, ctx: commands.GuildContext) -> List[discord.Embed]:
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            ctx.guild
        )
        if len(config.items()) < 1:
            raise commands.UserFeedbackCheckFailure("This server does not have any lottery.")
        embeds: List[discord.Embed] = []
        for idx, (name, ticket) in enumerate(config.items()):
            embed: discord.Embed = discord.Embed(
                title="Lottery - {}".format(name.lower()),
                description="**Tickets**: {}\n**Created**: {}\n".format(
                    sum(list(cast(Dict[str, int], ticket["users"]).values())),
                    "<t:{}:F>".format(ticket["created_at"]),
                ),
                color=await ctx.embed_color(),
            )
            droles, dusers = [], []
            for item in list(ticket["deputies"]):
                try:
                    obj: Union[discord.Role, discord.Member] = await cast(
                        commands.Converter[Union[discord.Role, discord.Member]],
                        RoleOrUserConverter,
                    ).convert(ctx, str(item))
                except commands.BadArgument:
                    continue
                else:
                    if isinstance(obj, discord.Role):
                        droles.append("{0.mention} (`{0.id}`)".format(obj))
                    elif isinstance(obj, discord.Member):
                        dusers.append("{0.mention} (`{0.id}`)".format(obj))
                    else:
                        continue
            if droles:
                value: str = "\n".join(
                    ["{}. {}".format(idx + 1, d) for idx, d in enumerate(droles)]
                )
                embed.add_field(
                    name="Deputy Roles:",
                    value=truncate(value, max=1000),
                    inline=False,
                )
            if dusers:
                value: str = "\n".join(
                    ["{}. {}".format(idx + 1, d) for idx, d in enumerate(dusers)]
                )
                embed.add_field(
                    name="Deputy Users:",
                    value=truncate(value, max=1000),
                    inline=False,
                )
            embed.set_footer(text="Ticket {}/{}".format(idx + 1, len(config.items())))
            embeds.append(embed)
        return embeds

    async def tickets_add(
        self, author: discord.Member, name: str, member: discord.Member, tickets: int = 1
    ) -> None:
        lock: asyncio.Lock = self.config.guild(author.guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            author.guild
        )
        if name.lower() not in config.keys():
            lock.release()
            raise commands.CheckFailure()
        lottery: Dict[str, Union[int, Dict[str, int], List[int]]] = config[name.lower()]
        deputies: List[int] = cast(List[int], lottery["deputies"])
        if not author.guild_permissions.manage_guild and not (
            author.id == int(lottery["owner"])
            or author.id in deputies
            or any(deputy in list(author._roles) for deputy in deputies)
        ):
            lock.release()
            raise commands.CheckFailure()
        if str(member.id) not in cast(Dict[str, int], config[name.lower()]["users"]).keys():
            cast(Dict[str, int], config[name.lower()]["users"])[str(member.id)] = 0
        cast(Dict[str, int], config[name.lower()]["users"])[str(member.id)] += tickets
        await self.config.guild(member.guild).lotteries.set(config)
        lock.release()

    async def tickets_remove(
        self, author: discord.Member, name: str, member: discord.Member, tickets: int = 1
    ) -> None:
        lock: asyncio.Lock = self.config.guild(author.guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            author.guild
        )
        if name.lower() not in config.keys():
            lock.release()
            raise commands.CheckFailure()
        lottery: Dict[str, Union[int, Dict[str, int], List[int]]] = config[name.lower()]
        deputies: List[int] = cast(List[int], lottery["deputies"])
        if not author.guild_permissions.manage_guild and not (
            author.id == int(lottery["owner"])
            or author.id in deputies
            or any(deputy in list(author._roles) for deputy in deputies)
        ):
            lock.release()
            raise commands.CheckFailure()
        if str(member.id) not in cast(Dict[str, int], config[name.lower()]["users"]).keys():
            lock.release()
            raise commands.UserFeedbackCheckFailure(
                (
                    "{} (`{}`) does not have any tickets in the lottery `{}`.".format(
                        member.global_name, member.id, name.lower()
                    )
                )
            )
        if cast(Dict[str, int], config[name.lower()]["users"])[str(member.id)] < tickets:
            lock.release()
            raise commands.UserFeedbackCheckFailure(
                "{} (`{}`) only has {} tickets in the lottery `{}`.".format(
                    member.global_name,
                    member.id,
                    cast(Dict[str, int], config[name.lower()]["users"])[str(member.id)],
                    name.lower(),
                )
            )
        cast(Dict[str, int], config[name.lower()]["users"])[str(member.id)] -= tickets
        await self.config.guild(author.guild).lotteries.set(config)
        lock.release()

    async def tickets_list(self, ctx: commands.GuildContext, name: str) -> List[discord.Embed]:
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            ctx.guild
        )
        if name.lower() not in config.keys():
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        lottery: Dict[str, Union[int, Dict[str, int], List[int]]] = config[name.lower()]
        tickets: Dict[str, int] = cast(Dict[str, int], lottery["users"])
        if not len(tickets) > 0:
            raise commands.UserFeedbackCheckFailure(
                "There are no tickets in the lottery `{}`.".format(name.lower())
            )
        string: str = ""
        for idx, (user_id, ticket) in enumerate(tickets.items()):
            try:
                user: discord.User = await commands.UserConverter().convert(ctx, user_id)
            except commands.UserNotFound:
                data: str = "Unknown User (`{}`)".format(user_id)
            else:
                data: str = "{0.global_name} (`{0.id}`)".format(user)
            string += "{}. {} - **{}**\n".format(idx + 1, data, ticket)
        pages: List[str] = list(pagify(string))
        embeds: List[discord.Embed] = []
        template: discord.Embed = discord.Embed(
            title="Lottery Tickets - {}".format(name.lower()), color=await ctx.embed_color()
        )
        for idx, page in enumerate(pages):
            embed: discord.Embed = template.copy()
            embed.description = page
            embed.set_footer(text="Page {}/{}".format(idx + 1, len(pages)))
            embeds.append(embed)
        return embeds

    async def deputies(self, ctx: commands.GuildContext, name: str) -> List[str]:
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            ctx.guild
        )
        if name.lower() not in config.keys():
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        if not cast(List[int], config[name.lower()]["deputies"]):
            raise commands.UserFeedbackCheckFailure(
                "There are no deputies in the lottery `{}`.".format(name.lower())
            )
        deputies: List[str] = []
        for idx, _id in enumerate(cast(List[int], config[name.lower()]["deputies"])):
            try:
                deputy: Union[discord.Role, discord.Member] = await cast(
                    commands.Converter[Union[discord.Role, discord.Member]], RoleOrUserConverter
                ).convert(ctx, str(_id))
            except commands.BadArgument:
                string: str = "{}. Unknown (`{}`)".format(idx, _id)
            else:
                string: str = "{}. {} (`{}`)".format(idx, deputy.mention, deputy.id)
            deputies.append(string)
        return deputies

    async def deputies_add(
        self, name: str, guild: discord.Guild, elements: Iterable[RoleOrUserConverter]
    ) -> None:
        lock: asyncio.Lock = self.config.guild(guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            guild
        )
        if name.lower() not in config.keys():
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        if len(cast(List[str], config[name.lower()]["deputies"])) >= 20:
            raise commands.UserFeedbackCheckFailure("Cannot have more than 20 deputies.")
        cast(List[str], config[name.lower()]["deputies"]).extend(
            [elem.id for elem in elements if elem not in list(config[name.lower()]["deputies"])]
        )
        await self.config.guild(guild).lotteries.set(config)
        lock.release()

    async def deputies_remove(
        self, name: str, guild: discord.Guild, elements: Iterable[RoleOrUserConverter]
    ) -> None:
        lock: asyncio.Lock = self.config.guild(guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await self.get_guild(
            guild
        )
        if name.lower() not in config.keys():
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        for elem in elements:
            if elem.id in cast(List[int], config[name.lower()]["deputies"]):
                cast(List[int], config[name.lower()]["deputies"]).remove(elem.id)
        await self.config.guild(guild).lotteries.set(config)
        lock.release()
