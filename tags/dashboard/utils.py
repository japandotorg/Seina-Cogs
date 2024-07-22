import datetime
from typing import Any, Callable, Final, Optional

from redbot.core import commands
from redbot.core.bot import Red

from ..objects import Tag


def dashboard_page(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:
    def decorator(func: Callable) -> Callable[[Any], Any]:
        func.__dashboard_decorator_params__ = (args, kwargs)
        return func

    return decorator


def get_tags_cog(
    bot: Red,
    name: str,
    tagscript: str,
    *,
    guild_id: Optional[int],
    author_id: int,
    created_at: datetime.datetime,
) -> Tag:
    cog: Optional[commands.Cog] = bot.get_cog("Tags")
    return Tag(
        cog,
        name,
        tagscript,
        guild_id=guild_id,
        author_id=author_id,
        created_at=created_at,
    )


WEB_CONTENT: Final[
    str
] = """
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
