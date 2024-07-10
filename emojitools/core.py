"""
MIT License

Copyright (c) 2021-2024 Obi-Wan3
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

import asyncio
import contextlib
import os
import shutil
from io import BytesIO
from typing import Any, AsyncGenerator, Dict, Final, List, Literal, Optional, Union, cast
from zipfile import ZipFile

import discord
from PIL import Image
from redbot.core import commands, data_manager
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list
from redbot.core.utils.mod import get_audit_reason
from redbot.core.utils.views import ConfirmView
from zipstream.aiozipstream import AioZipStream


class EmojiTools(commands.Cog):
    """Tools for Managing Custom Emojis"""

    __author__: Final[List[str]] = ["inthedark.org", "Obi-Wan3"]
    __version__: Final[str] = "2.0.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

    @staticmethod
    def _ext(e: Union[discord.Emoji, discord.PartialEmoji]) -> Literal[".gif", ".png"]:
        return ".gif" if e.animated else ".png"

    @staticmethod
    async def _convert_emoji(
        ctx: commands.Context, emoji: str, partial: bool = True
    ) -> Union[discord.Emoji, discord.PartialEmoji]:
        try:
            if partial:
                return await commands.PartialEmojiConverter().convert(ctx, emoji)
            return await commands.EmojiConverter().convert(ctx, emoji)
        except commands.BadArgument:
            raise commands.UserFeedbackCheckFailure("Invalid emoji: {}".format(emoji))

    @staticmethod
    async def _generate_emoji(
        e: Union[discord.Emoji, discord.PartialEmoji]
    ) -> AsyncGenerator[bytes, Any]:
        yield await e.read()

    @staticmethod
    async def _edit_guild_emoji(ctx: commands.GuildContext, emoji: discord.Emoji, **kwargs: Any):
        if emoji.guild_id != ctx.guild.id:
            raise commands.BadArgument("You can only edit emojis from the current server!")
        if roles := kwargs["roles"]:
            for role in roles:
                if (
                    role >= ctx.author.top_role and ctx.author != ctx.guild.owner
                ) or role >= ctx.guild.me.top_role:
                    raise commands.BadArgument(
                        "I cannot perform this action due to the Discord role hierarchy!"
                    )
        kwargs["reason"] = get_audit_reason(ctx.author, reason="[EmojITools] edited an emoji.")
        try:
            await emoji.edit(**kwargs)
        except (discord.Forbidden, discord.HTTPException):
            raise commands.UserFeedbackCheckFailure(
                "Something went wrong when editing the emoji: {}.".format(emoji)
            )

    async def _create_emoji_from_string(
        self,
        ctx: commands.GuildContext,
        emoji: str,
        *,
        name: Optional[str] = None,  # type: ignore
        guild: Optional[discord.Guild] = None,  # type: ignore
        timeout: float = 10.0,
    ) -> discord.Emoji:
        e: discord.PartialEmoji = cast(discord.PartialEmoji, await self._convert_emoji(ctx, emoji))
        guild: discord.Guild = guild or ctx.guild
        name: str = name or e.name
        try:
            to_be_created: discord.Emoji = await asyncio.wait_for(
                guild.create_custom_emoji(
                    name=name,
                    image=await e.read(),
                    reason=get_audit_reason(ctx.author, "[EmojiTools] custom emoji created."),
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise commands.BadArgument(
                "The request timed out or we are being ratelimited, "
                "please try again after a few minutes."
            )
        except commands.CommandInvokeError:
            raise commands.BadArgument(
                "Something went wrong while adding the emoji. Has the limit been reached?"
            )
        except discord.HTTPException:
            raise commands.BadArgument(
                "Something went wrong while adding the emoji(s): the source file may "
                "be too big or the limit may have been reached."
            )
        return to_be_created

    async def _create_emoji_from_image(
        self,
        ctx: commands.GuildContext,
        image: bytes,
        name: str,
        *,
        guild: Optional[discord.Guild] = None,  # type: ignore
        timeout: float = 10.0,
    ):
        guild: discord.Guild = guild or ctx.guild
        try:
            emoji: discord.Emoji = await asyncio.wait_for(
                guild.create_custom_emoji(
                    name=name,
                    image=image,
                    reason=get_audit_reason(ctx.author, "[EmojiTools] added a custom emoji."),
                ),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise commands.BadArgument(
                "The request timed out or we are being ratelimited, "
                "please try again after a few minutes."
            )
        except commands.CommandInvokeError:
            raise commands.BadArgument(
                "Something went wrong while adding the emoji. Has the limit been reached?"
            )
        except discord.HTTPException:
            raise commands.BadArgument(
                "Something went wrong while adding the emoji(s): the source file may "
                "be too big or the limit may have been reached."
            )
        return emoji

    async def _maybe_create_folder(self, name: str) -> str:
        path: str = os.path.join("{}".format(data_manager.cog_data_path(self)), "{}".format(name))
        try:
            os.mkdir(path)
        except OSError:
            raise commands.UserFeedbackCheckFailure(
                "The emojis will be added to the existing folder with this name."
            )
        return path

    async def _zip_emojis(
        self, emojis: List[Union[discord.Emoji, discord.PartialEmoji]], name: str
    ) -> discord.File:
        emos: List[Dict[str, Union[AsyncGenerator[bytes, Any], str]]] = []
        for emoji in emojis:
            emos.append(
                {
                    "stream": self._generate_emoji(emoji),
                    "name": "{}{}".format(emoji.name, self._ext(emoji)),
                }
            )
        stream: AioZipStream = AioZipStream(emos, chunksize=32768)
        with BytesIO() as b:
            async for chunk in stream.stream():
                b.write(chunk)
            b.seek(0)
            file: discord.File = discord.File(b, filename=name)
        return file

    @commands.guild_only()
    @commands.admin_or_permissions(manage_emojis=True)
    @commands.group(name="emojitools")
    async def _emoji_tools(self, _: commands.GuildContext):
        """
        Various tools for managing custom emojis in servers.

        `[p]emojitools add` has various tools to add emojis to the current server.
        `[p]emojitools delete` lets you remove emojis from the server.
        `[p]emojitools tozip` returns an instant `.zip` archive of emojis (w/o saving a folder permanently).
        `[p]emojitools save` allows you to save emojis to folders **in the cog data path**: this requires storage!
        """

    @commands.bot_has_permissions(attach_files=True)
    @_emoji_tools.command(name="enlarge")  # type: ignore
    async def _emoji_tools_enlarge(self, ctx: commands.GuildContext, emoji: str):
        """Enlarge a custom emoji."""
        emo: discord.PartialEmoji = cast(
            discord.PartialEmoji, await self._convert_emoji(ctx, emoji)
        )
        with BytesIO() as b:
            await emo.save(b)
            image: Image.Image = Image.open(b)
            width, height = image.size
            image: Image.Image = image.resize(*(width * 5, height * 5), Image.Resampling.LANCZOS)
            byte: BytesIO = BytesIO()
            image.save(byte, "PNG", optimize=True)
            byte.seek(0)
            file: discord.File = discord.File(byte, "{}.png".format(emo.name))
        await ctx.send(file=file)

    @commands.bot_has_permissions(embed_links=True)
    @_emoji_tools.command(name="info")  # type: ignore
    async def _emoji_tools_info(self, ctx: commands.GuildContext, emoji: discord.Emoji):
        """Get info about a custom emoji [botname] has access to."""
        description: str = (
            "ID            : {}\n"
            "Name          : {}\n"
            "Animated      : {}\n"
            "Creation (UTC): {}\n"
        ).format(
            emoji.id,
            emoji.name,
            emoji.animated,
            emoji.created_at.strftime("%B %d, %Y (%I:%M:%S %p)"),
        )
        embed: discord.Embed = discord.Embed(
            description="Emoji Information for {}!\n\n".format(emoji)
            + box(description, lang="prolog"),
            color=await ctx.embed_color(),
        )
        embed.set_thumbnail(url=emoji.url)
        if guild := emoji.guild:
            embed.add_field(
                name="Roles Allowed:",
                value="{}".format(humanize_list([r.mention for r in emoji.roles]) or "Everyone."),
            )
            if guild.me.guild_permissions.manage_emojis:
                with contextlib.suppress(discord.HTTPException):
                    embed.add_field(
                        name="Author:",
                        value="{}".format(emoji.user.mention if emoji.user else "Unknown"),
                    )
                    embed.add_field(
                        name="Guild:",
                        value="{} (`{}`)".format(guild.name, guild.shard_id),
                        inline=False,
                    )
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @commands.admin_or_permissions(administrator=True)
    @_emoji_tools.group(name="save")  # type: ignore
    async def _emoji_tools_save(self, _: commands.GuildContext):
        """
        Save Custom Emojis to Folders

        **IMPORTANT**: this **will** save folders to the cog data path, requiring storage in the machine the bot is hosted on.
        The folders will be accessible to admin across all servers with access to this cog.
        The other `EmojiTools` features that do **NOT** require storage, so disable this command group if you wish.
        For large public bots, it is highly recommended to restrict usage of or disable this command group.
        """

    @commands.cooldown(1, 15, commands.BucketType.user)
    @_emoji_tools_save.command(name="emojis", require_var_positional=True)  # type: ignore
    async def _emoji_tools_save_emojis(self, ctx: commands.GuildContext, name: str, *emojis: str):
        """Save to a folder the specified custom emojis (can be from any server)."""
        async with ctx.typing():
            path: str = await self._maybe_create_folder(name)
            for e in emojis:
                emoji: Union[discord.Emoji, discord.PartialEmoji] = await self._convert_emoji(
                    ctx, e
                )
                await emoji.save(os.path.join(path, "{}{}".format(emoji.name, self._ext(emoji))))
        await ctx.send("{} emojis were saved to `{}`.".format(len(emojis), name))

    @commands.cooldown(1, 60, commands.BucketType.guild)
    @_emoji_tools_save.command(name="server", aliases=["guild"])  # type: ignore
    async def _emoji_tools_save_server(
        self, ctx: commands.GuildContext, name: Optional[str] = None
    ):
        """Save to a folder all custom emojis from this server (folder name defaults to server name)."""
        async with ctx.typing():
            path = await self._maybe_create_folder(name or str(ctx.guild.id))
            for emoji in ctx.guild.emojis:
                await emoji.save(os.path.join(path, "{}{}".format(emoji.name, self._ext(emoji))))
        await ctx.send(
            "{} emojis were saved to `{}`.".format(len(ctx.guild.emojis), name or ctx.guild.id)
        )

    @_emoji_tools_save.command(name="folders")  # type: ignore
    async def _emoji_tools_save_folders(self, ctx: commands.GuildContext):
        """List all your saved EmojiTools folders."""
        string: str = ""
        for index, dir in enumerate(
            sorted(os.listdir("{}".format(data_manager.cog_data_path(self))))
        ):
            if os.path.isdir(os.path.join("{}".format(data_manager.cog_data_path(self)), dir)):
                string += "{}. {}".format(index, dir)
        await ctx.maybe_send_embed(
            string
            or "You have no EmojiTools folders yet. Save emojis with `{}emojitools save`!".format(
                ctx.clean_prefix
            )
        )

    @commands.cooldown(1, 60, commands.BucketType.user)
    @_emoji_tools_save.command(name="remove", aliases=["delete"])  # type: ignore
    async def _emoji_tools_save_remove(self, ctx: commands.GuildContext, number: int):
        """Remove an EmojiTools folder."""
        dirs: List[str] = sorted(os.listdir("{}".format(data_manager.cog_data_path(self))))
        try:
            to_remove: str = dirs[number]
        except IndexError:
            raise commands.BadArgument("Invalid folder number.")
        await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: shutil.rmtree(
                (
                    os.path.join(
                        "{}".format(data_manager.cog_data_path(self)), "{}".format(to_remove)
                    )
                )
            ),
        )
        await ctx.send("`{}` has been removed.".format(to_remove))

    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @_emoji_tools_save.command(name="getzip", aliases=["gz"])  # type: ignore
    async def _emoji_tools_save_get_zip(self, ctx: commands.GuildContext, number: int):
        """Zip and upload an EmojiTools folder."""
        async with ctx.typing():
            items: List[str] = sorted(os.listdir("{}".format(data_manager.cog_data_path(self))))
            for item in items:
                if item.endswith(".zip"):
                    await asyncio.get_running_loop().run_in_executor(
                        None,
                        lambda: os.remove(
                            os.path.join("{}".format(data_manager.cog_data_path(self)), item)
                        ),
                    )
            try:
                folder: str = items[number]
            except IndexError:
                raise commands.BadArgument("Invalid folder number.")
            path: str = os.path.join("{}".format(data_manager.cog_data_path(self)), folder)
            files = []
            for root, _, _files in os.walk(path):
                for file in _files:
                    files.append({"file": os.path.join(root, file)})
            stream: AioZipStream = AioZipStream(files, chunksize=32768)
            with BytesIO() as b:
                async for chunk in stream.stream():
                    b.write(chunk)
                b.seek(0)
                zip: discord.File = discord.File(b, filename="{}.zip".format(folder))
        try:
            await ctx.send(file=zip)
        except discord.HTTPException:
            raise commands.BadArgument(
                "Unfortunately, it seems the attachment was too large to be sent."
            )

    @commands.bot_has_permissions(manage_emojis=True)
    @_emoji_tools.group(name="delete", aliases=["remove"])  # type: ignore
    async def _emoji_tools_delete(self, _: commands.GuildContext):
        """Delete Server Custom Emojis."""

    @commands.cooldown(1, 15, commands.BucketType.guild)
    @_emoji_tools_delete.command(name="emojis", aliases=["emoji"], require_var_positional=True)  # type: ignore
    async def _emoji_tools_delete_emojis(
        self, ctx: commands.GuildContext, *emojis: Union[str, discord.Emoji]
    ):
        """Delete custom emojis from the server."""
        async with ctx.typing():
            for emoji in emojis:  # type: ignore
                if isinstance(emoji, str):
                    emoji: discord.Emoji = cast(
                        discord.Emoji, await self._convert_emoji(ctx, emoji, partial=False)
                    )
                elif emoji.guild_id != ctx.guild.id:
                    raise commands.BadArgument(
                        "The following emoji is not in this server: {}.".format(emoji)
                    )
                await emoji.delete(
                    reason=get_audit_reason(
                        ctx.author,
                        "[EmojiTools] Deleted the {0.name} (`{0.id}`) emoji.".format(emoji),
                    )
                )
        await ctx.send(
            "The following emojis have been removed from this server: `{}`.".format(
                "`, `".join([str(e) for e in emojis])
            )
        )

    @commands.cooldown(1, 60, commands.BucketType.guild)
    @_emoji_tools_delete.command(name="all")  # type: ignore
    async def _emoji_tools_delete_all(self, ctx: commands.GuildContext, force: bool = False):
        """Delete all custom emojis from the server."""
        if not force:
            message: str = (
                "Using this command will delete all the emojis in this server. Do you wish to continue?"
            )
            view: ConfirmView = ConfirmView(ctx.author, disable_buttons=True)
            view.confirm_button.emoji = "\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16}"
            view.confirm_button.style = discord.ButtonStyle.green
            view.confirm_button.label = None
            view.dismiss_button.emoji = "\N{HEAVY MULTIPLICATION X}\N{VARIATION SELECTOR-16}"
            view.dismiss_button.style = discord.ButtonStyle.red
            view.dismiss_button.label = None
            view.message = await ctx.send(message, view=view)
            await view.wait()
            if not view.result:
                raise commands.UserFeedbackCheckFailure("Operation aborted.")
        async with ctx.typing():
            counter: int = 0
            for emoji in ctx.guild.emojis:
                with contextlib.suppress(discord.HTTPException):
                    await emoji.delete(
                        reason=get_audit_reason(
                            ctx.author,
                            "[EmojiTools] Deleted the {0.name} (`{0.id}`) emoji.".format(emoji),
                        )
                    )
                    counter += 1
        await ctx.send("All {} custom emojis have been removed from this server.".format(counter))

    @commands.bot_has_permissions(manage_emojis=True)
    @_emoji_tools.group(name="add", aliases=["+"])  # type: ignore
    async def _emoji_tools_add(self, _: commands.GuildContext):
        """Add Custom Emojis to Server"""

    @commands.cooldown(1, 15, commands.BucketType.guild)
    @_emoji_tools_add.command(name="emoji")  # type: ignore
    async def _emoji_tools_add_emoji(
        self, ctx: commands.GuildContext, emoji: discord.PartialEmoji, name: Optional[str] = None
    ):
        """Add an emoji to this server (leave `name` blank to use the emoji's original name)."""
        async with ctx.typing():
            final: discord.Emoji = await self._create_emoji_from_string(
                ctx, str(emoji), name=name or emoji.name
            )
        await ctx.send("{} has been added to this server!".format(final))

    @commands.cooldown(1, 60, commands.BucketType.guild)
    @_emoji_tools_add.command(name="emojis", require_var_positional=True)  # type: ignore
    async def _emoji_tools_add_emojis(self, ctx: commands.GuildContext, *emojis: str):
        """Add some emojis to this server."""
        async with ctx.typing():
            added: List[discord.Emoji] = []
            for emoji in emojis:
                waited: discord.Emoji = await self._create_emoji_from_string(ctx, emoji)
                added.append(waited)
        await ctx.send(
            "{} emojis were added to this server: {}.".format(
                len(emojis), humanize_list([str(e) for e in added])
            )
        )

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @_emoji_tools_add.command(name="reaction", aliases=["fromreaction"])  # type: ignore
    async def _emoji_tools_add_reaction(
        self,
        ctx: commands.GuildContext,
        option: Literal["specific", "all"] = "specific",
        message: Optional[discord.Message] = None,  # type: ignore
        word: Optional[str] = None,
        name: str = None,
    ):
        """Add emojis to this server from reaction on a message."""
        if not message:
            reference: Optional[discord.MessageReference] = ctx.message.reference
            if not (reference and isinstance(reference.resolved, discord.Message)):
                raise commands.BadArgument("I need a valid message to load reactions from!")
            message: discord.Message = reference.resolved
        async with ctx.typing():
            added: List[discord.Emoji] = []
            for reaction in message.reactions:
                if option.lower() == "specific":
                    if not word:
                        raise commands.BadArgument(
                            "`specific` is a required argument when used with the 'specific' option."
                        )
                    emoji: discord.PartialEmoji = cast(
                        discord.PartialEmoji, await self._convert_emoji(ctx, str(reaction.emoji))
                    )
                    if reaction.is_custom_emoji() and emoji.name == word:
                        created: discord.Emoji = await self._create_emoji_from_string(
                            ctx, str(emoji), name=name or emoji.name
                        )
                        added.append(created)
                    else:
                        raise commands.BadArgument(
                            "No reaction called `{}` was found on that message!".format(word)
                        )
                elif option.lower() == "all":
                    if name:
                        raise commands.BadArgument(
                            "Cannot use the `name` argument with the `all` option."
                        )
                    if not reaction.is_custom_emoji():
                        continue
                    created: discord.Emoji = await self._create_emoji_from_string(
                        ctx, str(reaction.emoji)
                    )
                    added.append(created)
        if not added:
            raise commands.BadArgument("No emojis were added.")
        await ctx.send(
            "{} emoji{} {} added to this server: {}".format(
                len(added),
                "s" if len(added) > 1 else "",
                "were" if len(added) > 1 else "was",
                humanize_list([str(e) for e in added]),
            )
        )

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.admin_or_permissions(manage_emojis=True)
    @_emoji_tools_add.command(name="image", aliases=["fromimage"])  # type: ignore
    async def _emoji_tools_add_image(self, ctx: commands.GuildContext, name: Optional[str] = None):
        """
        Add an emoji to this server from a provided image.

        The attached image should be in one of the following formats: `.png`, `.jpg`, or `.gif`.
        """
        async with ctx.typing():
            if len(ctx.message.attachments) > 1:
                raise commands.BadArgument("Please only attach one file!")
            elif len(ctx.message.attachments) < 1:
                raise commands.BadArgument("Please attach an image!")
            if not ctx.message.attachments[0].filename.endswith((".png", ".jpg", ".gif")):
                raise commands.BadArgument(
                    "Please make sure the uploaded image is a `.png`, `.jpg` or `.gif` file!"
                )
            image: bytes = await ctx.message.attachments[0].read()
            emoji: discord.Emoji = await self._create_emoji_from_image(
                ctx, image, name or ctx.message.attachments[0].filename[:-4]
            )
        await ctx.send("{} has been added to this server!".format(emoji))

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.admin_or_permissions(manage_emojis=True)
    @_emoji_tools_add.command(name="zip", aliases=["fromzip"])  # type: ignore
    async def _emoji_tools_add_zip(self, ctx: commands.GuildContext):
        """
        Add some emojis to this server from a provided .zip archive.

        The `.zip` archive should extract to a folder, which contains files in the formats `.png`, `.jpg`, or `.gif`.
        You can also use the `[p]emojitools tozip` command to get a zip archive, extract it, remove unnecessary emojis, then re-zip and upload.
        """
        async with ctx.typing():
            if len(ctx.message.attachments) > 1:
                raise commands.BadArgument("Please only attach one file!")
            elif len(ctx.message.attachments) < 1:
                raise commands.BadArgument("Please attach a `.zip` file!")
            if not ctx.message.attachments[0].filename.endswith(".zip"):
                raise commands.BadArgument(
                    "Please make sure the uploaded file is a `.zip` archive!"
                )
            added: List[discord.Emoji] = []
            failed: int = 0
            with ZipFile(BytesIO(await ctx.message.attachments[0].read())) as zip:
                for info in zip.infolist():
                    if not info.filename.endswith((".png", ".jpg", ".gif")):
                        failed += 1
                        continue
                    image: bytes = zip.read(info)
                    try:
                        emoji: discord.Emoji = await self._create_emoji_from_image(
                            ctx, image, info.filename[:-4]
                        )
                    except commands.BadArgument:
                        failed += 1
                        continue
                    added.append(emoji)
        content: str = "{} emoji{} {} added to this server: {}.".format(
            len(added),
            "s" if len(added) > 1 else "",
            "were" if len(added) > 1 else "was",
            humanize_list([str(e) for e in added]),
        )
        if failed > 1:
            content += "\nFailed to add {} emoji{}.".format(failed, "s" if len(added) > 1 else "")
        await ctx.send(content)

    @commands.bot_has_permissions(manage_emojis=True)
    @_emoji_tools.command(name="edit")  # type: ignore
    async def _emoji_tools_edit(self, _: commands.Context):
        """Edit Custom Emojis in the Server"""

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @_emoji_tools_edit.command(name="name")  # type: ignore
    async def _emoji_tools_edit_name(
        self, ctx: commands.GuildContext, emoji: discord.Emoji, name: str
    ):
        """Edit the name of a custom emoji from this server."""
        await self._edit_guild_emoji(ctx, emoji, name=name)
        await ctx.tick()

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @_emoji_tools_edit.command(name="roles")  # type: ignore
    async def _emoji_tools_edit_roles(
        self, ctx: commands.GuildContext, emoji: discord.Emoji, *roles: discord.Role
    ):
        """Edit the roles to which the usage of a custom emoji from this server is restricted."""
        await self._edit_guild_emoji(ctx, emoji, roles=roles)
        await ctx.tick()

    @commands.bot_has_permissions(attach_files=True)
    @_emoji_tools.command(name="zip", aliases=["tozip"])  # type: ignore
    async def _emoji_tools_zip(self, _: commands.GuildContext):
        """Get a `.zip` Archive of Emojis"""

    @commands.cooldown(1, 30, commands.BucketType.user)
    @_emoji_tools_zip.command(name="emojis", require_var_positional=True)  # type: ignore
    async def _emoji_tools_zip_emojis(self, ctx: commands.GuildContext, *emojis: str):
        """
        Get a `.zip` archive of the provided emojis.

        The returned `.zip` archive can be used for the `[p]emojitools add fromzip` command.
        """
        async with ctx.typing():
            converted: List[discord.PartialEmoji] = cast(
                List[discord.PartialEmoji],
                [await self._convert_emoji(ctx, emoji) for emoji in emojis],
            )
            file: discord.File = await self._zip_emojis(converted, "emojis.zip")
        try:
            await ctx.send(
                "{} emoji{} {} were saved to this `.zip` archive!".format(
                    len(emojis),
                    "s" if len(emojis) > 1 else "",
                    "were" if len(emojis) > 1 else "was",
                ),
                file=file,
            )
        except discord.HTTPException:
            raise commands.UserFeedbackCheckFailure(
                "Unfortunately, it seems the attachment was too large to be sent."
            )

    @commands.cooldown(1, 60, commands.BucketType.guild)
    @_emoji_tools_zip.command(name="server", aliases=["guild"])  # type: ignore
    async def _emoji_tools_zip_server(self, ctx: commands.GuildContext):
        """
        Get a `.zip` archive of all custom emojis in the server.

        The returned `.zip` archive can be used for the `[p]emojitools add fromzip` command.
        """
        if not (emojis := list(ctx.guild.emojis)):
            raise commands.UserFeedbackCheckFailure("This server has no custom emojis!")
        async with ctx.typing():
            file: discord.File = await self._zip_emojis(emojis, "{}.zip".format(ctx.guild.name))
        try:
            await ctx.send(
                "{} emoji{} {} were saved to this `.zip` archive!".format(
                    len(emojis),
                    "s" if len(emojis) > 1 else "",
                    "were" if len(emojis) > 1 else "was",
                ),
                file=file,
            )
        except discord.HTTPException:
            raise commands.UserFeedbackCheckFailure(
                "Unfortunately, it seems the attachment was too large to be sent."
            )
