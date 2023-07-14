import logging
from datetime import timedelta
from types import TracebackType
from typing import Any, Dict, Optional, Tuple, Type, Union, final

import aiohttp
from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from redbot.core import commands
from typing_extensions import Self

from .constants import (
    BASE_URL,
    SESSION_TIMEOUT,
    URL_EXPIRE_AFTER,
    Endpoints,
    Methods,
    Ratings,
    StrOrUrl,
)

log: logging.Logger = logging.getLogger("red.seina.conversationgames.http")


class HTTPClient:
    __slots__: Tuple = ("_base_url", "_session")

    def __init__(
        self,
        base_url: Optional[StrOrUrl] = BASE_URL,
        session: Optional[CachedSession] = None,
    ) -> None:
        self._base_url: Optional[StrOrUrl] = base_url
        self._session: Optional[CachedSession] = session

    async def __request(self, method: Methods, route: str, **kwargs: Any) -> Dict[str, Any]:
        url = self._base_url + route  # type: ignore

        if not self._session:
            timeout = aiohttp.ClientTimeout(total=SESSION_TIMEOUT)
            cache = SQLiteBackend(
                cache_name="~/.cache/conversationgames.db",
                expire_after=timedelta(seconds=3),
                allowed_methods=["GET", "HEAD"],
                urls_expire_after=URL_EXPIRE_AFTER,
                use_temp=True,
            )
            self._session = CachedSession(cache=cache, timeout=timeout)

        async with self._session.request(method, url, **kwargs) as response:
            if response.status != 200:
                log.error("Truth&Dare API down!")
                raise commands.UserFeedbackCheckFailure(
                    "Something went wrong requesting the truth&dare api!"
                )
            return await response.json()

    async def request(
        self, method: Methods, route: str, **kwargs: Any
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        return await self.__request(method, route, **kwargs)

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        if self._session and self._session.closed:  # type: ignore
            log.error("Session is closed, unable to request the endpoint.")
            raise commands.UserFeedbackCheckFailure(
                "Something went wrong with the session, unable to request the endpoint."
            )

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()


@final
class TruthOrDareAPIClient(HTTPClient):
    def __init__(self, session: Optional[CachedSession] = None):
        super().__init__(BASE_URL, session)

    async def _request(
        self, endpoint: Endpoints, rating: Optional[Ratings] = None
    ) -> Dict[str, Union[str, Dict[str, str]]]:
        params = {"rating": rating} if rating else None
        return await self.request("GET", f"/{endpoint}", params=params)
