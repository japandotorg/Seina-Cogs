from typing import Dict, Final, List, Union

from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from ._tagscript import TAGSCRIPT_LIMIT, TagCharacterLimitReached, boosted, unboosted
from .abc import CompositeMetaClass
from .commands.message import MessageCommands
from .events import EventMixin


class BoostUtils(
    commands.Cog,
    EventMixin,
    MessageCommands,
    metaclass=CompositeMetaClass,
):
    """Nitro Boost Utilities."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        default_guild: Dict[str, Dict[str, Union[bool, List[int], str]]] = {
            "boost_message": {
                "toggle": False,
                "channels": [],
                "boosted": boosted,
                "unboosted": unboosted,
            }
        }
        self.config.register_guild(**default_guild)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed: str = super().format_help_for_context(ctx)
        n: str = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"**Author:** {humanize_list(self.__author__)}",
            f"**Version:** {str(self.__version__)}",
        ]
        return "\n".join(text)

    @staticmethod
    async def validate_tagscript(tagscript: str) -> bool:
        length = len(tagscript)
        if length > TAGSCRIPT_LIMIT:
            raise TagCharacterLimitReached(TAGSCRIPT_LIMIT, length)
        return True
