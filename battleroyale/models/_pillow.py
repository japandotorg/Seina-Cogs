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

# much of this code has been taken from https://github.com/shahriyardx/easy-pil/tree/master

from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

Color = Union[int, str, Tuple[int, int, int], Tuple[int, int, int, int]]

StrOrBytesPath = Union[str, bytes, PathLike[str], PathLike[bytes]]


class Font:
    def __init__(self, path: str, size: int = 10, **kwargs: Any) -> None:
        self._font: ImageFont.FreeTypeFont = ImageFont.truetype(path, size=size, **kwargs)

    @property
    def font(self) -> ImageFont.FreeTypeFont:
        return self._font

    def getsize(self, text: str) -> Tuple[float, float]:
        bbox: Tuple[float, float, float, float] = self.font.getbbox(text)
        return bbox[2], bbox[3]


class Text:
    def __init__(
        self, text: str, font: Union[ImageFont.FreeTypeFont, Font], color: Color = "black"
    ) -> None:
        self.text: str = text
        self.color: Color = color
        if isinstance(font, Font):
            self.font: ImageFont.FreeTypeFont = font.font
        else:
            self.font: ImageFont.FreeTypeFont = font

    def getsize(self) -> Tuple[float, float]:
        bbox: Tuple[float, float, float, float] = self.font.getbbox(self.text)
        return bbox[2], bbox[3]


class Canvas:
    def __init__(
        self,
        size: Optional[Tuple[int, int]] = None,
        width: int = 0,
        height: int = 0,
        color: Color = 0,
    ) -> None:
        if not (size or (width and height)):
            raise ValueError(
                "Expecting size or width & height, got {} & {} instead.".format(
                    type(size), "{}:{}".format(type(width), type(height))
                )
            )
        elif not size:
            size: Tuple[int, int] = (width, height)
        self.size: Tuple[int, int] = size
        self.color: Color = color
        self.image: Image.Image = Image.new("RGBA", size, color=color)


class Editor:
    def __init__(self, _image: Union[Image.Image, str, BytesIO, "Editor", Canvas, Path]) -> None:
        if isinstance(_image, (str, BytesIO, Path)):
            self.image: Image.Image = Image.open(_image)
        elif isinstance(_image, (Canvas, Editor)):
            self.image: Image.Image = _image.image
        elif isinstance(_image, Image):
            self.image: Image.Image = _image
        else:
            raise ValueError(
                "Editor requires an Image, Path, Editor or Canvas, recieved {} instead.".format(
                    type(_image)
                )
            )
        self.image: Image.Image = self.image.convert("RGBA")

    @property
    def image_bytes(self) -> BytesIO:
        _bytes: BytesIO = BytesIO()
        self.image.save(_bytes, "png", optimize=True)
        _bytes.seek(0)
        return _bytes

    def show(self) -> None:
        self.image.show()

    def save(
        self, fp: StrOrBytesPath, file_format: Optional[str] = None, **params: Any
    ) -> None:
        self.image.save(fp, file_format, **params)

    def resize(self, size: Tuple[int, int], crop: bool = False) -> "Editor":
        if not crop:
            self.image = self.image.resize(size, Image.Resampling.LANCZOS)
        else:
            width, height = self.image.size
            ideal_width, ideal_height = size
            aspect = width / height
            ideal_aspect = ideal_width / ideal_height
            if aspect > ideal_aspect:
                new_width = ideal_aspect * height
                offset = int((width - new_width) / 2)
                resize = (offset, 0, width - offset, height)
            else:
                new_height = width / ideal_aspect
                offset = int((height - new_height) / 2)
                resize = (0, offset, width, height - offset)
            self.image = self.image.crop(resize).resize(
                (ideal_width, ideal_height), Image.Resampling.LANCZOS
            )
        return self

    def paste(
        self, image: Union[Image.Image, "Editor", Canvas], position: Tuple[int, int]
    ) -> "Editor":
        blank: Image.Image = Image.new("RGBA", size=self.image.size, color=(255, 255, 255, 0))
        if isinstance(image, Editor) or isinstance(image, Canvas):
            image: Image.Image = image.image
        blank.paste(image, position)
        self.image = Image.alpha_composite(self.image, blank)
        blank.close()
        return self

    def text(
        self,
        position: Tuple[float, float],
        text: str,
        font: Optional[Union[ImageFont.FreeTypeFont, Font]] = None,
        color: Color = "black",
        align: Literal["left", "center", "right"] = "left",
        stroke_width: Optional[int] = None,
        stroke_fill: Color = "black",
    ) -> "Editor":
        if isinstance(font, Font):
            font: ImageFont.FreeTypeFont = font.font
        anchors: Dict[str, str] = {"left": "lt", "center": "mt", "right": "rt"}
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.image)
        if stroke_width:
            draw.text(
                position,
                text,
                color,
                font=font,
                anchor=anchors[align],
                stroke_width=stroke_width,
                stroke_fill=stroke_fill,
            )
        else:
            draw.text(position, text, color, font=font, anchor=anchors[align])
        return self

    def rectangle(
        self,
        position: Tuple[float, float],
        width: float,
        height: float,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        outline: Optional[Color] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> "Editor":
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.image)
        to_width: float = width + position[0]
        to_height: float = height + position[1]
        if color:
            fill: Color = color
        if radius <= 0:
            draw.rectangle(
                position + (to_width, to_height),
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        else:
            draw.rounded_rectangle(
                position + (to_width, to_height),
                radius=radius,
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        return self

    def bar(
        self,
        position: Tuple[float, float],
        max_width: Union[int, float],
        height: Union[int, float],
        percentage: int = 1,
        fill: Optional[Color] = None,
        color: Optional[Color] = None,
        outline: Optional[Color] = None,
        stroke_width: float = 1,
        radius: int = 0,
    ) -> "Editor":
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(self.image)
        if color:
            fill: Color = color
        ratio: float = max_width / 100
        to_width: float = ratio * percentage + position[0]
        height: float = height + position[1]
        if radius <= 0:
            draw.rectangle(
                position + (to_width, height),
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        else:
            draw.rounded_rectangle(
                position + (to_width, height),
                radius=radius,
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
        return self
