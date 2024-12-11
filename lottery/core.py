from typing import Dict, Final, List, Union

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils.chat_formatting import humanize_list

from .abc import CompositeMetaClass
from .apps import LotteryGroup
from .commands import Commands
from .models import LotteryManager


class Lottery(commands.Cog, Commands, metaclass=CompositeMetaClass):
    """Make and host lotteries in your server."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.config: Config = Config.get_conf(self, identifier=69_666_420, force_registration=True)
        __default: Dict[str, Dict[str, Dict[str, Union[int, Dict[str, int], List[int]]]]] = {
            "lotteries": {}
        }
        self.config.register_guild(**__default)
        self.config.register_global(**{"updated": False})

        self.manager: LotteryManager = LotteryManager(self)
        self.apps: LotteryGroup = LotteryGroup(self.manager)

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed: str = super().format_help_for_context(ctx)
        n: str = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"**Author:** {humanize_list(self.__author__)}",
            f"**Version:** {str(self.__version__)}",
        ]
        return "\n".join(text)

    async def cog_load(self) -> None:
        self.bot.tree.add_command(self.apps)
