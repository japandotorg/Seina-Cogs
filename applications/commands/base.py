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

from typing import Any, Dict, List, cast

import discord
import TagScriptEngine as tse
from redbot.core.utils import AsyncIter
from redbot.core import app_commands, commands
from redbot.core.utils.chat_formatting import box


from ..abc import PipeMeta
from ..pipes.groups import Groups
from ..common.menus import EmojiMenu
from ..common.utils import name_auto_complete
from ..common.exceptions import ApplicationError
from ..common.views import ApplicationView, DynamicApplyButton
from ..common.models import Application, AppSettings, Buttons
from ..common.tagscript import DEFAULT_SETTINGS_MESSAGE, SettingsAdapter

application: commands.HybridGroup[Any, ..., Any] = cast(
    commands.HybridGroup[Any, ..., Any], Groups.application
)


class SettingCommands(PipeMeta):
    @application.command(name="create", aliases=["+"])
    @app_commands.describe(
        name="short name for the application.",
        description="long name for the application.",
        channel="response channel where the applications will be submitted.",
    )
    async def application_create(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        description: commands.Range[str, 1, 120],
        channel: discord.TextChannel,
    ) -> None:
        """
        Create applications.

        **Arguments:**
        - `name        :` short name for the application. (quotes are needed to use spaces)
        - `description :` long name for the application. (quotes are needed to use spaces)
        - `channel     :` response channel where the applications will be submitted.

        **Examples:**
        - `[p]application create event "event manager" #logging`
        - `[p]application create "dank event" "dank memer event manager" 133251234164375552`
        """
        await ctx.defer()
        try:
            app: Application = await self.manager.create(
                ctx.guild.id, name, description, channel.id
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        embed: discord.Embed = discord.Embed(
            color=discord.Color.from_str((color := app.settings.color)),
            description="**Successfully created a new application.**\n\n"
            + (
                "- **Name**: {name}\n"
                "- **Description**: {description}\n"
                "- **Channel**: {channel} ( `{channel_id}` )\n"
                "- **Color**: {color}\n"
                "- **Cooldown**: {cooldown}\n"
                "- **DM Toggle**: {dm}\n"
                "- **Thread Toggle**: {thread}\n"
            ).format(
                name=name.lower(),
                description=app.description,
                channel=(
                    c.mention
                    if (c := ctx.guild.get_channel(app.settings.channel))
                    else "Unknown Channel ( `{}` )".format(app.settings.channel)
                ),
                channel_id=app.settings.channel,
                color=color,
                cooldown=app.settings.cooldown,
                dm="Enabled" if app.settings.dm else "Disabled",
                thread="Enabled" if app.settings.thread else "Disabled",
            ),
            timestamp=app.settings.time,
        )
        message: discord.Message = await ctx.send(embed=embed)
        await ctx.send(
            "**Message:**\n{message}".format(
                message=box(app.settings.message, lang="json")
            ),
            reference=message.to_reference(fail_if_not_exists=False),
        )

    @application.command(name="delete")
    @app_commands.describe(name="short name of the application")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_delete(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 20]
    ) -> None:
        """
        Delete an existing application.

        **Arguments:**
        - `name :` short name of the application. (quotes are needed to use spaces)
        """
        try:
            await self.manager.delete(ctx.guild.id, name)
        except ApplicationError as exc:
            raise commands.UserFeedbackCheckFailure(exc)
        await ctx.send(
            "Successfully deleted the application named **{}**.".format(
                name.lower()
            )
        )

    @application.command(name="post")
    @app_commands.describe(name="short name of the application")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_post(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 20]
    ) -> None:
        """
        Post an configured application.

        **Arguments:**
        - `name :` short name of the application. (quotes are needed to use spaces)
        """
        try:
            app: Application = await self.manager.get_application(
                ctx.guild.id, name=name.lower()
            )
        except ApplicationError as exc:
            await ctx.send(str(exc), ephemeral=True)
            return
        if not app.questions:
            await ctx.send(
                "No questions configured on this application.", ephemeral=True
            )
            return
        settings: AppSettings = app.settings
        button: Buttons = app.buttons
        kwargs: Dict[str, Any] = await self.manager.process_tagscript(
            settings.message,
            {
                "settings": SettingsAdapter(settings),
                "guild": tse.GuildAdapter(ctx.guild),
                "server": tse.GuildAdapter(ctx.guild),
                "responses": tse.IntAdapter(len(app.responses)),
            },
        )
        if not kwargs:
            await self.manager.edit_setting_for(
                ctx.guild.id,
                name=name.lower(),
                object="message",
                value=DEFAULT_SETTINGS_MESSAGE,
            )
            kwargs: Dict[str, Any] = await self.manager.process_tagscript(
                DEFAULT_SETTINGS_MESSAGE,
                {
                    "settings": SettingsAdapter(settings),
                    "guild": tse.GuildAdapter(ctx.guild),
                    "server": tse.GuildAdapter(ctx.guild),
                    "responses": tse.IntAdapter(len(app.responses)),
                },
            )
        view: ApplicationView = ApplicationView(
            ctx.guild.id,
            name.lower(),
            **{
                "style": DynamicApplyButton.format_style(button.style),
                "label": button.label,
                "emoji": button.emoji,
            },
        )
        await ctx.send(**kwargs, view=view)

    @application.command(
        name="list", aliases=["view", "viewall", "showall", "all"]
    )
    async def application_list(self, ctx: commands.GuildContext) -> None:
        """
        View all configured applications in the current server.
        """
        await ctx.defer()
        apps: List[Application] = await self.manager.get_all_applications(
            ctx.guild.id
        )
        if not apps:
            raise commands.UserFeedbackCheckFailure(
                "There are no configured applications on this server."
            )
        embeds: List[discord.Embed] = []
        async for idx, app in AsyncIter(enumerate(apps)):
            embed: discord.Embed = discord.Embed(
                title="Applications (Page {}/{})".format(idx + 1, len(apps)),
                description=(
                    "**Name**: {name}\n"
                    "**Description**: {description}\n"
                    "**Channel**: {channel}\n"
                    "**Status**: {status}\n\n"
                    "**NOTE: For more info about a specific application, use the "
                    "`{prefix}application config view` command instead.**"
                ).format(
                    name=app.name,
                    description=app.description,
                    channel=(
                        "{0.mention} ({0.id})".format(chan)
                        if (chan := ctx.guild.get_channel(app.settings.channel))
                        else "Unknown Channel {}".format(app.settings.channel)
                    ),
                    status="Submission open"
                    if app.settings.open
                    else "Submission closed",
                    prefix=ctx.clean_prefix,
                ),
                color=discord.Color.from_str(app.settings.color),
                timestamp=app.settings.time,
            )
            embed.set_footer(text="Created at")
            embed.set_thumbnail(url=getattr(ctx.guild.icon, "url", None))
            embeds.append(embed)
        await EmojiMenu(pages=embeds).start(ctx)
