"""
MIT License

Copyright (c) 2023-present japandotorg

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
import io
import logging
from typing import Any, Dict, Final, List, Optional, Tuple, Union

import discord
import pydub
import speech_recognition as speech
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box, humanize_list

from .views import JumpToMessageView

MIC_GIF: Final[str] = "https://cdn.discordapp.com/emojis/1164844325973270599.gif"

log: logging.Logger = logging.getLogger("red.seina.voicenotelog")


class VoiceNoteLog(commands.Cog):
    """
    Voice note logging.
    """

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
        default_guild: Dict[str, Union[Optional[int], bool]] = {
            "channel": None,
            "toggle": False,
        }
        default_global: Dict[str, bool] = {
            "notice": False,
        }
        self.config.register_guild(**default_guild)

        self.task: asyncio.Task[Any] = asyncio.create_task(self.initialize())

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    def _has_voice_note(self, message: discord.Message) -> bool:
        if not message.attachments or not message.flags.value >> 13:
            return False
        return True

    async def initialize(self) -> None:
        await self.bot.wait_until_red_ready()
        if not await self.config.notice():
            try:
                await self.bot.send_to_owners(
                    "In order to use the **VoiceNoteLog** cog, you'll have to install ffmpeg in your server.\n"
                    "**Linux:** `sudo apt install ffmpeg -y`\n"
                    "**WIndows:** <https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/>\n"
                )
                await self.config.notice.set(True)
            except (discord.NotFound, discord.HTTPException):
                log.exception("Failed to send the notice message!")

    async def cog_unload(self) -> None:
        self.task.cancel()

    async def _embed(self, text: str, message: discord.Message) -> discord.Embed:
        embed: discord.Embed = discord.Embed(
            description=(
                f"**Channel:** {message.channel.mention}\n"  # type: ignore
                f"**Transcribed Text:** {box(text)}\n"
            ),
            color=await self.bot.get_embed_color(message.channel),  # type: ignore
            timestamp=message.created_at,
        )
        embed.set_thumbnail(url=MIC_GIF)
        embed.set_author(
            name=f"{message.author.display_name} ({message.author.id})",
            icon_url=message.author.display_avatar,
        )
        return embed

    async def _transcribe_message(
        self, message: discord.Message
    ) -> Optional[Union[Any, List, Tuple]]:
        if not self._has_voice_note(message):
            return None

        voice_message_bytes: bytes = await message.attachments[0].read()
        voice_message: io.BytesIO = io.BytesIO(voice_message_bytes)

        audio_segment = pydub.AudioSegment.from_file(voice_message)
        empty_bytes: io.BytesIO = io.BytesIO()
        audio_segment.export(empty_bytes, format="wav")

        recognizer = speech.Recognizer()
        with speech.AudioFile(empty_bytes) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
        except speech.UnknownValueError as error:
            raise error
        except Exception as error:
            raise error

        return text

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return
        if message.is_system():
            return
        if message.author.bot:
            return
        if not isinstance(
            message.channel, (discord.TextChannel, discord.VoiceChannel, discord.Thread)
        ):
            return

        if not (await self.config.guild(message.guild).toggle()):
            return

        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return

        if not self._has_voice_note(message):
            return

        log_channel: Optional[discord.TextChannel] = message.guild.get_channel(
            await self.config.guild(message.guild).channel()  # type: ignore
        )
        if not log_channel:
            await self.config.guild(message.guild).toggle.clear()
            log.debug(
                f"Disabled voice note logging in {message.guild.name} because logging channel was not configured."
            )
            return

        if not log_channel.permissions_for(message.guild.me).send_messages:
            await self.config.guild(message.guild).toggle.clear()
            log.debug(
                f"Disabled voice note logging in {message.guild.name} because I do not have send message permission in the configured logging channel."
            )
            return

        try:
            text: Any = await self._transcribe_message(message)
        except speech.UnknownValueError:
            log.debug(
                f"Could not transcribe {message.jump_url} as response was empty.",
            )
            return
        except Exception as error:
            log.exception(
                f"Failed to transcribe {message.jump_url} due to an error.", exc_info=error
            )
            return

        embed: discord.Embed = await self._embed(text, message)
        view: JumpToMessageView = JumpToMessageView("Jump To Message", message.jump_url)

        await log_channel.send(embed=embed, view=view)

    @commands.guild_only()
    @commands.mod_or_permissions(manage_guild=True)
    @commands.group(name="voicenotelog", aliases=["vnl"])
    async def _voice_note_log(self, _: commands.GuildContext):
        """
        Voice note logging settings.
        """

    @_voice_note_log.command(name="channel")  # type: ignore
    async def _voice_note_log_channel(
        self, ctx: commands.GuildContext, channel: Optional[discord.TextChannel] = None
    ):
        """
        Configure the logging channel.
        """
        if not channel:
            await self.config.guild(ctx.guild).channel.clear()
            await ctx.send(
                "Cleared the voice note logging channel.",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        await self.config.guild(ctx.guild).channel.set(channel.id)
        await ctx.send(
            f"Configured the voice note logging channel to {channel.mention}!",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_voice_note_log.command(name="toggle")  # type: ignore
    async def _voice_note_log_toggle(self, ctx: commands.GuildContext, toggle: bool):
        """
        Toggle voice note logging.
        """
        await self.config.guild(ctx.guild).toggle.set(toggle)
        await ctx.send(
            f"Voice note logging is now {'enabled' if toggle else 'disabled'}.",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.bot_has_permissions(embed_links=True)
    @_voice_note_log.command(name="settings", aliases=["showsettings", "show"])  # type: ignore
    async def _voice_note_log_settings(self, ctx: commands.GuildContext):
        """
        View the voice note logging configuration settings.
        """
        data: Dict[str, Union[Optional[int], bool]] = await self.config.guild(ctx.guild).all()
        embed: discord.Embed = discord.Embed(
            title="Voice Note Logging Settings",
            description=(f"Channel: **{data['channel']}**\n" f"Toggle: **{data['toggle']}\n"),
            color=await ctx.embed_color(),
        )
        embed.set_thumbnail(url=getattr(ctx.guild.icon, "url", None))
        await ctx.send(
            embed=embed,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
