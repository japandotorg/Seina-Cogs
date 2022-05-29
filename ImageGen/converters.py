"""
MIT License

Copyright (c) 2022-present japandotorg

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

from typing import Union, Optional

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

    async def converted_to_buffer(self, source: discord.Member | discord.User | discord.PartialEmoji) -> bytes:
        if isinstance(source, (discord.Member, discord.User)):
            source = await source.display_avatar.read()

        elif isinstance(source, discord.PartialEmoji):
            source = await source.read()

        return source

    async def convert(
        self, ctx: commands.Context, argument: str, *, raise_on_failure: bool = True
    ) -> Optional[bytes]:
        for converter in self._converters:
            try:
                source = await converter().convert(ctx, argument)
            except commands.BadArgument:
                continue
            else:
                break
        else:
            if raise_on_failure:
                raise commands.BadArgument("Failed to fetch an image frrom argument")
            else:
                return None

        return await self.converted_to_buffer(source)
