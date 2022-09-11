import aiohttp
from typing import Final, Tuple, Union

BASE_URL: Final[str] = "https://crates.io/api/v1"

class CratesIOAPI:
    def __init__(
        self,
        session: aiohttp.ClientSession,
    ):
        self.session: aiohttp.ClientSession = session
        
    async def _get_crate_data(
        self,
        crate: str
    ) -> Union[dict, None]:
        response: aiohttp.ClientResponse = await self.session.get(BASE_URL + f"/crates/{crate}")
        if response.status == 200:
            return await response.json()
        
    async def _keyfetch_or_none(
        self,
        endpoint: str,
        key: Union[str, list],
        list_index: Union[int, None] = None
    ) -> Union[Tuple[dict, list, str], Tuple[int, bool, None]]:
        response: aiohttp.ClientResponse = await self.session.get(BASE_URL + endpoint)
        if response.status == 200:
            data: dict = await response.json()
            try:
                if isinstance(key, str):
                    data = data[key]
                else:
                    for k in key:
                        data = data[k]
                
                if list_index is not None and isinstance(data, list):
                    return data[list_index]
                return data
            except KeyError:
                return None
            
    async def _get_crate_downloads(self, crate: str) -> Union[list, None]:
        return await self._keyfetch_or_none(f"/crates/{crate}/downloads", ["meta", "extra_downloads"])
    
    async def _get_crate_owners(self, crate: str) -> Union[list, None]:
        return await self._keyfetch_or_none(f"/crates/{crate}owners", "users")
    
    async def _get_crate_owner_users(self, crate: str) -> Union[list, None]:
        return await self._keyfetch_or_none(f"/crates/{crate}/owner_user", "users")
    
    async def _get_crate_owner_teams(self, crate: str) -> Union[list, None]:
        return await self._keyfetch_or_none(f"/crates/{crate}owner_team", "teams")
    