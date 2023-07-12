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

import random
from typing import Dict, List, Optional

import aiohttp
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, pagify

from .utils import raise_for_status


class AnimalAPI:
    def __init__(self, session: aiohttp.ClientSession):
        self.session: aiohttp.ClientSession = session
        self.endpoints: Dict[str, Dict[str, List[Dict[str, str]]]] = {
            "images": {
                "bear": [{"url": "https://and-here-is-my-code.glitch.me/img/bear", "key": "Link"}],
                "bird": [{"url": "https://some-random-api.com/animal/bird", "key": "image"}],
                "dolphin": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/dolphin", "key": "Link"}
                ],
                "duck": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/duck", "key": "Link"},
                    {"url": "https://random-d.uk/api/v2/quack", "key": "url"},
                ],
                "elephant": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/elephant", "key": "Link"}
                ],
                "giraffe": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/giraffe", "key": "Link"}
                ],
                "hippo": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/hippo", "key": "Link"}
                ],
                "horse": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/horse", "key": "Link"}
                ],
                "killerwhale": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/killerwhale", "key": "Link"}
                ],
                "lion": [{"url": "https://and-here-is-my-code.glitch.me/img/lion", "key": "Link"}],
                "panda": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/panda", "key": "Link"},
                    {"url": "https://some-random-api.com/animal/panda", "key": "image"},
                ],
                "pig": [{"url": "https://and-here-is-my-code.glitch.me/img/pig", "key": "Link"}],
                "redpanda": [
                    {"url": "https://some-random-api.com/animal/red_panda", "key": "image"}
                ],
                "shark": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/shark", "key": "Link"}
                ],
                "snake": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/snakes", "key": "Link"}
                ],
                "spider": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/spiders", "key": "Link"}
                ],
                "turtle": [
                    {"url": "https://and-here-is-my-code.glitch.me/img/turtle", "key": "Link"}
                ],
                "fox": [
                    {"url": "https://some-random-api.com/animal/fox", "key": "image"}
                ],
                "koala": [
                    {"url": "https://some-random-api.com/animal/koala", "key": "image"}
                ],
                "kangaroo": [
                    {"url": "https://some-random-api.com/animal/kangaroo", "key": "image"}
                ],
                "raccoon": [
                    {"url": "https://some-random-api.com/animal/raccoon", "key": "image"}
                ]
            },
            "facts": {
                "bear": [
                    {"url": "https://and-here-is-my-code.glitch.me/facts/bear", "key": "Link"}
                ],
                "bird": [{"url": "https://some-random-api.com/animal/bird", "key": "fact"}],
                "fox": [{"url": "https://some-random-api.ml/facts/fox", "key": "fact"}],
                "giraffe": [
                    {"url": "https://and-here-is-my-code.glitch.me/facts/giraffe", "key": "Link"}
                ],
                "lion": [
                    {"url": "https://and-here-is-my-code.glitch.me/facts/lion", "key": "Link"}
                ],
                "redpanda": [{"url": "https://some-random-api.com/animal/red_panda", "key": "facts"}],
                "panda": [{"url": "https://some-random-api.com/animal/panda", "key": "fact"}],
                "shark": [
                    {"url": "https://and-here-is-my-code.glitch.me/facts/shark", "key": "Link"}
                ],
                "snake": [
                    {"url": "https://and-here-is-my-code.glitch.me/facts/snake", "key": "Link"}
                ],
                "fox": [
                    {"url": "https://some-random-api.com/animal/fox", "key": "fact"}
                ],
                "koala": [
                    {"url": "https://some-random-api.com/animal/koala", "key": "fact"}
                ],
                "kangaroo": [
                    {"url": "https://some-random-api.com/animal/kangaroo", "key": "fact"}
                ],
                "raccoon": [
                    {"url": "https://some-random-api.com/animal/raccoon", "key": "fact"}
                ]
            },
        }

    async def image(self, animal: str):
        endpoint = random.choice(self.endpoints["images"][animal])
        async with self.session.get(url=endpoint["url"]) as response:
            if response.status != 200:
                return raise_for_status(response)
            return (await response.json())[endpoint["key"]]

    async def fact(self, animal: str):
        endpoint = random.choice(self.endpoints["facts"][animal])
        async with self.session.get(url=endpoint["url"]) as response:
            if response.status != 200:
                return raise_for_status(response)
            try:
                return (await response.json())[endpoint["key"]]
            except aiohttp.ContentTypeError:
                return "Failed to generate Fact."


class CatAPI:
    def __init__(self, ctx: commands.Context, session: aiohttp.ClientSession):
        self.ctx: commands.Context = ctx
        self.bot: Red = self.ctx.bot
        self.session: aiohttp.ClientSession = session
        self.base: str = "https://api.thecatapi.com/v1/"
        self.traits: List[str] = [
            "Experimental",
            "Hairless",
            "Natural",
            "Rare",
            "Rex",
            "Suppressed tail",
            "Short legs",
            "Hypoallergenic",
            "Indoor",
            "Lap",
        ]
        self.scale: List[str] = [
            "Adaptability",
            "Affection level",
            "Child friendly",
            "Dog friendly",
            "Energy level",
            "Grooming",
            "Health issues",
            "Intelligence",
            "Shedding level",
            "Social needs",
            "Stranger friendly",
            "Vocalisation",
        ]

    async def image(self, breed: Optional[str] = None):
        url = self.base + "images/search?has_breeds=1"
        keys = await self.bot.get_shared_api_tokens("thecatapi")
        token = keys.get("api_key")
        if breed:
            breeds = {}
            async with self.session.get(
                url=self.base + "breeds", headers={"x-api-key": token}
            ) as response:
                if response.status != 200:
                    return raise_for_status(response)
                breed_list = await response.json()
            for x in breed_list:
                breeds[x["name"].lower()] = x["id"]
            if breed.lower() not in breeds:
                return None, None, None
            url += f"&breed_id={breeds[breed.lower()]}"
        async with self.session.get(url=url, headers={"x-api-key": token}) as response:
            if response.status != 200:
                return raise_for_status(response)
            response = (await response.json())[0]
            details = ""
            traits = []
            urls = {}
            for x, y in response["breeds"][0].items():
                if x not in ["id", "name", "country_codes", "country_code"]:
                    x = x.capitalize().replace("_", " ")
                    if x in ["Cfa url", "Vetstreet url", "Vcahospitals url", "Wikipedia url"]:
                        x = (
                            x.split(" ")[0]
                            .replace("Cfa", "CFA")
                            .replace("Vcahospitals", "VCA Hospitals")
                        )
                        urls[x] = y.replace("(", "").replace(")", "")
                    elif x == "Origin":
                        origin = f"**{x}:** {y} ({response['breeds'][0]['country_code']})\n"
                    elif x == "Weight":
                        weight = f"**{x}:** {y['imperial']}lb ({y['metric']}kg)\n"
                    elif x == "Life span":
                        details += f"**{x}:** {y} years\n"
                    elif x in self.traits:
                        if y == 1:
                            traits.append(x)
                    elif x in self.scale:
                        y = (
                            str(y)
                            .replace("1", "Bad")
                            .replace("2", "Poor")
                            .replace("3", "Average")
                            .replace("4", "Above average")
                            .replace("5", "Good")
                        )
                        details += f"**{x}:** {y}\n"
                    else:
                        details += f"**{x}:** {y}\n"
            details = origin + details  # type: ignore
            details += f"**Traits:** {', '.join(traits)}\n" if traits else ""
            details += weight  # type: ignore
            if urls:
                details += f"**URLs:** {' • '.join([f'[{x}]({y})' for x, y in urls.items()])}"
            return response["url"], response["breeds"][0]["name"], details

    async def breeds(self):
        keys = await self.bot.get_shared_api_tokens("thecatapi")
        token = keys.get("api_key")
        async with self.session.get(
            url=self.base + "breeds", headers={"x-api-key": token}
        ) as response:
            if response.status != 200:
                return raise_for_status(response)
            breed_list = await response.json()
        breeds = [x["name"] for x in breed_list]
        breed_count = len(breeds)
        breeds = humanize_list(breeds)
        pages = pagify(breeds, delims=[" "], page_length=2048)
        pages = [x for x in pages]
        return pages, breed_count


class DogAPI:
    def __init__(self, ctx: commands.Context, session: aiohttp.ClientSession):
        self.ctx: commands.Context = ctx
        self.bot: Red = self.ctx.bot
        self.session: aiohttp.ClientSession = session
        self.base: str = "https://api.thedogapi.com/v1/"

    async def image(self, breed: Optional[str] = None):
        url = self.base + "images/search?has_breeds=1"
        keys = await self.bot.get_shared_api_tokens("thedogapi")
        token = keys.get("api_key")
        if breed:
            breeds = {}
            async with self.session.get(
                url=self.base + "breeds", headers={"x-api-key": token}
            ) as response:
                if response.status != 200:
                    return raise_for_status(response)
                breed_list = await response.json()
            for x in breed_list:
                breeds[x["name"].lower()] = x["id"]
            if breed.lower() not in breeds:
                return None, None, None
            url += f"&breed_id={breeds[breed.lower()]}"
        async with self.session.get(url=url, headers={"x-api-key": token}) as response:
            if response.status != 200:
                return raise_for_status(response)
            response = (await response.json())[0]
            details = ""
            for x, y in response["breeds"][0].items():
                if x not in ["id", "name"]:
                    x = x.capitalize().replace("_", " ")
                    if x == "Height":
                        height = f"**{x}:** {y['imperial']}in ({y['metric']}cm)\n"
                        continue
                    if x == "Weight":
                        weight = f"**{x}:** {y['imperial']}lb ({y['metric']}kg)\n"
                        continue
                    details += f"**{x}:** {y}\n"
            details += height + weight  # type: ignore
            return response["url"], response["breeds"][0]["name"], details

    async def breeds(self):
        keys = await self.bot.get_shared_api_tokens("thedogapi")
        token = keys.get("api_key")
        async with self.session.get(
            url=self.base + "breeds", headers={"x-api-key": token}
        ) as response:
            if response.status != 200:
                return raise_for_status(response)
            breed_list = await response.json()
        breeds = [x["name"] for x in breed_list]
        breed_count = len(breeds)
        breeds = humanize_list(breeds)
        pages = pagify(breeds, delims=[" "], page_length=2048)
        pages = [x for x in pages]
        return pages, breed_count
