from typing import Optional

from TagScriptEngine import Block, Context


class CommentBlock(Block):
    """
    The comment block is just for comments, it will not be parsed,
    however it will be removed from your tag's output.

    **Usage:** ``{comment([other]):[text]}``

    **Aliases:** /, Comment, comment, //, #

    **Payload:** ``text``

    **Parameter:** ``other``

    .. tagscript::

        {#:Comment!}

        {Comment(Something):Comment!}
    """

    ACCEPTED_NAMES = ("/", "Comment", "comment", "//", "#")

    def process(self, ctx: Context) -> Optional[str]:
        return ""
