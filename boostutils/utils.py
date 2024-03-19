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
