from typing import Any, Dict, List, Union

import discord


@staticmethod
async def group_embeds_by_fields(
    *fields: Dict[str, Union[str, bool]],
    per_embed: int = 3,
    page_in_footer: Union[str, bool] = True,
    **kwargs: Any,
) -> List[discord.Embed]:
    fix_kwargs = lambda kwargs: {  # noqa: E731
        next(x): (fix_kwargs({next(x): v}) if "__" in k else v)
        for k, v in kwargs.copy().items()
        if (x := iter(k.split("__", 1)))
    }
    kwargs = fix_kwargs(kwargs)
    groups: List[discord.Embed] = []
    page_format = ""
    if page_in_footer:
        kwargs.get("footer", {}).pop("text", None)
        page_format = (
            page_in_footer if isinstance(page_in_footer, str) else "Page {page}/{total_pages}"
        )
    ran = list(range(0, len(fields), per_embed))
    for ind, i in enumerate(ran):
        groups.append(discord.Embed.from_dict(kwargs))
        fields_to_add = fields[i : i + per_embed]
        for field in fields_to_add:
            groups[ind].add_field(**field)  # type: ignore
        if page_format:
            groups[ind].set_footer(text=page_format.format(page=ind + 1, total_pages=len(ran)))
    return groups
