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

import contextlib
import functools
from typing import Any, Callable, Dict, Literal, Optional, Union, cast

import discord
from redbot.core import app_commands, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box

from ..abc import PipeMeta
from ..common.exceptions import ApplicationError
from ..common.finders import EmojiFinder
from ..common.models import Application, AppSettings
from ..common.utils import name_auto_complete
from ..common.views import ChooseChoicesModal
from ..pipes.groups import Groups

application_config: commands.HybridGroup[Any, ..., Any] = cast(
    commands.HybridGroup[Any, ..., Any], Groups.application_config
)


class ConfigCommands(PipeMeta):
    @application_config.command(name="channel", aliases=["responsechannel"])
    @app_commands.describe(name="short name of the application", channel="the response channel")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_channel(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        channel: discord.TextChannel,
    ) -> None:
        """
        Edit the response logging channel for the specific application.

        **Arguments:**
        - `name    :` short name of the application. (quotes are needed to use spaces)
        - `channel :` the new response channel. (quotes are needed to use spaces)

        **Examples:**
        - `[p]application config channel "event manager" #logging`
        """
        try:
            await self.manager.edit_setting_for(
                ctx.guild.id, name=name, object="channel", value=channel.id
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(error)
        await ctx.send(
            "Successfully changed the response channel to {} ( `{}` ).".format(
                channel.mention, channel.id
            )
        )

    @application_config.command(name="message")
    @app_commands.describe(name="short name of the application", message="the new post message")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_message(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        *,
        message: str,
    ) -> None:
        """
        Edit the application post message.

        **Arguments:**
        - `name    :` short name of the application. (quotes are needed to use spaces)
        - `message :` the new post message.

        **Examples:**
        ```json
        [p]application config message "event manager" {embed({
            "title": "{settings(description)}",
            "color": "{settings(color)}",
            "description": "Fill this application to apply as a {settings(name)} in {guild(name)}.",
            "footer": {
                "text": "Click below to apply to this application!"
            },
            "fields": [
                {
                    "name": "Response Count",
                    "value": "{responses}",
                    "inline": false
                }
            ]
        })}
        ```
        """
        try:
            await self.manager.edit_setting_for(
                ctx.guild.id, name=name, object="message", value=message
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(error)
        await ctx.send(
            "Successfully changed the application message to -\n{}".format(
                box(message, lang="json")
            )
        )

    @application_config.command(name="color")
    @app_commands.describe(
        name="short name of the application",
        color='the new embed color (formats - `0x2f33136`, `#2f3136`, or `"rgb(47, 49, 54)`)"',
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_color(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        color: str,
    ) -> None:
        """
        Edit the application embed color.

        **Arguments:**
        - `name  :` short name of the application. (quotes are needed to use spaces)
        - `color :` the new embed color. (formats - `0x2f33136`, `#2f3136`, or `rgb(47, 49, 54)`)

        **Examples:**
        - `[p]application config color event #2f3136`
        - `[p]application config color "event manager" "rgb(47, 49, 54)`)"`
        """
        try:
            discord_color: discord.Color = discord.Color.from_str(color)
        except ValueError:
            raise commands.UserFeedbackCheckFailure(
                "Couldn't convert `{}` to a valid color.".format(color)
            )
        await self.manager.edit_setting_for(ctx.guild.id, name=name, object="color", value=color)
        await ctx.send(
            embed=discord.Embed(
                description="Successfully changed the application color to `{}`.".format(color),
                color=discord_color,
            )
        )

    @application_config.command(name="status")
    @app_commands.describe(
        name="short name of the application",
        status="new status of the application (open or close)",
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_status(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        status: Literal["open", "close"],
    ) -> None:
        """
        Open/Close a specific application.

        **Arguments:**
        - `name   :` short name of the application. (quotes are needed to use spaces)
        - `status :` new status of the application. ("open" or "close")

        **Examples:**
        - `[p]application config status "event manager" close`
        """
        try:
            await self.manager.edit_setting_for(
                ctx.guild.id,
                name=name,
                object="open",
                value=True if status.lower() == "open" else False,
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(error)
        await ctx.send(
            "Successfully {} submissions for the application named **{}**.".format(
                "opened" if status.lower() == "open" else "closed", name.lower()
            )
        )

    @application_config.command(name="thread", aliases=["threads"])
    @app_commands.describe(
        name="short name of the application",
        toggle="enable or disable thread creation",
        custom="add custom name for the threads",
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_thread(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        toggle: bool,
        custom: Optional[commands.Range[str, 1, 30]] = None,
    ) -> None:
        """
        Enable/Disable thread creation on response messages.

        **Arguments:**
        - `name   :` short name of the application. (quotes are needed to use spaces)
        - `toggle :` enable or disable thread creation.
        - `custom :` add a custom name for the threads. (quotes are needed to use spaces)

        **Examples:**
        - `[p]application config thread manager true`
        - `[p]application config thread "event manager" true {member(name)}`
        """
        try:
            await self.manager.edit_thread_settings(
                ctx.guild.id, name=name, toggle=toggle, value=custom
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(error)
        await ctx.send(
            "Ok I'll {} threads on responses for the **{}** application from now.".format(
                "open" if toggle else "not open", name.lower()
            )
        )

    @application_config.command(name="notifications", aliases=["notifs", "notif"])
    @app_commands.describe()
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_notifications(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        type: Literal["toggle", "content", "channel", "users", "roles", "everyone"],
        *,
        value: commands.Range[str, 1],
    ) -> None:
        """
        Edit the notification settings for a specific application.

        **Arguments:**
        - `name  :` short name of the application. (quotes are needed to use spaces)
        - `type  :` what part of the notification settings to configure.
        - `value :` value of the said configuration type.

        **Note:**
        - users, roles and everyone are of boolean type & are for managing the mentions of the notification message.
        - the type **channel** is for sending notification messages to additional channels..
        - for multiple channels separate **channel ids** by `,`. (only channel ids allowed/supported)

        **Examples:**
        - `[p]application config notifications "event manager" toggle true`
        - `[p]application config notifications "event manager" users/roles/everyone true`
        -
        ```json
        [p]application config notifications "event manager" content {embed({
            "description": "New application submitted by {member(name)} for application **{app}** with response id {id}",
            "color": "{color}"
        })}
        ```
        """
        try:
            await self.manager.edit_notification_settings(
                ctx.guild.id, name=name.lower(), type=type.lower(), value=value
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(error)
        await ctx.tick()

    @application_config.command(name="button", aliases=["buttons"])
    @app_commands.describe(
        name="short name of the application",
        type="what part of the button to configure",
        value="value of the said configuration type",
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_buttons(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        type: Literal["label", "emoji", "style", "boolean"],
        value: Optional[str] = None,
    ) -> None:
        """
        Edit the application buttons.

        **Arguments:**
        - `name  :` short name of the application. (quotes are needed to use spaces)
        - `type  :` what part of the button to configure.
        - `value :` value of the said configuration type.

        **Note:**
        - label, emoji or style are for the application post message. (see `[p]app post` command)
        - boolean is for configuring the buttons related to the boolean (True or False) question type. (see the `[p]app question` commands)

        **Examples:**
        - `[p]application config button "event manager" boolean`
        - `[p]application config button "event manager" emoji :myappemoji:`
        - `[p]application config button "event manager" label "Click Here To Apply!"`
        """
        if type.lower() == "boolean":
            app: Application = await self.manager.get_application(ctx.guild.id, name=name.lower())
            modal: ChooseChoicesModal = ChooseChoicesModal(ctx.author, application=app)
            view: discord.ui.View = discord.ui.View(timeout=120.0)
            view.on_timeout = lambda: modal.tfn(view)
            button: discord.ui.Button[discord.ui.View] = discord.ui.Button(
                label="Configure", style=discord.ButtonStyle.green
            )

            @staticmethod
            async def clbk(_: discord.ui.View, interaction: discord.Interaction[Red]) -> None:
                await interaction.response.send_modal(modal)

            button.callback = functools.partial(clbk, button)
            view.add_item(button)
            embed: discord.Embed = discord.Embed(
                description=(
                    "**Click on the **Configure** button to edit the "
                    "**boolean** button for the questions of the **{}** application.**"
                ).format(name.lower()),
                color=discord.Color.from_str(app.settings.color),
            )
            message: discord.Message = await ctx.send(embed=embed, view=view)
            setattr(view, "_message", message)
        else:
            if not value:
                raise commands.UserFeedbackCheckFailure(
                    "Value is a required argument for type **{}**.".format(type.lower())
                )
            if type.lower() == "emoji":
                value: str = str(await EmojiFinder().convert(ctx, value))
            app: Application = await self.manager.edit_button_settings(
                ctx.guild.id, name=name, object=type.lower(), value=value
            )
            await ctx.send(
                embed=discord.Embed(
                    description=(
                        "Configured {value} as the value of "
                        "**{object}** for the **{name}** application."
                    ).format(value=value, object=type.lower(), name=name.lower())
                ),
                color=discord.Color.from_str(app.settings.color),
            )

    @application_config.command(name="view", aliases=["ss", "show", "settings", "showsettings"])
    @app_commands.describe(name="short name of the application")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_config_view(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 20]
    ) -> None:
        """
        Show configuration settings for the specific application.

        **Arguments:**
        - `name :` short name of the application. (quotes are needed to use spaces)
        """
        await ctx.defer()
        try:
            app: Application = await self.manager.get_application(ctx.guild.id, name=name.lower())
        except ApplicationError as exc:
            raise commands.UserFeedbackCheckFailure(str(exc))
        settings: AppSettings = app.settings
        description: str = (
            "**Name**: {name}\n"
            "**Description**: {description}\n"
            "**Channel**: {channel}\n"
            "**Color**: {color}\n"
            "**Status**: {status}\n"
            "**__Thread__**:\n"
            "- **toggle**: {thread}\n"
            "- **message**:\n"
            "{message}\n"
        ).format(
            name=settings.name,
            description=settings.description,
            channel=(
                "{0.mention} (`{0.id}`)".format(chan)
                if (chan := ctx.guild.get_channel(settings.channel))
                else "unknown channel {}".format(settings.channel)
            ),
            color=settings.color,
            status="submission open" if settings.open else "submission closed",
            thread="enabled" if settings.thread.toggle else "disabled",
            message=box(settings.thread.custom, lang="json"),
        )
        embed: discord.Embed = discord.Embed(
            title="Application Config",
            description=description,
            timestamp=settings.time,
            color=discord.Color.from_str(settings.color),
        )
        embed.add_field(
            name="**__Button Settings__**",
            value=("**Label**: {label}\n**Emoji**: {emoji}\n**Style**: {style}").format(
                label=label if (label := app.buttons.label) else "no label configured",
                emoji=app.buttons.emoji,
                style=app.buttons.style,
            ),
            inline=False,
        )
        embed.add_field(
            name="**__Boolean Button Settings__**",
            value=("**__True__**:\n- {yl}\n- {ye}\n\n" "**__False__**:\n- {nl}\n- {ne}\n").format(
                yl=label if (label := app.buttons.choice.yes.label) else "no label configured",
                ye=app.buttons.choice.yes.emoji,
                nl=label if (label := app.buttons.choice.no.label) else "no label configured",
                ne=app.buttons.choice.no.emoji,
            ),
            inline=False,
        )
        embed.add_field(
            name="**__Notification Settings__**",
            value="**Toggle**: {status}\n**Channels**: {channels}\n".format(
                status="enabled" if (notifs := settings.notifications).toggle else "disabled",
                channels=(
                    ", ".join(
                        (
                            "{1}. {0.mention} (`{0.id}`)".format(channel, idx)
                            if (channel := ctx.guild.get_channel(c))
                            else "Unknown Channel (`{}`)".format(c)
                        )
                        for idx, c in enumerate(channels[:4])
                    )
                    + ("..." if len(channels) > 4 else "")
                    if (channels := list(notifs.channels))
                    else "no additional channels configured"
                ),
            ),
        )
        embed.set_thumbnail(url=getattr(ctx.guild.icon, "url", None))
        embed.set_footer(text="Created at")
        kwargs: Callable[  # noqa: E731
            [discord.Message],
            Dict[str, Union[discord.MessageReference, discord.AllowedMentions]],
        ] = lambda m: {
            "reference": m.to_reference(fail_if_not_exists=False),
            "allowed_mentions": discord.AllowedMentions.none(),
        }
        view: discord.ui.View = discord.ui.View(timeout=120.0)

        @staticmethod
        async def tfn(self: discord.ui.View) -> None:
            for item in self.children:
                item: discord.ui.Item[discord.ui.View]
                item.disabled = True  # pyright: ignore[reportAttributeAccessIssue]
            with contextlib.suppress(discord.HTTPException):
                await cast(
                    discord.Message,
                    self._message,  # pyright: ignore[reportAttributeAccessIssue]
                ).edit(view=self)

        view.on_timeout = lambda: tfn(view)
        select: discord.ui.ChannelSelect[discord.ui.View] = discord.ui.ChannelSelect(
            channel_types=[discord.ChannelType.text],
            placeholder="edit the response logging channel!",
        )

        @staticmethod
        async def ichk(
            _: discord.ui.ChannelSelect[discord.ui.View],
            interaction: discord.Interaction[Red],
            /,
        ) -> bool:
            if await interaction.client.is_admin(interaction.user):
                return True
            await interaction.response.send_message(
                "You're not allowed to use this interaction!", ephemeral=True
            )
            return False

        select.interaction_check = functools.partial(ichk, select)

        @staticmethod
        async def clbk(
            item: discord.ui.ChannelSelect[discord.ui.View],
            interaction: discord.Interaction[Red],
        ) -> None:
            chan: Union[app_commands.AppCommandChannel, app_commands.AppCommandThread] = (
                item.values[0]
            )
            settings.channel = item.values[0].id
            async with self.config.guild(ctx.guild).apps() as apps:
                apps.update(**{app.name.lower(): app.model_dump(mode="python")})
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Application - **{}**".format(app.name.lower()),
                    description="Configured {} (`{}`) as the new response logging channel.".format(
                        chan.mention, chan.id
                    ),
                    color=discord.Color.from_str(settings.color),
                    timestamp=discord.utils.utcnow(),
                )
                .set_thumbnail(url=getattr(ctx.guild.icon, "url", None))
                .set_footer(text="edited at")
            )

        select.callback = functools.partial(clbk, select)
        view.add_item(select)

        message: discord.Message = await ctx.send(embed=embed, **kwargs(ctx.message), view=view)
        await ctx.send(
            "**Post Message:**\n" + box(app.settings.message, lang="json"),
            **kwargs(message),
        )
        await ctx.send(
            "**Notification Message:**\n" + box(notifs.content, lang="json"),
            **kwargs(message),
        )
