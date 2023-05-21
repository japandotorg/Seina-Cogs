import discord


class URLView(discord.ui.View):
    def __init__(self, label: str, jump_url: str) -> None:
        super().__init__(timeout=None)
        self.label: str = label
        self.jump: str = jump_url

        button: discord.ui.Button = discord.ui.Button(
            label=str(self.label), style=discord.ButtonStyle.url, url=str(self.jump)
        )
        self.add_item(button)

    async def on_timeout(self) -> None:
        pass
