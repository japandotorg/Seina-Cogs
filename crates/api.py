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
    