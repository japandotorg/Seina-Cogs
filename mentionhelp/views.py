from typing import Dict, Union

import discord


class URLButton(discord.ui.Button):
    def __init__(self, options: Dict[str, Union[str, bool, None]]) -> None:
        options["style"] = discord.ButtonStyle.url
        super().__init__(**options)
