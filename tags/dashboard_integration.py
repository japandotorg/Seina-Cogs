from redbot.core import commands
from redbot.core.bot import Red
import discord
import typing

import datetime

from .converters import TagConverter
from .errors import TagFeedbackError
from .objects import Tag

def dashboard_page(*args, **kwargs):
    def decorator(func: typing.Callable):
        func.__dashboard_decorator_params__ = (args, kwargs)
        return func

    return decorator


class DashboardIntegration:
    bot: Red

    @commands.Cog.listener()
    async def on_dashboard_cog_add(self, dashboard_cog: commands.Cog) -> None:
        dashboard_cog.rpc.third_parties_handler.add_third_party(self)


    async def get_dashboard_page(self, user: discord.User, guild: typing.Optional[discord.Guild], **kwargs) -> typing.Dict[str, typing.Any]:
        import wtforms
        from markupsafe import Markup
        class MarkdownTextAreaField(wtforms.TextAreaField):
            def __call__(
                self,
                disable_toolbar: bool = False,
                **kwargs,
            ) -> Markup:
                if "class" not in kwargs:
                    kwargs["class"] = "markdown-text-area-field"
                else:
                    kwargs["class"] += " markdown-text-area-field"
                if disable_toolbar:
                    kwargs["class"] += " markdown-text-area-field-toolbar-disabled"
                return super().__call__(**kwargs)
        class TagForm(kwargs["Form"]):
            tag_name: wtforms.StringField = wtforms.StringField("Name", validators=[wtforms.validators.InputRequired(), wtforms.validators.Regexp(r"^[^\s]+$"), wtforms.validators.Length(max=300)])
            tagscript: MarkdownTextAreaField = MarkdownTextAreaField("Script", validators=[wtforms.validators.InputRequired(), wtforms.validators.Length(max=1700), kwargs["DpyObjectConverter"](TagConverter)])
        class TagsForm(kwargs["Form"]):
            def __init__(self, tags: typing.Dict[str, str]) -> None:
                super().__init__(prefix="tags_form_")
                for name, tagscript in tags.items():
                    self.tags.append_entry({"tag_name": name, "tagscript": tagscript})
                self.tags.default = [entry for entry in self.tags.entries if entry.csrf_token.data is None]
                self.tags.entries = [entry for entry in self.tags.entries if entry.csrf_token.data is not None]
            tags: wtforms.FieldList = wtforms.FieldList(wtforms.FormField(TagForm))
            submit: wtforms.SubmitField = wtforms.SubmitField("Save Modifications")

        if guild is not None:
            existing_tags = self.guild_tag_cache[guild.id].copy()
        else:
            existing_tags = self.global_tag_cache.copy()
        tags_form: TagsForm = TagsForm({tag.name: tag.tagscript for tag in sorted(existing_tags.values(), key=lambda tag: tag.name)})
        if tags_form.validate_on_submit() and await tags_form.validate_dpy_converters():
            tags = {tag.tag_name.data: tag.tagscript.data for tag in tags_form.tags}
            for tag_name, tagscript in tags.items():
                if tag_name not in existing_tags:
                    __import__
                    try:
                        self.validate_tag_count(guild)
                    except TagFeedbackError as e:
                        return {"status": 1, "notifications": [{"message": str(e), "category": "warning"}]}
                    tag = Tag(
                        self,
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
                "notifications": [{"message": "Successfully saved the modifications.", "category": "success"}],
                "redirect_url": kwargs["request_url"],
            }

        html_form = [
            '<form action="" method="POST" role="form" enctype="multipart/form-data">',
            f"    {tags_form.hidden_tag()}",
        ]
        for i, tag_form in enumerate(tags_form.tags.default):
            html_form.append('    <div class="row mb-3">')
            if i > 0:
                html_form.append('        <hr class="horizontal dark" />')
            tag_form.tag_name.render_kw, tag_form.tagscript.render_kw = {"class": "form-control form-control-default"}, {"class": "form-control form-control-default"}
            html_form.extend(
                [
                    f"        {tag_form.hidden_tag()}",
                    '        <div class="col-md-5">',
                    '            <div class="form-group">',
                    f"                {tag_form.tag_name(placeholder='Name')}",
                    "            </div>",
                    "        </div>",
                    '        <div class="col-md-7">',
                    '            <div class="form-group">',
                    f"                {tag_form.tagscript(rows=4, disable_toolbar=True, placeholder='Script')}",
                    "            </div>",
                    "        </div>",
                    '        <div class="col-md-12 d-flex justify-content-end align-items-center">',
                    '            <a href="javascript:void(0);" onclick="this.parentElement.parentNode.remove();" class="text-danger mr-3"><i class="fa fa-minus-circle"></i> Delete Tag</a>',
                    "        </div>",
                    "    </div>",
                ]
            )
        tags_form.submit.render_kw = {"class": "btn mb-0 bg-gradient-success btn-md w-100 my-4 mb-2"}
        html_form.extend(
            [
                '    <a href="javascript:void(0);" onclick="createTag(this);" class="text-success mr-3"><i class="fa fa-plus-circle"></i> Create Tag</a>'
                '    <div class="text-center">'
                f"        {tags_form.submit()}",
                "    </div>",
                "</form>",
            ]
        )
        tags_form_str = Markup("\n".join(html_form))

        return {
            "status": 0,
            "web_content": {
                "source": WEB_CONTENT,
                "tags_form": tags_form_str,
                "tags_form_length": len(tags_form.tags.default),
            },
        }

    @dashboard_page(name=None, description="Manage global Tags.", is_owner=True, methods=("GET", "POST"))
    async def dashboard_global_page(self, user: discord.User, **kwargs) -> typing.Dict[str, typing.Any]:
        if user.id not in self.bot.owner_ids:
            return {"status": 1}
        return await self.get_dashboard_page(user=user, guild=None, **kwargs)

    @dashboard_page(name="guild", description="Manage guild Tags.", methods=("GET", "POST"))
    async def dashboard_guild_page(
        self, user: discord.User, guild: discord.Guild, **kwargs
    ) -> typing.Dict[str, typing.Any]:
            member = guild.get_member(user.id)
            if (
                user.id not in self.bot.owner_ids
                and (
                    member is None
                    or not (await self.bot.is_mod(member) or member.guild_permissions.manage_guild)
                )
            ):
                return {"status": 1}
            return await self.get_dashboard_page(user=user, guild=guild, **kwargs)

WEB_CONTENT = """
    {{ tags_form|safe }}

    <script>
        var tag_index = {{ tags_form_length }} - 1;
        function createTag(element) {
            var newRow = document.createElement("div");
            newRow.classList.add("row", "mb-3");
            tag_index += 1;
            if (document.querySelectorAll("#third-party-content .row").length != 0) {
                var horizontal = '<hr class="horizontal dark" />\\n';
            } else {
                var horizontal = "";
            }
            newRow.innerHTML = horizontal + `
                <input id="tags_form_tags-${tag_index}-csrf_token" name="tags_form_tags-${tag_index}-csrf_token" type="hidden" value="{{ csrf_token() }}">
                <div class="col-md-5">
                    <div class="form-group">
                        <input class="form-control form-control-default" id="tags_form_tags-${tag_index}-tag_name" maxlength="300" name="tags_form_tags-${tag_index}-tag_name" required type="text" value="" placeholder="Name">
                    </div>
                </div>
                <div class="col-md-7">
                    <div class="form-group">
                        <textarea class="form-control form-control-default markdown-text-area-field markdown-text-area-field-toolbar-disabled" id="tags_form_tags-${tag_index}-tagscript" maxlength="1700" name="tags_form_tags-${tag_index}-tagscript" required rows="4" placeholder="Command"></textarea>
                    </div>
                </div>
                <div class="col-md-12 d-flex justify-content-end align-items-center">
                    <a href="javascript:void(0);" onclick="this.parentElement.parentNode.remove();" class="text-danger mr-3"><i class="fa fa-minus-circle"></i> Delete Tag</a>
                </div>
            `
            element.parentNode.insertBefore(newRow, element);
            MarkdownField(document.getElementById(`tags_form_tags-${tag_index}-tagscript`));
            document.getElementById(`tags_form_tags-${tag_index}-tag_name`).focus();
        }
    </script>
"""
