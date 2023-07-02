from typing import TYPE_CHECKING, Optional

from emoji import EMOJI_DATA
from redbot.core import commands

from .utils import Emoji


if TYPE_CHECKING:
    EmojiConverter = Optional[Emoji]
else:

    class EmojiConverter(commands.PartialEmojiConverter):
        async def convert(self, ctx: commands.Context, arg: str) -> Optional[Emoji]:
            if arg.lower() == "none":
                return None
            arg = arg.strip()
            data = arg if arg in EMOJI_DATA.keys() else await super().convert(ctx, arg)
            data = getattr(data, "to_dict", lambda: data)()
            return Emoji.from_data(data)
