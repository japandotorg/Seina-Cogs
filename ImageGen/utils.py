import io
from typing import List, Optional

import discord
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from redbot.core import commands

from .converters import ImageConverter
from .funcs import create_embed

__all__ = [
    "image_to_file",
    "maybe_resize_image",
    "rotate_image",
    "invert_image",
    "greyscale_image",
    "deepfry_image",
    "noise_image",
    "blur_image",
    "brighten_image",
    "contrast_image",
    "make_mask",
    "make_flag",
    "pride_flag",
    "add_impact",
]


def image_to_file(image: Image, name: str) -> discord.File:
    img_bytes = io.BytesIO()
    image.save(img_bytes, "png", optimize=True)

    img_bytes.seek(0)

    return discord.File(img_bytes, f"{name}.png")


def maybe_resize_image(image: Image, max_size: int) -> Image:
    b = io.BytesIO()
    image.save(b, "png")

    while b.tell() > max_size:
        b.close()
        new_size = image.size[0] // 2, image.size[1] // 2
        image = image.resize(new_size, resample=Image.BILINEAR)
        b = io.BytesIO()
        image.save(b, "png")

    return image


def rotate_image(b: bytes, angle: int, max_size: int):
    image = Image.open(io.BytesIO(b)).convert("RGBA")
    image = image.rotate(-angle, expand=True)
    image = maybe_resize_image(image, max_size)

    return image_to_file(image, "rotate")


def invert_image(b: bytes, max_size) -> discord.File:
    image = Image.open(io.BytesIO(b).convert("RGBA"))

    r, g, b, a = image.split()
    rgb_image = Image.merge("RGB", (r, g, b))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()

    image = Image.merge("RGBA", (r2, g2, b2, a))
    image = maybe_resize_image(image, max_size)

    return image_to_file(image, "inverted")


def greyscale_image(b: bytes) -> discord.File:
    # Double convert for transparent gifs
    image = Image.open(io.BytesIO(b)).convert("RGBA").convert("LA")

    return image_to_file(image, "greyscale")


def deepfry_image(b: bytes) -> discord.File:
    original = Image.open(io.BytesIO(b)).convert("P").convert("RGB")
    noise = Image.effect_noise(original.size, 20).convert("RGB")

    b = ImageEnhance.Brightness(original)
    image = b.enhance(1.1)
    c = ImageEnhance.Contrast(image)
    image = c.enhance(10)

    image = Image.blend(image, noise, 0.25).convert("P").convert("RGB")

    img_bytes = io.BytesIO()
    image.save(img_bytes, "jpeg", quality=10, optimize=True)

    img_bytes.seek(0)
    return discord.File(img_bytes, "deepfry.jpg")


def noise_image(b: bytes, alpha: float) -> discord.File:
    original = Image.open(io.BytesIO(b)).convert("RGBA")
    noise = Image.effect_noise(original.size, 20).convert("RGBA")

    image = Image.blend(original, noise, alpha)

    return image_to_file(image, "noise")


def blur_image(b: bytes, radius: int) -> discord.File:
    image = Image.open(io.BytesIO(b)).convert("RGBA")
    image = image.filter(ImageFilter.GaussianBlur(radius))

    return image_to_file(image, "blur")


def brighten_image(b: bytes, intensity: float) -> discord.File:
    image = Image.open(io.BytesIO(b)).convert("RGBA")

    b = ImageEnhance.Brightness(image)
    image = b.enhance(intensity)

    return image_to_file(image, "brighten")


def contrast_image(b: bytes, intensity: float) -> discord.File:
    image = Image.open(io.BytesIO(b)).convert("RGBA")

    c = ImageEnhance.Contrast(image)
    image = c.enhance(intensity)

    return image_to_file(image, "contrast")


def make_mask(colors, width, height):
    color_height = height / len(colors)

    color_image = Image.new("RGBA", (width, height))
    canvas = ImageDraw.Draw(color_image)

    for i, color in enumerate(colors):
        x1 = 0
        x2 = width

        y1 = i * color_height
        y2 = y1 + color_height

        cords = [(x1, y1), (x2, y2)]

        canvas.rectangle(cords, fill=color)

    return color_image


def make_flag(b: bytes, alpha: float, max_size: int, colors: List):
    image = Image.open(io.BytesIO(b)).convert("RGBA")

    mask = make_mask(colors, *image.size)
    blended_image = Image.blend(image, mask, alpha)
    resized_image = maybe_resize_image(blended_image, max_size)

    return image_to_file(resized_image, "pride")


async def pride_flag(
    ctx: commands.Context, image: Optional[bytes], transparency: int, colors: List
):
    if not 0 < transparency <= 100:
        raise commands.BadArgument("Transparency should be in between 0 and 100")

    transparency /= 100

    if not image:
        image_bytes = await ImageConverter().convert(ctx, image)
    else:
        image_bytes = image

    limit = ctx.guild.filesize_limit if ctx.guild else 8 * 1000 * 1000

    file = await ctx.bot.loop.run_in_executor(
        None, make_flag, image_bytes, transparency, limit, colors
    )

    embed = create_embed(
        ctx.author, title=f"Here's your {ctx.command.name} image:", image="attachment://pride.png"
    )

    await ctx.send(embed=embed, file=file)


def add_impact(b: bytes, max_size: int, top_text: str, bottom_text: str):
    image = Image.open(io.BytesIO(b)).convert("RGBA")

    top_text = top_text.upper()
    bottom_text = bottom_text.upper() if bottom_text else None

    if image.width < 256:
        height = int(256 * (image.height / image.width))
        image = image.resize((256, height))

    impact = ImageFont.truetype("assets/impact.ttf", image.width // 10)
    canvas = ImageDraw.Draw(image)

    xpos = image.width / 2

    font_kwargs = {
        "fill": (255, 255, 255),
        "font": impact,
        "align": "center",
        "stroke_width": 3,
        "stroke_fill": (0, 0, 0),
    }

    canvas.multiline_text(xy=(xpos, 0), text=top_text, anchor="ma", **font_kwargs)

    if bottom_text:
        canvas.multiline_text(
            xy=(xpos, image.height), text=bottom_text, anchor="md", **font_kwargs
        )

    image = maybe_resize_image(image, max_size)

    return image_to_file(image, "impact")
