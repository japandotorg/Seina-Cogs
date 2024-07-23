import datetime
from typing import Any, Dict, List, Optional

import discord
from redbot.core import commands

from ..abc import MixinMeta
from ..converters import TagConverter
from ..errors import TagFeedbackError
from ..objects import Tag
from .utils import WEB_CONTENT, dashboard_page, get_tags_cog


class DashboardMixin(MixinMeta):
    @commands.Cog.listener()
    async def on_dashboard_cog_add(self, dashboard_cog: commands.Cog):
        dashboard_cog.rpc.third_parties_handler.add_third_party(self)

    async def get_dashboard_page(
        self, user: discord.User, guild: Optional[discord.Guild], **kwargs: Any
    ) -> Dict[str, Any]:
        import wtforms
        from markupsafe import Markup

        class MarkdownTextAreaField(wtforms.TextAreaField):
            def __call__(
                self,
                disable_toolbar: bool = False,
                **kwargs: Any,
            ) -> Markup:
                if "class" not in kwargs:
                    kwargs["class"] = "markdown-text-area-field"
                else:
                    kwargs["class"] += " markdown-text-area-field"
                if disable_toolbar:
                    kwargs["class"] += " markdown-text-area-field-toolbar-disabled"
                return super().__call__(**kwargs)

        class TagForm(kwargs["Form"]):
            tag_name: wtforms.StringField = wtforms.StringField(
                "Name",
                validators=[
                    wtforms.validators.InputRequired(),
                    wtforms.validators.Regexp(r"^[^\s]+$"),
                    wtforms.validators.Length(max=300),
                ],
            )
            tagscript: MarkdownTextAreaField = MarkdownTextAreaField(
                "Script",
                validators=[
                    wtforms.validators.InputRequired(),
                    wtforms.validators.Length(max=1700),
                    kwargs["DpyObjectConverter"](TagConverter),
                ],
            )

        class TagsForm(kwargs["Form"]):
            tags: wtforms.FieldList = wtforms.FieldList(wtforms.FormField(TagForm))
            submit: wtforms.SubmitField = wtforms.SubmitField("Save Modifications")

            def __init__(self, tags: Dict[str, str]) -> None:
                super().__init__(prefix="tags_form_")
                for name, tagscript in tags.items():
                    self.tags.append_entry(
                        {
                            "tag_name": name,
                            "tagscript": tagscript,
                        }
                    )
                self.tags.default = [
                    entry for entry in self.tags.entries if entry.csrf_token.data is None
                ]
                self.tags.entries = [
                    entry for entry in self.tags.entries if entry.csrf_token.data is not None
                ]

        if guild is not None:
            existing_tags: Dict[str, Tag] = self.guild_tag_cache[guild.id].copy()
        else:
            existing_tags: Dict[str, Tag] = self.global_tag_cache.copy()
        tags_form: TagsForm = TagsForm(
            {
                tag.name: tag.tagscript
                for tag in sorted(existing_tags.values(), key=lambda tag: tag.name)
            }
        )
        if tags_form.validate_on_submit() and await tags_form.validate_dpy_converters():
            tags: Dict[Any, Any] = {
                tag.tag_name.data: tag.tagscript.data for tag in tags_form.tags
            }
            for tag_name, tagscript in tags.items():
                if tag_name not in existing_tags:
                    try:
                        await self.validate_tag_count(guild)
                    except TagFeedbackError as error:
                        return {
                            "status": 1,
                            "notifications": [
                                {
                                    "message": str(error),
                                    "category": "warning",
                                }
                            ],
                        }
                    tag: Tag = get_tags_cog(
                        self.bot,
                        tag_name,
                        tagscript,
                        guild_id=guild.id if guild is not None else None,
                        author_id=user.id,
                        created_at=datetime.datetime.now(tz=datetime.timezone.utc),
                    )
                    await tag.initialize()
                elif tagscript != existing_tags[tag_name].tagscript:
                    await existing_tags[tag_name].edit_tagscript(tagscript)
            for tag_name in existing_tags:
                if tag_name not in tags:
                    await existing_tags[tag_name].delete()
            return {
                "status": 0,
                "notifications": [
                    {
                        "message": "Successfully saved the modifications.",
                        "category": "success",
                    }
                ],
                "redirect_url": kwargs["request_url"],
            }

        html_form: List[str] = [
            "<form action='' method='POST' role='form' enctype='multipart/form-data'>",
            f"    {tags_form.hidden_tag()}",
        ]

        for i, tag_form in enumerate(tags_form.tags.default):
            html_form.append("    <div class='row mb-3'>")
            if i > 0:
                html_form.append("        <hr class='horizontal dark' />")
            tag_form.tag_name.render_kw, tag_form.tagscript.render_kw = {
                "class": "form-control form-control-default",
            }, {
                "class": "form-control form-control-default",
            }
            html_form.extend(
                [
                    f"        {tag_form.hidden_tag()}",
                    "        <div class='col-md-5'>",
                    "            <div class='form-group'>",
                    f"                {tag_form.tag_name(placeholder='Name')}",
                    "            </div>",
                    "        </div>",
                    "        <div class='col-md-7'>",
                    "            <div class='form-group'>",
                    f"                {tag_form.tagscript(rows=4, disable_toolbar=True, placeholder='Script')}",
                    "            </div>",
                    "        </div>",
                    "        <div class='col-md-12 d-flex justify-content-end align-items-center'>",
                    "            <a href='javascript:void(0);' onclick='this.parentElement.parentNode.remove();' class='text-danger mr-3'><i class='fa fa-minus-circle'></i> Delete Tag</a>",
                    "        </div>",
                    "    </div>",
                ]
            )
        tags_form.submit.render_kw = {
            "class": "btn mb-0 bg-gradient-success btn-md w-100 my-4 mb-2"
        }
        html_form.extend(
            [
                "    <a href='javascript:void(0);' onclick='createTag(this);' class='text-success mr-3'><i class='fa fa-plus-circle'></i> Create Tag</a>"
                "    <div class='text-center'>"
                f"        {tags_form.submit()}",
                "    </div>",
                "</form>",
            ]
        )
        tags_form_str: Markup = Markup("\n".join(html_form))

        return {
            "status": 0,
            "web_content": {
                "source": WEB_CONTENT,
                "tags_form": tags_form_str,
                "tags_form_length": len(tags_form.tags.default),
            },
        }

    @dashboard_page(
        name=None,
        description="Manage Global Tags.",
        is_owner=True,
        methods=("GET", "POST"),
    )
    async def dashboard_global_page(self, user: discord.User, **kwargs: Any) -> Dict[str, Any]:
        if user.id not in self.bot.owner_ids:
            return {
                "status": 1,
            }
        return await self.get_dashboard_page(user=user, guild=None, **kwargs)

    @dashboard_page(
        name="guild",
        description="Manage Guild Tags.",
        methods=("GET", "POST"),
    )
    async def dashboard_guild_page(
        self, user: discord.User, guild: discord.Guild, **kwargs: Any
    ) -> Dict[str, Any]:
        member: Optional[discord.Member] = guild.get_member(user.id)
        if user.id not in self.bot.owner_ids and (
            member is None
            or not (await self.bot.is_mod(member) or member.guild_permissions.manage_guild)
        ):
            return {
                "status": 1,
            }
        return await self.get_dashboard_page(user=user, guild=guild, **kwargs)
