"""
MIT License

Copyright (c) 2020-2023 PhenoM4n4n
Copyright (c) 2023-present japandotorg

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

from typing import ClassVar, Dict, List, Optional, Tuple, Union

from TagScriptEngine import Block, Context


class AllowedMentionsBlock(Block):
    """
    The "allowed mentions" block attempts to enable mentioning of roles.
    Passing no parameter enables mentioning of all roles within the message
    content. However passing a role name or ID to the block parameter allows
    mentioning of that specific role only. Multiple role name or IDs can be
    included, separated by a comma ",". By default, mentioning is only
    triggered if the execution author has "manage server" permissions. However,
    using the "override" keyword as a payload allows mentioning to be triggered
    by anyone.

    **Usage:** ``{allowedmentions(<role, None>):["override", None]}``

    **Aliases:** ``mentions``

    **Payload:** "override", None

    **Parameter:** role, None

    **Examples:** ::

        {allowedmentions}
        {allowedmentions:override}
        {allowedmentions(@Admin, Moderator):override}
        {allowedmentions(763522431151112265, 812949167190048769)}
        {mentions(763522431151112265, 812949167190048769):override}
    """

    ACCEPTED_NAMES: ClassVar[Tuple[str, ...]] = ("allowedmentions", "mentions")
    PAYLOADS: ClassVar[Tuple[str, ...]] = ("override",)

    @classmethod
    def will_accept(cls, ctx: Context) -> bool:
        if ctx.verb.payload and ctx.verb.payload not in cls.PAYLOADS:
            return False
        return super().will_accept(ctx)

    def process(self, ctx: Context) -> Optional[str]:
        actions: Optional[Dict[str, Union[bool, List[str]]]] = ctx.response.actions.get(
            "allowed_mentions"
        )
        if actions:
            return None
        if not (param := ctx.verb.parameter):
            ctx.response.actions["allowed_mentions"] = {
                "mentions": True,
                "override": True if ctx.verb.payload else False,
            }
            return ""
        ctx.response.actions["allowed_mentions"] = {
            "mentions": [r.strip() for r in param.split(",")],
            "override": True if ctx.verb.payload else False,
        }
        return ""
