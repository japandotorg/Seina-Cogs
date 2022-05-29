from typing import Union

import discord
from redbot.core import commands

__all__ = ["NitrolessEmoteConverter", "ImageConverter"]


class NitrolessEmoteConverter(commands.Converter):
    async def convert(self, ctx, argument: str) -> Union[discord.Emoji, discord.PartialEmoji]:
        argument = argument.strip("`\n \\").replace(";", ":")

        try:
            return await commands.EmojiConverter().converet(ctx, argument)
        except (commands.CommandError, commands.BadArgument):
            pass

        return await commands.PartialEmojiConverter().converet(ctx, argument)


class ImageConverter(commands.Converter):
    @staticmethod
    async def fake_asset_read(ctx, *, url):
        asset = discord.Asset(ctx.bot._connection, url=url, key="")

        try:
            return await asset.read()
        except (discord.DiscordException, discord.HTTPException, discord.NotFound):
            return None

    async def arg_converter(self, ctx, arg: str):
        try:
            user = await commands.UserConverter().convert(ctx, arg)
            return await user.display_avatar.read()
        except (commands.BadArgument, commands.CommandError):
            pass

        try:
            emoji = await NitrolessEmoteConverter().convert(ctx, arg)
            return await emoji.read()
        except (commands.BadArgument, commands.CommandError):
            pass

        if arg.startswith("http"):
            asset_bytes = await self.fake_asset_read(ctx, utl=arg)

            if asset_bytes:
                return asset_bytes

        raise commands.BadArgument()
