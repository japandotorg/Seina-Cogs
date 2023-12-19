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

import io
import yarl
import asyncio
import aiohttp
from urllib.parse import quote_plus
from typing import (
    Dict,
    Final,
    Literal,
    List,
    Optional,
    Union,
    Any,
)

import backoff

import discord
from redbot.core.bot import Red
from redbot.core import commands


class DiffusionError(discord.errors.DiscordException):
    pass


class StableDiffusion(commands.Cog):
    """Stable Diffusion using the Replicate API."""

    __author__: Final[List[str]] = ["inthedark.org"]
    __version__: Final[str] = "0.1.0"

    URL: Dict[str, str] = {
        "replicate": "https://inpainter.vercel.app/api/predictions",
    }
    HEADERS: Dict[str, str] = {"Content-Type": "application/json"}

    def __init__(self, bot: Red) -> None:
        self.bot: Red = bot
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    async def cog_unload(self) -> None:
        if self.session:
            await self.session.close()

    async def _image_to_file(
        self, url: Union[str, yarl.URL], prompt: str, spoiler: bool = False
    ) -> discord.File:
        image: bytes = await (await self.session.get(url)).read()
        return discord.File(
            io.BytesIO(image),
            filename=f"{'SPOILER_' if spoiler else ''}{quote_plus(prompt)}.png",
        )

    @backoff.on_exception(
        backoff.expo,
        aiohttp.ClientResponseError,
        max_tries=3,
        giveup=lambda x: x.status == 402,  # type: ignore
    )
    async def _request(
        self,
        verb: Literal["GET", "POST"],
        url: Union[str, yarl.URL] = "",
        params: Dict[str, Any] = {},
        headers: Dict[str, Any] = {},
        data: Optional[Dict[str, Any]] = None,
        service: Literal["replicate"] = "replicate",
    ) -> aiohttp.ClientResponse:
        response: aiohttp.ClientResponse = await self.session.request(
            verb,
            f"{self.URL[service]}{url}",
            params=params,
            headers={**headers, **self.HEADERS},
            json=data,
        )
        response.raise_for_status()
        return response

    async def _start_job(self, prompt: str) -> str:
        payload = {"prompt": prompt}
        response = await self._request("POST", data=payload)
        response = await response.json(content_type=None)
        if response.get("error"):
            raise DiffusionError(response["error"])
        return response["id"]

    async def _get_job(self, id: str) -> List[str]:
        checks = 0
        while True:
            if checks >= 45:
                await self._request("POST", url=f"/{id}/cancel", data={})
                raise DiffusionError(
                    "Couldn't get a result after 90 seconds. Aborting...",
                )
            response = await self._request("GET", url=f"{id}")
            response = await response.json(content_type=None)
            if response.get("error"):
                raise DiffusionError(response["error"])
            if response.get("completed_at"):
                return response["output"]
            checks += 1
            await asyncio.sleep(2)

    @commands.command(name="stablediffusion", aliases=["dream", "diffusion"])
    async def _stable_diffusion(self, ctx: commands.Context, *, prompt: str) -> None:
        """
        Generate art using Replicate Stable Diffusion.
        """
        await ctx.typing()
        try:
            job_id: str = await self._start_job(prompt)
            images: List[str] = await self._get_job(job_id)
        except DiffusionError as e:
            await ctx.send(
                f"Uh Oh! Something went wrong...\n{e}",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        except aiohttp.ClientResponseError as e:
            await ctx.send(
                f"Uh Oh! Recieved status code: `{e.status}`\n{e.message}",
                reference=ctx.message.to_reference(fail_if_not_exists=False),
                allowed_mentions=discord.AllowedMentions(replied_user=False),
            )
            return
        file: discord.File = await self._image_to_file(images[0], prompt)
        await ctx.send(
            embed=discord.Embed(
                description=f"Prompt: {prompt}",
                color=await ctx.embed_color(),
            ),
            files=[file],
        )
