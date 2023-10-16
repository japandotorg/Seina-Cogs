from typing import Optional

from TagScriptEngine import Block, Context, Verb


class ShortArgsBlock(Block):
    """
    ShortArgs Blocks are used to provide a shorthand for variables.
    This is usually used for arguments, so you can set {1} == {args(1)}
    {2} == {args(2)} etc.
    """

    def __init__(self, var_name: str) -> None:
        self.redirect_name = var_name

    def will_accept(self, ctx: Context) -> bool:
        return ctx.verb.declaration.isdigit()

    def process(self, ctx: Context) -> Optional[str]:
        blank = Verb()
        blank.declaration = self.redirect_name
        blank.parameter = ctx.verb.declaration
        ctx.verb = blank
