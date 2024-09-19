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

import io
import asyncio
import logging
from PIL import Image
from typing import Any, Dict, Literal, Optional, cast

import transformers
from tensorflow import config as conf

try:
    import regex as re
except ModuleNotFoundError:
    import re as re


log: logging.Logger = logging.getLogger("red.seina.screenshot.filter")


class Filter:
    DEVICE: Literal["cpu", "cuda"] = "cuda" if conf.list_physical_devices("GPU") else "cpu"

    def __init__(self) -> None:
        self.model: transformers.Pipeline = transformers.pipeline(
            "image-classification", model="Falconsai/nsfw_image_detection", device=self.DEVICE
        )

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
        img: Image.ImageFile.ImageFile = Image.open(io.BytesIO(image))
        response: Dict[str, Any] = cast(
            Dict[str, Any], await asyncio.to_thread(lambda: self.model(img))
        )
        pred: str = max(response, key=lambda x: x["score"])
        return pred["label"] == "nsfw"
