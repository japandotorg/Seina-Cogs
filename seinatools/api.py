import datetime
from io import BytesIO
from types import TracebackType
from typing import List, Optional, Type, Union

import aiohttp
import discord
import yarl
from typing_extensions import Self


class APIError(Exception):
    """
    Base class for all exceptions.
    """



class APIClient:
    def __init__(self, api_key: str, *, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.base_url: yarl.URL = yarl.URL("https://api.jeyy.xyz/v2/")
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.new_session = False
        if session is None:
            self.session = aiohttp.ClientSession()
            self.new_session = True
        else:
            self.session = session

    async def close(self) -> None:
        if self.new_session:
            if self.session.closed:
                raise TypeError("session is already closed")
            await self.session.close()
        else:
            raise TypeError("session was created manually. call .close() on the session instead.")

    async def __aenter__(self) -> Self:
        if self.session.closed:
            raise TypeError("session has closed.")

        return self

    async def __aexit__(
        self, exc_type: Type[BaseException], exc: BaseException, tb: TracebackType
    ) -> None:
        try:
            await self.close()
        except:
            pass

    async def spotify(
        self,
        title: str,
        cover_url: str,
        duration: Union[datetime.timedelta, int, float],
        start: Union[datetime.datetime, float],
        artists: List[str],
    ) -> BytesIO:
        if isinstance(duration, datetime.timedelta):
            duration = int(duration.seconds)
        else:
            duration = int(duration)

        if isinstance(start, datetime.datetime):
            start = float(start.timestamp())
        else:
            start = float(start)

        params = {
            "title": str(title),
            "cover_url": str(cover_url),
            "duration_seconds": duration,
            "start_timestamp": start,
            "artists": artists,
        }

        async with self.session.get(
            self.base_url / "discord/spotify", params=params, headers=self.headers
        ) as response:
            if response.status != 200:
                raise APIError(await response.text())

            data = await response.read()

        buffer = BytesIO(data)
        return buffer

    async def spotify_from_object(self, spotify: discord.Spotify) -> BytesIO:
        if spotify.__class__.__name__ != "Spotify":
            raise TypeError(
                f"discord.Spotify is expected, got {spotify.__class__.__name__} instead."
            )

        kwargs = {
            "title": spotify.title,
            "cover_url": spotify.album_cover_url,
            "duration": spotify.duration.seconds,
            "start": spotify.start.timestamp(),
            "artists": spotify.artists,
        }

        return await self.spotify(**kwargs)
