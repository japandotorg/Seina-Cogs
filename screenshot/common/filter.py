"""
MIT License

Copyright (c) 2024-present japandotorg

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

# isort: off
import os
import io
import asyncio
import logging
from PIL import Image
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union, cast

import discord

import torch
import transformers

if TYPE_CHECKING:
    from ..core import Screenshot

try:
    import regex as re
except ModuleNotFoundError:
    import re as re
# isort: on


log: logging.Logger = logging.getLogger("red.seina.screenshot.filter")


class Filter:
    def __init__(self, cog: "Screenshot") -> None:
        self.cog: "Screenshot" = cog
        self.models: Dict[Literal["small", "normal", "large"], transformers.Pipeline] = (
            discord.utils.MISSING
        )

    def maybe_setup_models(self) -> None:
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
        if self.models is discord.utils.MISSING:
            self.models: Dict[Literal["small", "normal", "large"], transformers.Pipeline] = {
                "small": transformers.pipeline(
                    "image-classification",
                    model="AdamCodd/vit-base-nsfw-detector",
                    device=torch.device("cpu"),
                ),
                "normal": transformers.pipeline(
                    "image-classification",
                    model="MichalMlodawski/nsfw-image-detection-large",
                    device=torch.device("cpu"),
                ),
                "large": transformers.pipeline(
                    "image-classification",
                    model="Falconsai/nsfw_image_detection",
                    device=torch.device("cpu"),
                ),
            }

    @staticmethod
    def is_valid_url(url: str) -> bool:
        regex: re.Pattern[str] = re.compile(
            r"^https?://"
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
            r"localhost|"
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            r"(?::\d+)?"
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        match: Optional[re.Match[str]] = regex.search(url)
        return match is not None

    async def read(self, image: bytes) -> bool:
        model: Literal["small", "normal", "large"] = await self.cog.config.nsfw()
        if model.lower() == "small":
            return await asyncio.to_thread(lambda: self.small(image))
        elif model.lower() == "normal":
            return await asyncio.to_thread(lambda: self.normal(image))
        elif model.lower() == "large":
            return await asyncio.to_thread(lambda: self.large(image))
        raise RuntimeError("No model named '{}' found.".format(model.lower()))

    def small(self, image: bytes) -> bool:
        img: Image.ImageFile.ImageFile = Image.open(io.BytesIO(image))
        response: List[Dict[str, Union[str, float]]] = cast(
            List[Dict[str, Union[str, float]]], self.models["small"](img)
        )
        pred: Dict[str, Union[str, float]] = max(response, key=lambda x: x["score"])
        return cast(str, pred["label"]).lower() == "nsfw"

    def normal(self, image: bytes) -> bool:
        img: Image.ImageFile.ImageFile = Image.open(io.BytesIO(image))
        response: List[Dict[str, Union[str, float]]] = cast(
            List[Dict[str, Union[str, float]]], self.models["normal"](img)
        )
        pred: Dict[str, Union[str, float]] = max(response, key=lambda x: x["score"])
        return cast(str, pred["label"]).lower() != "safe"

    def large(self, image: bytes) -> bool:
        img: Image.ImageFile.ImageFile = Image.open(io.BytesIO(image))
        response: List[Dict[str, Union[str, float]]] = cast(
            List[Dict[str, Union[str, float]]], self.models["large"](img)
        )
        pred: Dict[str, Union[str, float]] = max(response, key=lambda x: x["score"])
        return cast(str, pred["label"]).lower() == "nsfw"
