"""
MIT License

Copyright (c) 2024-present japandotorg

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

from typing import Any, List, Literal, cast

import discord
from redbot.core import app_commands, commands
from redbot.core.utils.chat_formatting import pagify

from ..abc import PipeMeta
from ..common.exceptions import ApplicationError
from ..common.menus import EmojiMenu
from ..common.models import Application
from ..common.utils import name_auto_complete
from ..pipes.groups import Groups

application_role: commands.HybridGroup[Any, ..., Any] = cast(
    commands.HybridGroup, Groups.application_role
)


class RoleCommands(PipeMeta):

    @application_role.command(name="whitelist", aliases=["allowlist", "wl"])
    @app_commands.describe(
        add_or_remove="add or remove from the whitelist",
        name="short name of the application",
        roles="list of roles separated by spaces",
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_role_whitelist(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        name: commands.Range[str, 1, 20],
        roles: commands.Greedy[discord.Role],
    ) -> None:
        """
        Manage the whitelist for a specific application. (using a whitelist will suppress the blacklist)

        **Arguments:**
        - `add_or_remove :` add or remove from the whitelist.
        - `name          :` short name of the application. (quotes are needed to use spaces)
        - `roles         :` list of roles separated by spaces.
        """
        try:
            app: Application = await self.manager.get_application(ctx.guild.id, name=name)
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        whitelist: List[int] = app.roles.whitelist
        if add_or_remove.lower() == "add":
            for role in roles:
                if role.id not in whitelist:
                    app.roles.whitelist.append(role.id)
        elif add_or_remove.lower() == "remove":
            for role in roles:
                if role.id in whitelist:
                    app.roles.whitelist.remove(role.id)
        else:
            raise commands.UserFeedbackCheckFailure()
        async with self.config.guild(ctx.guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        await ctx.send(
            "Successfully {} {} role{} {} the application's whitelist.".format(
                len(roles),
                "added" if add_or_remove.lower() == "add" else "removed",
                "s" if len(roles) > 1 else "",
                "to" if add_or_remove.lower() == "add" else "from",
            )
        )

    @application_role.command(name="blacklist", aliases=["blocklist", "bl"])
    @app_commands.describe(
        add_or_remove="add or remove from the blacklist",
        name="short name of the application",
        roles="list of roles separated by spaces",
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_role_blacklist(
        self,
        ctx: commands.GuildContext,
        add_or_remove: Literal["add", "remove"],
        name: commands.Range[str, 1, 20],
        roles: commands.Greedy[discord.Role],
    ) -> None:
        """
        Manage the blacklist for a specific application.

        **Arguments:**
        - `add_or_remove :` add or remove from the blacklist.
        - `name          :` short name of the application. (quotes are needed to use spaces)
        - `roles         :` list of roles separated by spaces.
        """
        try:
            app: Application = await self.manager.get_application(ctx.guild.id, name=name)
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        blacklist: List[int] = app.roles.blacklist
        if add_or_remove.lower() == "add":
            for role in roles:
                if role.id not in blacklist:
                    app.roles.blacklist.append(role.id)
        elif add_or_remove.lower() == "remove":
            for role in roles:
                if role.id in blacklist:
                    app.roles.blacklist.remove(role.id)
        else:
            raise commands.UserFeedbackCheckFailure()
        async with self.config.guild(ctx.guild).apps() as apps:
            apps.update(**{name.lower(): app.model_dump(mode="python")})
        await ctx.send(
            "Successfully {} {} role{} {} the application's blacklist.".format(
                len(roles),
                "added" if add_or_remove.lower() == "add" else "removed",
                "s" if len(roles) > 1 else "",
                "to" if add_or_remove.lower() == "add" else "from",
            )
        )

    @application_role.command(name="view", aliases=["list"])
    @app_commands.describe(item="whitelist or blacklist", name="short name of the application")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_role_view(
        self,
        ctx: commands.GuildContext,
        item: Literal["whitelist", "blacklist"],
        name: commands.Range[str, 1, 20],
    ) -> None:
        """
        View the whitelist or the blacklist.

        **Arguments:**
        - `item :` whitelist or blacklist.
        - `name :` short name of the application. (quotes are needed to use spaces)
        """
        try:
            app: Application = await self.manager.get_application(ctx.guild.id, name=name)
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        if item.lower() == "whitelist":
            whitelist: List[int] = app.roles.whitelist
            if not whitelist:
                raise commands.UserFeedbackCheckFailure(
                    "There are no whitelisted roles for this application."
                )
            roles: str = "\n".join(
                "{}. <@&{}>".format(idx + 1, role) for idx, role in enumerate(whitelist)
            )
            pages: List[str] = list(pagify(roles))
            embeds: List[discord.Embed] = []
            for idx, page in enumerate(pages):
                embed: discord.Embed = discord.Embed(
                    description=page,
                    title="Application Whitelist - **{}**".format(name.lower()),
                    color=discord.Color.from_str(app.settings.color),
                )
                embed.set_footer(text="Page {}/{}".format(idx + 1, len(pages)))
                embeds.append(embed)
            await EmojiMenu(pages=embeds).start(ctx)
        elif item.lower() == "blacklist":
            blacklist: List[int] = app.roles.blacklist
            if not blacklist:
                raise commands.UserFeedbackCheckFailure(
                    "There are no blacklisted roles for this application."
                )
            roles: str = "\n".join(
                "{}. <@&{}>".format(idx + 1, role) for idx, role in enumerate(blacklist)
            )
            pages: List[str] = list(pagify(roles))
            embeds: List[discord.Embed] = []
            for idx, page in enumerate(pages):
                embed: discord.Embed = discord.Embed(
                    description=page,
                    title="Application Blacklist - **{}**".format(name.lower()),
                    color=discord.Color.from_str(app.settings.color),
                )
                embed.set_footer(text="Page {}/{}".format(idx + 1, len(pages)))
                embeds.append(embed)
            await EmojiMenu(pages=embeds).start(ctx)
        else:
            raise commands.UserFeedbackCheckFailure()
