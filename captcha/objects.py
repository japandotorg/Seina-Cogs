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

# https://github.com/lepture/captcha/blob/master/src/captcha/image.py

import random
from io import BytesIO
from typing import TYPE_CHECKING, List, Optional, Tuple, TypeAlias, Union

from PIL.Image import BILINEAR, QUAD, Image
from PIL.Image import new as create
from PIL.ImageDraw import Draw, ImageDraw
from PIL.ImageFilter import SMOOTH
from PIL.ImageFont import FreeTypeFont, truetype

if TYPE_CHECKING:
    from .core import Captcha

ColorTuple: TypeAlias = Union[Tuple[int, int, int], Tuple[int, int, int, int]]


class CaptchaObj:
    lookup_table: List[int] = [int(index * 1.97) for index in range(256)]

    def __init__(
        self,
        cog: "Captcha",
        width: int = 160,
        height: int = 60,
        font_sizes: Optional[Tuple[int, ...]] = None,
    ) -> None:
        super().__init__()
        self._cog: "Captcha" = cog

        self._width: int = width
        self._height: int = height

        self._font: str = cog.font_data
        self._truefonts: List[FreeTypeFont] = []
        self._font_sizes: Optional[Tuple[int, ...]] = font_sizes or (42, 50, 56)

    @property
    def truefonts(self) -> List[FreeTypeFont]:
        if self._truefonts:
            return self._truefonts
        self._truefonts: List[FreeTypeFont] = [
            truetype(str(self._font), size) for size in self._font_sizes  # type: ignore
        ]
        return self._truefonts

    @staticmethod
    def _create_noise_curve(image: Image, color: ColorTuple) -> Image:
        w, h = image.size
        x1: int = random.randint(0, int(w / 5))
        x2: int = random.randint(w - int(w / 5), w)
        y1: int = random.randint(int(h / 5), h - int(h / 5))
        y2: int = random.randint(y1, h - int(h / 5))
        points: List[int] = [x1, y1, x2, y2]
        end: int = random.randint(160, 200)
        start: int = random.randint(0, 20)
        Draw(image).arc(points, start, end, fill=color)
        return image

    @staticmethod
    def _create_noise_dots(
        image: Image,
        color: ColorTuple,
        width: int = 3,
        number: int = 30,
    ) -> Image:
        draw: ImageDraw = Draw(image)
        w, h = image.size
        while number:
            x1: int = random.randint(0, w)
            y1: int = random.randint(0, h)
            draw.line(((x1, y1), (x1 - 1, y1 - 1)), fill=color, width=width)
            number -= 1
        return image

    def _draw_character(
        self,
        string: str,
        draw: ImageDraw,
        color: ColorTuple,
    ) -> Image:
        font = random.choice(self.truefonts)
        _, _, w, h = draw.multiline_textbbox((1, 1), string, font=font)

        dx1: int = random.randint(0, 4)
        dy1: int = random.randint(0, 6)
        image: Image = create("RGBA", (w + dx1, h + dy1))
        Draw(image).text((dx1, dy1), string, font=font, fill=color)

        image: Image = image.crop(image.getbbox())
        image: Image = image.rotate(random.uniform(-30, 30), BILINEAR, expand=True)

        dx2: float = w * random.uniform(0.1, 0.3)
        dy2: float = h * random.uniform(0.2, 0.3)
        x1: int = int(random.uniform(-dx2, dx2))
        y1: int = int(random.uniform(-dy2, dy2))
        x2: int = int(random.uniform(-dx2, dx2))
        y2: int = int(random.uniform(-dy2, dy2))
        w2: int = w + abs(x1) + abs(x2)
        h2: int = h + abs(y1) + abs(y2)
        data: Tuple[int, int, int, int, int, int, int, int] = (
            x1,
            y1,
            -x1,
            h2 - y2,
            w2 + x2,
            h2 + y2,
            w2 - x2,
            -y1,
        )
        image: Image = image.resize((w2, h2))
        image: Image = image.transform((w, h), QUAD, data)
        return image

    def _create_captcha_image(
        self,
        chars: str,
        color: ColorTuple,
        background: ColorTuple,
    ) -> Image:
        image: Image = create("RGB", (self._width, self._height), background)
        draw: ImageDraw = Draw(image)

        images: List[Image] = []
        for char in chars:
            if random.random() > 0.5:
                images.append(self._draw_character(" ", draw, color))
            images.append(self._draw_character(char, draw, color))

        text_width: int = sum([im.size[0] for im in images])

        width: int = max(text_width, self._width)
        image: Image = image.resize((width, self._height))

        average: int = int(text_width / len(chars))
        rand: int = int(0.25 * average)
        offset: int = int(average * 0.1)

        for img in images:
            w, h = img.size
            mask: Image = img.convert("L").point(self.lookup_table)
            image.paste(img, (offset, int((self._height - h) / 2)), mask)
            offset: int = offset + w + random.randint(-rand, 0)

        if width > self._width:
            image: Image = image.resize((self._width, self._height))

        return image

    def _generate(self, chars: str) -> Image:
        background: ColorTuple = random_color(238, 255)
        color: ColorTuple = random_color(10, 200, random.randint(220, 255))
        image: Image = self._create_captcha_image(chars, color, background)
        self._create_noise_dots(image, color)
        self._create_noise_curve(image, color)
        image: Image = image.filter(SMOOTH)
        return image

    def generate(self, chars: str, format: str = "png") -> BytesIO:
        image: Image = self._generate(chars)
        byte: BytesIO = BytesIO()
        image.save(byte, format=format)
        byte.seek(0)
        return byte

    def write(self, chars: str, output: str, format: str = "png") -> None:
        image: Image = self._generate(chars)
        image.save(output, format=format)


def random_color(
    start: int,
    end: int,
    opacity: Optional[int] = None,
) -> ColorTuple:
    red: int = random.randint(start, end)
    green: int = random.randint(start, end)
    blue: int = random.randint(start, end)
    if opacity is None:
        return (red, green, blue)
    return (red, green, blue, opacity)
