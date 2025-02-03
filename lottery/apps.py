from typing import Any, Dict, List, Optional, Union, cast

import discord
from redbot.core import app_commands, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import pagify

from .converters import LotteryTransformer
from .models import LotteryManager
from .views import DeputyView, InteractionSimpleMenu, LotteryEditView


@app_commands.guild_only()
class LotteryGroup(app_commands.Group):
    perms: Dict[str, bool] = {"administrator": True}

    def __init__(self, manager: LotteryManager, **_kwargs: Any) -> None:
        super().__init__(name="lottery", description="Lottery commands.", **_kwargs)
        self.manager: LotteryManager = manager

    @app_commands.default_permissions(**perms)
    @app_commands.command(name="roll", description="Roll tickets from a specific lottery.")
    async def lottery_roll(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ):
        await interaction.response.defer(thinking=True)
        try:
            winner, score, index, tickets = await self.manager.roll(interaction.user, name)
        except commands.UserFeedbackCheckFailure as error:
            return await interaction.followup.send(error.message, ephemeral=True)
        except commands.CheckFailure:
            return await interaction.followup.send(
                "You're not allowed to use this command.", ephemeral=True
            )
        ctx: commands.GuildContext = await commands.GuildContext.from_interaction(interaction)
        user: discord.User = await commands.UserConverter().convert(ctx, winner)
        return await interaction.followup.send(
            embed=discord.Embed(
                title="Winner of {}".format(name.lower()),
                description=("**Selected #{} out of {} lottery tickets.**").format(
                    index + 1, tickets
                ),
                color=await ctx.embed_color(),
                timestamp=ctx.message.created_at,
            )
            .add_field(
                name="Winner",
                value="{user.mention} (`{user.id}`) won with **{score}** tickets.\n".format(
                    user=user, score=score
                ),
                inline=False,
            )
            .set_thumbnail(url=user.display_avatar.url),
        )

    @app_commands.default_permissions(**perms)
    @app_commands.command(name="create", description="Create a lottery.")
    async def lottery_create(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Range[str, 1, 10],
        deputies: bool = False,
    ) -> None:
        ctx: commands.GuildContext = await commands.GuildContext.from_interaction(interaction)
        view: Optional[DeputyView] = DeputyView(name, ctx.author) if deputies else None
        await self.manager.create(author=interaction.user, name=name, deputies=[])
        await interaction.response.send_message(
            "Lottery named `{}` created.".format(name.lower()), view=view
        )
        if view:
            view._message = await interaction.original_response()

    @app_commands.default_permissions(**perms)
    @app_commands.command(name="delete", description="Delete a lottery.")
    async def lottery_delete(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ) -> None:
        await interaction.response.defer()
        await self.manager.delete(guild=interaction.guild, name=name)
        await interaction.followup.send("Deleted lottery `{}`.".format(name.lower()))

    @app_commands.default_permissions(**perms)
    @app_commands.command(name="edit", description="Edit an existing lottery.")
    async def lottery_edit(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ) -> None:
        await interaction.response.defer()
        view: LotteryEditView = LotteryEditView(
            name=name.lower(), config=self.manager.config, author=interaction.user
        )
        await interaction.followup.send(view=view)
        view._message = await interaction.original_response()

    @app_commands.default_permissions(**perms)
    @app_commands.command(name="info", description="Check the info for an existing lottery.")
    async def lottery_info(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ) -> None:
        await interaction.response.defer()
        ctx: commands.GuildContext = await commands.GuildContext.from_interaction(interaction)
        embed: discord.Embed = await self.manager.info(ctx, name)
        await interaction.followup.send(embed=embed)

    lottery_tickets: app_commands.Group = app_commands.Group(
        name="tickets",
        description="Manage lottery tickets.",
        default_permissions=discord.Permissions(manage_messages=True),
    )

    @lottery_tickets.command(name="view", description="View standard tickets info.")
    async def lottery_tickets_view(self, interaction: discord.Interaction[Red]) -> None:
        await interaction.response.defer()
        ctx: commands.GuildContext = await commands.GuildContext.from_interaction(interaction)
        embeds: List[discord.Embed] = await self.manager.tickets(ctx)
        await InteractionSimpleMenu(pages=embeds, disable_after_timeout=True).inter(interaction)

    @lottery_tickets.command(
        name="add", description="Add tickets for a user in a specific lottery."
    )
    async def lottery_tickets_add(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
        member: discord.Member,
        tickets: app_commands.Range[int, 1, 1000] = 1,
    ) -> None:
        await interaction.response.defer()
        await self.manager.tickets_add(interaction.user, name, member, tickets)
        await interaction.followup.send(
            "Added {} ticket{} to {} (`{}`)".format(
                tickets, "" if tickets == 1 else "s", member.global_name, member.id
            )
        )

    @lottery_tickets.command(
        name="remove", description="Remove tickets from a user in a specific lottery."
    )
    async def lottery_tickets_remove(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
        member: discord.Member,
        tickets: app_commands.Range[int, 1, 1000] = 1,
    ) -> None:
        await interaction.response.defer()
        await self.manager.tickets_remove(interaction.user, name, member, tickets)
        await interaction.followup.send(
            "Removed {} ticket{} from {} (`{}`)".format(
                tickets, "" if tickets == 1 else "s", member.global_name, member.id
            )
        )

    @lottery_tickets.command(
        name="list", description="Check the detailed tickets list for a specific lottery."
    )
    async def lottery_tickets_list(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ) -> None:
        await interaction.response.defer()
        ctx: commands.GuildContext = await commands.GuildContext.from_interaction(interaction)
        embeds: List[discord.Embed] = await self.manager.tickets_list(ctx, name)
        await InteractionSimpleMenu(pages=embeds, disable_after_timeout=True).inter(interaction)

    lottery_deputies: app_commands.Group = app_commands.Group(
        name="deputies",
        description="Manage lottery deputies.",
        default_permissions=discord.Permissions(manage_messages=True),
    )

    @lottery_deputies.command(
        name="view", description="View configured deputies for a specific lottery."
    )
    async def lottery_deputies_view(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ) -> None:
        await interaction.response.defer()
        ctx: commands.GuildContext = await commands.GuildContext.from_interaction(interaction)
        deputies: List[str] = await self.manager.deputies(ctx, name)
        pages: List[str] = list(pagify("\n".join(deputies)))
        embeds: List[discord.Embed] = []
        template: discord.Embed = discord.Embed(
            title="Deputies - {}".format(name.lower()), color=await ctx.embed_color()
        )
        for idx, page in enumerate(pages):
            embed: discord.Embed = template.copy()
            embed.description = page
            embed.set_footer(text="Page {}/{}".format(idx, len(pages)))
            embeds.append(embed)
        await InteractionSimpleMenu(pages=embeds, disable_after_timeout=True).inter(interaction)

    @lottery_deputies.command(
        name="set", description="Add or remove deputies from a specific lottery."
    )
    async def lottery_deputies_set(
        self,
        interaction: discord.Interaction[Red],
        name: app_commands.Transform[str, LotteryTransformer],
    ) -> None:
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = (
            await self.manager.get_guild(interaction.guild)
        )
        if name.lower() not in config.keys():
            return await interaction.response.send_message(
                "There's no lottery named `{}`.".format(name.lower())
            )
        deputies: List[int] = cast(List[int], config[name.lower()]["deputies"])
        view: DeputyView = DeputyView(name, interaction.user)
        embed: discord.Embed = view.add_fields(
            interaction,
            discord.Embed(
                title="Deputy `{}`".format(name.lower()),
                color=await interaction.client.get_embed_color(interaction.channel),
            ),
            deputies,
        )
        await interaction.response.send_message(embed=embed, view=view)
