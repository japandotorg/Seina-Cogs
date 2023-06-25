from __future__ import annotations

import io
from dataclasses import dataclass

import pydub.exceptions
from redbot.core import commands
from shazamio import Shazam as Client


@dataclass
class ShazamTrack:
    song: str
    artist: str
    metadata: list
    cover_art: str
    url: str


# https://github.com/joinemm/miso-bot/blob/master/modules/shazam.py
class ShazamClient:
    def __init__(self, cog: commands.Cog) -> None:
        self.cog: commands.Cog = cog
        self.shazam: Client = Client()

    async def recognize_file(self, file: bytes) -> ShazamTrack | None:
        try:
            data = await self.shazam.recognize_song(file)
            track = data["track"]
        except (IndexError, KeyError, pydub.exceptions.CouldntDecodeError):
            return None
        return ShazamTrack(
            track["title"],
            track["subtitle"],
            track["sections"][0]["metadata"],
            track["images"]["coverart"],
            track["url"],
        )

    async def recognize_from_url(self, url: str) -> ShazamTrack | None:
        async with self.cog.session.get(url) as response:
            buffer = io.BytesIO(await response.read())
            return await self.recognize_file(buffer.read())
