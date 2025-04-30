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

import collections
from typing import DefaultDict, Dict, Final, List

from redbot.core import Config, commands
from redbot.core.bot import Red

from .abc import CompositeMetaClass
from .common import manager, models, utils, views
from .pipes import Commands, Listeners


class Applications(
    Commands,
    Listeners,
    commands.Cog,
    metaclass=CompositeMetaClass,
):
    """Create custom applications."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.0.1b"

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        self.config: Config = Config.get_conf(
            self,
            identifier=69_666_420,
            force_registration=True,
        )
        __default: Dict[str, Dict[str, utils.TypedConfig]] = {"apps": {}}
        self.config.register_guild(**__default)

        self.cache: DefaultDict[int, Dict[str, models.Application]] = collections.defaultdict(dict)
        self.manager: manager.ApplicationManager = manager.ApplicationManager(self)

    async def cog_load(self) -> None:
        self.manager.initialize()
        self.bot.add_dynamic_items(views.DynamicApplyButton)
        # self.bot.add_dynamic_items(views.VotersButton)

    async def cog_unload(self) -> None:
        self.manager.close()
        self.bot.remove_dynamic_items(views.DynamicApplyButton)
        # self.bot.remove_dynamic_items(views.VotersButton)
