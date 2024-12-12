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

from typing import Any, List, Optional, cast

import discord
from redbot.core import commands, app_commands
from redbot.core.utils.chat_formatting import box

from ..abc import PipeMeta
from ..pipes.groups import Groups
from ..common.menus import EmojiMenu
from ..common.utils import name_auto_complete
from ..common.views import QuestionChoicesView
from ..common.models import Application, Types
from ..common.exceptions import ApplicationError


application_question: commands.HybridGroup[Any, ..., Any] = cast(
    commands.HybridGroup, Groups.application_question
)


class QuestionCommands(PipeMeta):

    @application_question.command(name="add", aliases=["create", "+"])
    @app_commands.describe(
        name="short name of the application",
        question="the question (can only be 350 characters long)",
        type="the answer type (text, boolean or choices)",
        required="if the question is required or not",
        position="position of the question",
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_question_add(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        question: commands.Range[str, 1, 350],
        type: Types = "text",
        required: bool = True,
        position: int = 0,
    ) -> None:
        """
        Add questions to a specific application.

        **Arguments:**
        - `name     :` short name of the application. (quotes are needed to use spaces)
        - `question :` the question. (quotes are needed to use spaces)
        - `type     :` the answer type (text, boolean or choices)
        - `required :` if the question is required or not.
        - `position  :` position of the question.

        **Examples:**
        - `[p]application question add "event manager" "what is your name" text false 2`
        - `[p]application question add event "what's your age" choices true 1`
        - `[p]application question add event "you good?" boolean`
        """
        await ctx.defer()
        if type.lower() not in list(Types.__args__):
            raise commands.UserFeedbackCheckFailure("Invalid type.")
        try:
            app, ques = await self.manager.question_add(
                ctx.guild.id,
                name=name,
                question=question,
                type=type,
                required=required,
                position=position,
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        position: int = (
            position
            if position > 0
            else (len(app.questions) + 1 if type.lower() == "choices" else len(app.questions))
        )
        embed: discord.Embed = discord.Embed(
            title="New Question Added!",
            description=(
                "- **Application**: {name}\n"
                "- **Question**: {question}\n"
                "- **Type**: {type}\n"
                "- **Required**: {required}\n"
                "- **Position**: {position}\n"
            ).format(
                name=name.lower(),
                question=question,
                type=type,
                required=required,
                position=position,
            ),
            color=discord.Color.from_str(app.settings.color),
            timestamp=discord.utils.utcnow(),
        )
        (
            embed.add_field(
                name="**NOTICE**",
                value=(
                    "- Make sure to click on the **Choices** button to configure the choices, "
                    "this question will be suspended otherwise."
                ),
                inline=False,
            )
            if type.lower() == "choices"
            else False
        )
        view: Optional[QuestionChoicesView] = (
            QuestionChoicesView(ctx.author, position=position, application=app, question=ques)
            if type.lower() == "choices"
            else None
        )
        message: discord.Message = await ctx.send(embed=embed, view=view)
        if view:
            view._message = message

    @application_question.command(name="remove", aliases=["delete", "-"])
    @app_commands.describe(
        name="short name of the application", position="position of the question"
    )
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_question_remove(
        self,
        ctx: commands.GuildContext,
        name: commands.Range[str, 1, 20],
        position: commands.Range[int, 1, 10],
    ) -> None:
        """
        Delete a specific question from a specific application.

        **Arguments:**
        - `name     :` short name of the application. (quotes are needed to use spaces)
        - `position :` position of the application.

        **Examples:**
        - `[p]application question remove "event manager" 3`
        """
        await ctx.defer()
        try:
            app, ques = await self.manager.question_remove(
                ctx.guild.id, name=name, position=position
            )
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        embed: discord.Embed = discord.Embed(
            title="Question Removed!",
            description=(
                "- **Application**: {name}\n"
                "- **Question**: {question}\n"
                "- **Type**: {type}\n"
                "- **Required**: {required}\n"
                "- **Position**: {position}\n"
            ).format(
                name=name.lower(),
                question=ques.text,
                type=ques.type,
                required=ques.required,
                position=position,
            ),
            color=discord.Color.from_str(app.settings.color),
        )
        (
            embed.add_field(
                name="Choices:",
                value=box(
                    "\n".join(
                        [
                            "{}. {}".format(idx + 1, answer)
                            for idx, answer in enumerate(ques.choices)
                        ]
                    ),
                    lang="sml",
                )
                + "\n- **Other**: {}".format(ques.other),
            )
            if len(ques.choices) > 0
            else False
        )
        await ctx.send(embed=embed)

    @application_question.command(name="list", aliases=["view", "all"])
    @app_commands.describe(name="short name of the application")
    @app_commands.autocomplete(name=name_auto_complete)
    async def application_question_list(
        self, ctx: commands.GuildContext, name: commands.Range[str, 1, 20]
    ) -> None:
        """
        Show the questions for a specific application.

        **Arguments:**
        - `name     :` short name of the application. (quotes are needed to use spaces)
        """
        try:
            app: Application = await self.manager.get_application(ctx.guild.id, name=name)
        except ApplicationError as error:
            raise commands.UserFeedbackCheckFailure(str(error))
        if len(app.questions) < 1:
            raise commands.UserFeedbackCheckFailure(
                "There are no questions configured in this application."
            )
        embeds: List[discord.Embed] = []
        for idx, question in enumerate(app.questions):
            embed: discord.Embed = discord.Embed(
                title="Questions",
                description=(
                    "- **Application**: {name}\n"
                    "- **Question**: {text}\n"
                    "- **Type**: {type}\n"
                    "- **Required**: {required}\n"
                ).format(
                    name=name.lower(),
                    text=question.text,
                    type=question.type,
                    required=question.required,
                ),
                color=discord.Color.from_str(app.settings.color),
            )
            embed.set_footer(text="Position: {}/{}".format(idx + 1, len(app.questions)))
            (
                embed.add_field(
                    name="**Choices**:",
                    value=box(
                        "\n".join(
                            [
                                "{}. {}".format(idx + 1, answer)
                                for idx, answer in enumerate(question.choices)
                            ]
                        ),
                        lang="sml",
                    )
                    + "\n- **Other**: {}".format(question.other),
                )
                if len(question.choices) > 0
                else False
            )
            embeds.append(embed)
        await EmojiMenu(pages=embeds).start(ctx)
