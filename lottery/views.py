import asyncio
import contextlib
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

import discord
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.embed import randomize_color
from redbot.core.utils.views import SimpleMenu

if TYPE_CHECKING:
    from .core import Lottery


class InteractionSimpleMenu(SimpleMenu):
    @staticmethod
    async def send_from_interaction(
        interaction: discord.Interaction[Red], *args: Any, **kwargs: Any
    ) -> discord.Message:
        if interaction.response.is_done():
            if interaction.is_expired():
                if interaction.channel:
                    return await cast(discord.abc.Messageable, interaction.channel).send(
                        *args, **kwargs
                    )
            delete_after: Optional[int] = kwargs.pop("delete_after", None)
            kwargs["wait"] = True
            message: discord.WebhookMessage = await interaction.followup.send(
                *args, ephemeral=True, **kwargs
            )
            if delete_after is not None:
                await message.delete(delay=delete_after)
            return message
        await interaction.response.send_message(*args, ephemeral=True, **kwargs)
        return await interaction.original_response()

    async def inter(self, interaction: discord.Interaction[Red]) -> None:
        self._fallback_author_to_ctx = False
        self.author: discord.abc.User = interaction.user
        kwargs: Dict[str, Any] = await self.get_page(self.current_page)
        self.message: discord.Message = await self.send_from_interaction(interaction, **kwargs)


class ChangeNameModal(discord.ui.Modal):
    name: discord.ui.TextInput = discord.ui.TextInput(
        label="Name",
        placeholder="Change the name of the lottery.",
        required=True,
        min_length=1,
        max_length=10,
    )

    def __init__(self, view: "LotteryEditView") -> None:
        super().__init__(
            title="Change Lottery Name", custom_id="model:change_name:{}".format(view._message.id)
        )
        self.old: str = view.name
        self.config: Config = view.config
        self.obj: "LotteryEditView" = view

    async def on_submit(self, interaction: discord.Interaction[Red]) -> None:
        lock: asyncio.Lock = self.config.guild(interaction.guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = (
            await self.config.guild(interaction.guild).lotteries()
        )
        if self.old.lower() not in config.keys():
            lock.release()
            await interaction.response.send_message(
                "There's no lottery named `{}`.".format(self.old.lower())
            )
            await self.obj.on_timeout()
            return
        if str(self.name).lower() in config.keys():
            lock.release()
            await interaction.response.send_message(
                "There's already a lottery named `{}`.".format(str(self.name).lower()),
                ephemeral=True,
            )
            return
        data: Dict[str, Union[int, Dict[str, int], List[int]]] = config[self.old.lower()]
        with contextlib.suppress(KeyError):
            del config[self.old.lower()]
        config[str(self.name).lower()] = data
        await self.config.guild(interaction.guild).lotteries.set(config)
        lock.release()
        await interaction.response.send_message(
            "Change lottery name from `{}` to `{}`.".format(
                self.old.lower(), str(self.name).lower()
            ),
            ephemeral=True,
        )


class DeputyView(discord.ui.View):
    def __init__(self, name: str, author: discord.abc.User, *, timeout: float = 120.0) -> None:
        super().__init__(timeout=timeout)
        self.name: str = name

        self._author: discord.abc.User = author
        self._message: discord.Message = discord.utils.MISSING

    def add_fields(
        self, inter: discord.Interaction[Red], embed: discord.Embed, data: List[str]
    ) -> discord.Embed:
        users, roles = [], []
        for d in data:
            obj: Optional[Union[discord.Role, discord.User]] = cast(
                discord.Guild, inter.guild
            ).get_role(int(d))
            if not obj:
                obj: Optional[Union[discord.Role, discord.User]] = inter.client.get_user(int(d))
            if isinstance(obj, discord.User):
                users.append("`{0.id}`: {0.mention}".format(obj))
            elif isinstance(obj, discord.Role):
                roles.append("`{0.id}`: {0.mention}".format(obj))
            else:
                continue
        embed.add_field(
            name="Users",
            value=(
                ustring
                if (
                    ustring := "\n".join(
                        "{}. {}".format(idx, string) for idx, string in enumerate(users)
                    )
                )
                else "No deputy user assigned."
            ),
            inline=False,
        )
        embed.add_field(
            name="Roles",
            value=(
                rstring
                if (
                    rstring := "\n".join(
                        "{}. {}".format(idx, string) for idx, string in enumerate(roles)
                    )
                )
                else "No deputy role assigned."
            ),
            inline=False,
        )
        return embed

    async def on_timeout(self) -> None:
        for item in self.children:
            item: discord.ui.Item["DeputyView"]
            item.disabled = True  # type: ignore
        if self._message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if self._author.id != interaction.user.id:
            await interaction.response.send_message(
                "You're not allowed to use this interaction.", ephemeral=True
            )
            return False
        return True

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Change the deputy users.",
        max_values=10,
    )
    async def deputy_user(
        self, interaction: discord.Interaction[Red], select: discord.ui.UserSelect["DeputyView"]
    ) -> None:
        await interaction.response.defer()
        conf: Config = cast("Lottery", interaction.client.get_cog("Lottery")).config
        lock: asyncio.Lock = conf.guild(interaction.guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await conf.guild(
            interaction.guild
        ).lotteries()
        deputies: List[str] = cast(List[str], config[self.name.lower()]["deputies"])
        if not (vals := select.values):
            return
        for deputy in vals:
            if (d := str(deputy.id)) in deputies:
                deputies.remove(d)
            elif d not in deputies:
                deputies.append(d)
            else:
                await interaction.followup.send(
                    "Something went wrong, try again later.", ephemeral=True
                )
                return
        await conf.guild(interaction.guild).lotteries.set(config)
        lock.release()
        await interaction.followup.send("Made changes successfully!", ephemeral=True)
        embed: discord.Embed = randomize_color(
            discord.Embed(title="Deputies `{}`".format(self.name.lower()))
        )
        embed: discord.Embed = self.add_fields(interaction, embed, deputies)
        await interaction.edit_original_response(embed=embed)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Change the deputy roles",
        max_values=10,
    )
    async def deputy_role(
        self, interaction: discord.Interaction[Red], select: discord.ui.RoleSelect["DeputyView"]
    ) -> None:
        await interaction.response.defer()
        conf: Config = cast("Lottery", interaction.client.get_cog("Lottery")).config
        lock: asyncio.Lock = conf.guild(interaction.guild).lotteries.get_lock()
        await lock.acquire()
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = await conf.guild(
            interaction.guild
        ).lotteries()
        deputies: List[str] = cast(List[str], config[self.name.lower()]["deputies"])
        if not (vals := select.values):
            return
        for deputy in vals:
            if (d := str(deputy.id)) in deputies:
                deputies.remove(d)
            elif d not in deputies:
                deputies.append(d)
            else:
                await interaction.followup.send(
                    "Something went wrong, try again later.", ephemeral=True
                )
                return
        await conf.guild(interaction.guild).lotteries.set(config)
        lock.release()
        await interaction.followup.send("Made changes successfully!", ephemeral=True)
        embed: discord.Embed = randomize_color(
            discord.Embed(title="Deputies `{}`".format(self.name.lower()))
        )
        embed: discord.Embed = self.add_fields(interaction, embed, deputies)
        await interaction.edit_original_response(embed=embed)


class LotteryEditView(discord.ui.View):
    def __init__(
        self, name: str, config: Config, author: discord.abc.User, *, timeout: float = 120.0
    ) -> None:
        super().__init__(timeout=timeout)
        self.name: str = name
        self.config: Config = config

        self._author: discord.abc.User = author
        self._message: discord.Message = discord.utils.MISSING

    async def on_timeout(self) -> None:
        for item in self.children:
            item: discord.ui.Item["LotteryEditView"]
            item.disabled = True  # type: ignore
        if self._message is not discord.utils.MISSING:
            with contextlib.suppress(discord.HTTPException):
                await self._message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if self._author.id != interaction.user.id:
            await interaction.response.send_message(
                "You're not allowed to use this interaction.", ephemeral=True
            )
            return False
        return True

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        placeholder="Change the lottery owner.",
        min_values=1,
        max_values=1,
    )
    async def change_owner(
        self,
        interaction: discord.Interaction[Red],
        select: discord.ui.UserSelect["LotteryEditView"],
    ) -> None:
        await interaction.response.defer()
        lock: asyncio.Lock = self.config.guild(interaction.guild).lotteries.get_lock()
        await lock.acquire()
        owner: discord.abc.User = select.values[0]
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = (
            await self.config.guild(interaction.guild).lotteries()
        )
        if self.name.lower() not in config.keys():
            await self.on_timeout()
            return
        existing: int = int(config[self.name.lower()]["owner"])
        if owner.id == existing:
            await interaction.followup.send(
                "{0.global_name} (`{0.id}`) is already the existing owner.".format(owner),
                ephemeral=True,
            )
            return
        config[self.name.lower()].update(owner=owner.id)
        await self.config.guild(interaction.guild).lotteries.set(config)
        lock.release()
        await interaction.followup.send(
            "Changed owner to {0.global_name} (`{0.id}`).".format(owner), ephemeral=True
        )

    @discord.ui.button(label="Change Lottery Name", style=discord.ButtonStyle.secondary)
    async def change_name(
        self, interaction: discord.Interaction[Red], _: discord.ui.Button["LotteryEditView"]
    ) -> None:
        model: ChangeNameModal = ChangeNameModal(self)
        await interaction.response.send_modal(model)

    @discord.ui.button(label="✖️", style=discord.ButtonStyle.red)
    async def cancel(
        self, interaction: discord.Interaction[Red], _: discord.ui.Button["LotteryEditView"]
    ) -> None:
        if interaction.message:
            with contextlib.suppress(discord.HTTPException):
                await interaction.message.delete()
