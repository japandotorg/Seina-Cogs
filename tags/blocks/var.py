from typing import Optional

from TagScriptEngine import StringAdapter, Block, Context


class VarBlock(Block):
    """
    Variables can be referenced using this block.
    **Note:**
    - If a variable's name is being "used" by any other block the
    variable will be ignored

    **Usage:** ``{let(<name>):<value>}``

    **ALiases:** ``let, var``

    **Payload:** ``value``

    **Parameter:** ``name``

    **Examples:**

    .. tagscript::

        {let(day):Monday}
        {if({day}==Wednesday):It's Wednesday my dudes!|The day is {day}.}
        The day is Monday.
    """

    ACCEPTED_NAMES = ("let", "var")

    def process(self, ctx: Context) -> Optional[str]:
        if ctx.verb.parameter in ctx.interpreter._blocknames:  # pylint: disable=protected-access
            return None
        ctx.response.variables[ctx.verb.parameter] = StringAdapter(str(ctx.verb.payload))
        return ""
