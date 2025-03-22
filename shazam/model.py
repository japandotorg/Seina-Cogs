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
import logging
from pydantic import BaseModel, ConfigDict, Field
from typing import TYPE_CHECKING, Any, Dict, List

from redbot.core import commands
from shazamio.exceptions import BadCityName, BadCountryName
from shazamio.api import Shazam as AudioAlchemist
from aiohttp_retry import ExponentialRetry as Pulse
from shazamio.schemas.playlist.playlist import PlayList
from shazamio.serializers import Serialize as Shazamalize
from shazamio.schemas.models import TrackInfo as Track
from shazamio.client import HTTPClient as SoundWaveNavigator
from shazamio_core.shazamio_core import SearchParams as SonicBlueprint

from .utils import TopFlags
from .types import GENRE, Genre

if TYPE_CHECKING:
    from .core import Shazam as Cog


log: logging.Logger = logging.getLogger("red.seina.shazam.model")


class Shazamed(BaseModel):
    track: Track
    metadata: str
    share: Dict[str, str] = Field(default_factory=dict)

    model_config: ConfigDict = ConfigDict(arbitrary_types_allowed=True)


class Shazam:
    def __init__(self, cog: "Cog") -> None:
        self.cog: "Cog" = cog
        self.alchemist: AudioAlchemist = AudioAlchemist(
            http_client=SoundWaveNavigator(
                retry_options=Pulse(
                    attempts=2, max_timeout=420.69, statuses={500, 502, 503, 504, 429}
                )
            ),
        )

    async def recognize(self, file: bytes, *, duration: int = 10) -> Shazamed:
        data: Dict[str, Any] = await self.alchemist.recognize(
            file, options=SonicBlueprint(segment_duration_seconds=duration)
        )
        try:
            track: Dict[str, Any] = data["track"]
        except (IndexError, KeyError):
            raise ValueError(
                "I was unable to recognize any song from this.",
            )
        metadata: str = "\n".join(
            [
                "- **{}**: {}".format(section["title"], section["text"])
                for section in track["sections"][0]["metadata"]
            ]
        )
        return Shazamed(
            track=await asyncio.to_thread(Shazamalize.track, track),
            metadata=metadata,
            share=track["share"],
        )

    async def recognize_from_url(self, url: str, duration: int = 10) -> Shazamed:
        async with self.cog.session.get(url) as response:
            return await self.recognize(await response.read(), duration=duration)

    async def top_world(self, limit: int = 10) -> List[PlayList]:
        tracks: Dict[str, Any] = await self.alchemist.top_world_tracks(limit=limit)
        playlists: List[PlayList] = Shazamalize.playlists(tracks)
        return playlists

    async def top_world_genre(self, genre: Genre, *, limit: int = 10) -> List[PlayList]:
        tracks: Dict[str, Any] = await self.alchemist.top_world_genre_tracks(
            genre=GENRE[genre.lower()], limit=limit
        )
        playlists: List[PlayList] = Shazamalize.playlists(tracks)
        return playlists

    async def top_country(self, country: str, *, limit: int = 10) -> List[PlayList]:
        tracks: Dict[str, Any] = await self.alchemist.top_country_tracks(
            country_code=country.upper(), limit=limit
        )
        playlists: List[PlayList] = Shazamalize.playlists(tracks)
        return playlists

    async def top_country_genre(
        self, country: str, genre: Genre, *, limit: str = 10
    ) -> List[PlayList]:
        tracks: Dict[str, Any] = await self.alchemist.top_country_genre_tracks(
            country_code=country.upper(), genre=GENRE[genre.lower()], limit=limit
        )
        playlists: List[PlayList] = Shazamalize.playlists(tracks)
        return playlists

    async def top_city(
        self, country: str, city: str, *, limit: int = 10
    ) -> List[PlayList]:
        tracks: Dict[str, Any] = await self.alchemist.top_city_tracks(
            country_code=country.upper(), city_name=city.title(), limit=limit
        )
        playlists: List[PlayList] = Shazamalize.playlists(tracks)
        return playlists

    async def from_flags(self, flags: TopFlags) -> List[PlayList]:
        if flags.city and not flags.country:
            raise commands.UserFeedbackCheckFailure(
                "The city flag must be used together with the country flag."
            )
        if flags.country:
            if flags.city:
                if flags.genre:
                    raise commands.UserFeedbackCheckFailure(
                        "Cannot use the genre flag while searching through cities."
                    )
                try:
                    playlists: List[PlayList] = await self.top_city(
                        flags.country, flags.city, limit=flags.limit
                    )
                except (BadCityName, BadCountryName) as error:
                    raise commands.UserFeedbackCheckFailure(str(error))
            else:
                try:
                    playlists: List[PlayList] = await self.top_country(
                        flags.country, limit=flags.limit
                    )
                except BadCountryName as error:
                    raise commands.UserFeedbackCheckFailure(str(error))
        elif flags.genre:
            if flags.country:
                try:
                    playlists: List[PlayList] = await self.top_country_genre(
                        flags.country, flags.genre, limit=flags.limit
                    )
                except BadCountryName as error:
                    raise commands.UserFeedbackCheckFailure(str(error))
            else:
                playlists: List[PlayList] = await self.top_world_genre(
                    flags.genre, limit=flags.limit
                )
        else:
            playlists: List[PlayList] = await self.top_world(limit=flags.limit)
        return playlists
