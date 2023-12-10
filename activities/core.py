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

from typing import Any, Final, List, Union

import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from .enums import Activity


class Activities(commands.Cog):
    """
    Discord Voice Channel Activities.
    """

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx)
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Author: **{humanize_list(self.__author__)}**",
            f"Cog Version: **{self.__version__}**",
        ]
        return "\n".join(text)

    @staticmethod
    async def create_activity_invite(
        channel: discord.VoiceChannel, activity: Union[Activity, int], **kwargs: Any
    ) -> discord.Invite:
        if isinstance(activity, Activity):
            activity = activity.value
        elif not isinstance(activity, int):
            raise TypeError(
                f"Excepted activities.enums.Activity or int, not {type(activity)}.",
            )

        return await channel.create_invite(
            reason="Created discord activities invite link.",
            target_type=discord.InviteTarget.embedded_application,
            target_application_id=activity,
            **kwargs,
        )

    async def _create_game(
        self, ctx: commands.Context, channel: discord.VoiceChannel, activity: Union[Activity, int]
    ) -> None:
        if isinstance(activity, Activity):
            activity = activity.value
        elif not isinstance(activity, int):
            raise TypeError(
                f"Excepted activities.enums.Activity or int, not {type(activity)}.",
            )

        try:
            invite: discord.Invite = await self.create_activity_invite(channel, activity)
        except discord.HTTPException:
            raise commands.UserFeedbackCheckFailure(
                "Something went wrong while creating the activity invite.",
            )

        await ctx.send(
            invite,
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @commands.guild_only()
    @commands.group(name="activity")  # type: ignore
    @commands.has_permissions(create_instant_invite=True, use_embedded_activities=True)
    @commands.bot_has_permissions(create_instant_invite=True, use_embedded_activities=True)
    async def _activity(self, _: commands.Context):
        """
        Base command for creating activity invite links.
        """

    @_activity.command(name="askaway")
    async def _ask_away(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Ask Away.
        """
        await self._create_game(ctx, channel, Activity.ask_away)

    @_activity.command(name="awkword")
    async def _awkword(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Awkword.
        """
        await self._create_game(ctx, channel, Activity.awkword)

    @_activity.command(name="bashout")
    async def _bash_out(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Bash Out
        """
        await self._create_game(ctx, channel, Activity.bash_out)

    @_activity.command(name="betrayal")
    async def _betrayal(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Betrayal.
        """
        await self._create_game(ctx, channel, Activity.betrayal)

    @_activity.command(name="blazing8s", aliases=["blazing"])
    async def _blazing(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Blazing 8s.
        """
        await self._create_game(ctx, channel, Activity.blazing_8s)

    @_activity.command(name="bobbleleague", aliases=["bobble"])
    async def _bobble_league(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Bobble League.
        """
        await self._create_game(ctx, channel, Activity.bobble_league)

    @_activity.command(name="checkersinthepark", aliases=["checkers"])
    async def _checkers_in_the_park(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Checkers In The Park.
        """
        await self._create_game(ctx, channel, Activity.checkers_in_the_park)

    @_activity.command(name="chessinthepark", aliases=["chess"])
    async def _chess_in_the_park(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Chess In The Park.
        """
        await self._create_game(ctx, channel, Activity.chess_in_the_park)

    @_activity.command(name="doodlecrew", aliases=["doodle"])
    async def _doodle_crew(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Doodle Crew.
        """
        await self._create_game(ctx, channel, Activity.doodle_crew)

    @_activity.command(name="decoder")
    async def _decoder(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Decoder.
        """
        await self._create_game(ctx, channel, Activity.decoder)

    @_activity.command(name="fishington")
    async def _fishington(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Fishington.
        """
        await self._create_game(ctx, channel, Activity.fishington)

    @_activity.command(name="garticphone", aliases=["gartic"])
    async def _gartic_phone(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Gartic Phone.
        """
        await self._create_game(ctx, channel, Activity.gartic_phone)

    @_activity.command(name="jamspace")
    async def _jamspace(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Jamspace.
        """
        await self._create_game(ctx, channel, Activity.jamspace)

    @_activity.command(name="knowwhatimeme", aliases=["meme"])
    async def _know_what_i_meme(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Know What I Meme.
        """
        await self._create_game(ctx, channel, Activity.know_what_i_meme)

    @_activity.command(name="landio", aliases=["land"])
    async def _land_io(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Land IO.
        """
        await self._create_game(ctx, channel, Activity.land_io)

    @_activity.command(name="letterleague", aliases=["letter"])
    async def _letter_league(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Letter League.
        """
        await self._create_game(ctx, channel, Activity.letter_league)

    @_activity.command(name="pokernight", aliases=["poker"])
    async def _poker_night(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Poker Night.
        """
        await self._create_game(ctx, channel, Activity.poker_night)

    @_activity.command(name="puttparty", aliases=["putt"])
    async def _putt_party(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Putt Party.
        """
        await self._create_game(ctx, channel, Activity.putt_party)

    @_activity.command(name="putts")
    async def _putts(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Putts.
        """
        await self._create_game(ctx, channel, Activity.putts)

    @_activity.command(name="sketchheads", aliases=["sketch"])
    async def _sketch_heads(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Sketch Heads.
        """
        await self._create_game(ctx, channel, Activity.sketch_heads)

    @_activity.command(name="sketchyartist", aliases=["sketchy"])
    async def _sketchy_artist(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Sketchy Artist.
        """
        await self._create_game(ctx, channel, Activity.sketchy_artist)

    @_activity.command(name="spellcast", aliases=["spell"])
    async def _spell(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Spell Cast.
        """
        await self._create_game(ctx, channel, Activity.spell_cast)

    @_activity.command(name="watchtogether", aliases=["watch"])
    async def _watch_together(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Watch Together.
        """
        await self._create_game(ctx, channel, Activity.watch_together)

    @_activity.command(name="wordsnacks", aliases=["word", "snacks"])
    async def _word_snacks(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Word Snacks.
        """
        await self._create_game(ctx, channel, Activity.word_snacks)

    @_activity.command(name="youtubetogether", aliases=["youtube"])
    async def _youtube_together(self, ctx: commands.Context, channel: discord.VoiceChannel):
        """
        Create an activity invite link for Youtube Together.
        """
        await self._create_game(ctx, channel, Activity.youtube_together)
