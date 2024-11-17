from typing import Dict, List, Union

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_list, pagify
from redbot.core.utils.views import SimpleMenu

from .abc import MixinMeta
from .converters import RoleOrUserConverter
from .views import LotteryEditView


class Commands(MixinMeta):
    @commands.guild_only()
    @commands.group()
    async def lottery(self, _: commands.Context) -> None:
        """Base command for lottery management."""

    @lottery.command(name="roll")
    async def lottery_roll(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 10]
    ) -> None:
        """Roll tickets from a specific lottery."""
        winner, score, index, tickets = await self.manager.roll(ctx.author, name)
        user: discord.User = await commands.UserConverter().convert(ctx, winner)
        await ctx.send(
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
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.admin_or_permissions(manage_guild=True)
    @lottery.command(name="create")
    async def lottery_create(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 10],
        deputies: commands.Greedy[RoleOrUserConverter] = None,
    ) -> None:
        """Create a lottery."""
        await self.manager.create(author=ctx.author, name=name, deputies=deputies or [])
        await ctx.send(
            "Lottery named `{}` created{}.".format(
                name.lower(),
                (
                    " with deputies {}".format(humanize_list(deputy))
                    if (deputy := [d.name for d in deputies or []])
                    else ""
                ),
            )
        )

    @lottery.command(name="delete")
    @commands.admin_or_permissions(manage_guild=True)
    async def lottery_delete(self, ctx: commands.GuildContext, name: commands.Range[str, 1, 10]):
        """Delete a lottery."""
        await self.manager.delete(guild=ctx.guild, name=name)
        await ctx.send("Deleted lottery `{}`.".format(name.lower()))

    @lottery.command(name="edit")
    @commands.admin_or_permissions(manage_guild=True)
    async def lottery_edit(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 10],
    ):
        """Edit an existing lottery."""
        config: Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]] = (
            await self.manager.get_guild(ctx.guild)
        )
        if name.lower() not in config.keys():
            raise commands.UserFeedbackCheckFailure(
                "There's no lottery named `{}`.".format(name.lower())
            )
        view: LotteryEditView = LotteryEditView(
            name=name.lower(), config=self.config, author=ctx.author
        )
        view._message = await ctx.send(view=view)

    @lottery.command(name="info")
    @commands.admin_or_permissions(manage_guild=True)
    async def lottery_info(self, ctx: commands.Context, name: str) -> None:
        """Check the info for an existing lottery."""
        embed: discord.Embed = await self.manager.info(ctx, name)
        await ctx.send(embed=embed)

    @lottery.group(name="tickets", invoke_without_command=True)
    async def lottery_tickets(self, ctx: commands.GuildContext) -> None:
        """View standard tickets info."""
        if not ctx.invoked_subcommand:
            embeds: List[discord.Embed] = await self.manager.tickets(ctx)
            await SimpleMenu(pages=embeds, disable_after_timeout=True).start(ctx)

    @lottery_tickets.command(name="add")
    async def lottery_tickets_add(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 10],
        member: discord.Member,
        tickets: commands.Range[int, 1, 1000] = 1,
    ) -> None:
        """Add tickets for a user in a specific lottery."""
        await self.manager.tickets_add(ctx.author, name, member, tickets)
        await ctx.send(
            "Added {} ticket{} to {} (`{}`).".format(
                tickets, "" if tickets == 1 else "s", member.global_name, member.id
            )
        )

    @lottery_tickets.command(name="remove")
    async def lottery_tickets_remove(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 10],
        member: discord.Member,
        tickets: commands.Range[int, 1, 1000] = 1,
    ) -> None:
        """Remove tickets from a user in a specific lottery."""
        await self.manager.tickets_remove(ctx.author, name, member, tickets)
        await ctx.send(
            "Removed {} ticket{} from {} (`{}`).".format(
                tickets, "" if tickets == 1 else "s", member.global_name, member.id
            )
        )

    @lottery_tickets.command(name="list")
    async def lottery_tickets_list(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 10]
    ) -> None:
        """Check the detailed tickets list for a specific lottery."""
        embeds: List[discord.Embed] = await self.manager.tickets_list(ctx, name)
        await SimpleMenu(pages=embeds, disable_after_timeout=True).start(ctx)

    @commands.admin_or_permissions(manage_guild=True)
    @lottery.group(name="deputies", invoke_without_command=True)
    async def lottery_deputies(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 10]
    ) -> None:
        """View configured deputies for a specific lottery."""
        if not ctx.invoked_subcommand:
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
            await SimpleMenu(pages=embeds, disable_after_timeout=True).start(ctx)

    @lottery_deputies.command(name="add")  # type: ignore
    async def lottery_deputies_add(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 10],
        deputies: commands.Greedy[RoleOrUserConverter],
    ) -> None:
        """Add deputies to a specific lottery."""
        await self.manager.deputies_add(name=name, guild=ctx.guild, elements=deputies)
        await ctx.send(
            "Added {} as deputy for `{}`.".format(
                humanize_list([deputy.name for deputy in deputies]), name.lower()
            )
        )

    @lottery_deputies.command(name="remove")  # type: ignore
    async def lottery_deputies_remove(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 10],
        deputies: commands.Greedy[RoleOrUserConverter],
    ) -> None:
        """Remove deputies from a specific lottery."""
        await self.manager.deputies_remove(name=name, guild=ctx.guild, elements=deputies)
        await ctx.send(
            "Removed {} from deputy of `{}`.".format(
                humanize_list([deputy.name for deputy in deputies]), name.lower()
            )
        )
