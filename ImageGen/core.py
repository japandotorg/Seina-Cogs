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

import io
import json
import random
import asyncio
import aiohttp
import logging
import requests
from typing import Optional, Literal

from PIL import UnidentifiedImageError, Image, ImageFont, ImageDraw

import discord
from redbot.core.bot import Red
from redbot.core import commands

from .funcs import create_embed
from .converters import ImageConverter

from .utils import (
    invert_image,
    greyscale_image,
    deepfry_image,
    blur_image,
    noise_image,
    brighten_image,
    contrast_image,
    add_impact,
    rotate_image,
    pride_flag
)

log = logging.getLogger("red.seina-cogs.imagegen")

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class ImageGen(commands.Cog):
    """
    Image Generation commands.
    """
    
    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"
    
    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.session = aiohttp.ClientSession()
        
    def cog_unload(self):
        asyncio.create_task(self.session.close())
        
    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        """
        Nothing to delete.
        """
        return
        
    @classmethod
    async def initialize(cls, bot: Red):
        await bot.wait_until_red_ready()
        
    @commands.command()
    async def invert(self, ctx: commands.Context, *, image: Optional[str]):
        """
        Inverts the colors of a specified image!
        """
        
        # Use converter here so that it triggers even without given argument
        image_bytes = await ImageConverter().convert(ctx, image)
        
        limit = ctx.guild.filesize_limit if ctx.guild else 8 * 1000 * 1000
        file = await self.bot.loop.run_in_executor(None, invert_image, image_bytes, limit)
        
        embed = create_embed(
            ctx.author,
            title="Here\'s your inverted image:",
            image="attachment://inverted.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["grey", "gray", "grayscale"])
    async def greyscale(self, ctx: commands.Context, *, image: Optional[str]):
        """
        Greyscale the specified image!
        """
        
        alias = ctx.invoked_with.lower()
        
        # Use converter here so that it triggers even without given argument
        image_bytes = await ImageConverter().convert(ctx, image)
        
        file = await self.bot.loop.run_in_executor(None, greyscale_image, image_bytes)
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your {alias[:4]}scale image:",
            image="attachment://greyscale.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["deep", "fry"])
    async def deepfry(self, ctx: commands.Context, *, image: Optional[str]):
        """
        Deepfry the specified image!
        """
        
        # Use converter here so that it triggers even without given argument
        image_bytes = await ImageConverter().convert(ctx, image)
        
        file = await self.bot.loop.run_in_executor(None, deepfry_image, image_bytes)
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your deepfried image:",
            image="attachment://deepfry.jpg"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["blurry"])
    async def blur(self, ctx: commands.Context, image: Optional[ImageConverter], strength=5):
        """
        Blurs the specified image!
        """
        
        if not image:
            image_bytes = await ImageConverter().convert(ctx, image)
        else:
            image_bytes = image
            
        file = await self.bot.loop.run_in_executor(None, blur_image, image_bytes, abs(strength))
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your blurred image:",
            image="attachment://blur.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["noisy"])
    async def noise(self, ctx: commands.Context, image: Optional[ImageConverter], strength=50):
        """
        Adds noise to specified image! Strength should be in between 0 and 100.
        """
        
        if not 0 < strength <= 100:
            raise commands.BadArgument("Strength should be in between 0 and 100")
        
        strength /= 100
        
        if not image:
            image_bytes = await ImageConverter().convert(ctx, image)
        else:
            image_bytes = image
            
        file = await self.bot.loop.run_in_executor(None, noise_image, image_bytes, strength)
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your noisy image:",
            image="attachment://noise.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["bright", "brightness"])
    async def brighten(self, ctx: commands.Context, image: Optional[ImageConverter], strength=1.25):
        """
        Brightens specified image! Passing in an strength less than 1 will darken it instead.
        """
        
        if not 0 < strength:
            raise commands.BadArgument("Strength should be more than zero!")
        
        if not image:
            image_bytes = await ImageConverter().convert(ctx, image)
        else:
            image_bytes = image
            
        file = await self.bot.loop.run_in_executor(None, brighten_image, image_bytes, strength)
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your brightened image:",
            image="attachment://brighten.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command()
    async def contrast(self, ctx: commands.Context, image: Optional[ImageConverter], strength=1.25):
        """
        Adds contrast to specified image! Passing in an strength less than 1 will lower it instead.
        """
        
        if not 0 < strength:
            raise commands.BadArgument("Strength should be more than zero!")
        
        if not image:
            image_bytes = await ImageConverter().convert(ctx, image)
        else:
            image_bytes = image
            
        file = await self.bot.loop.run_in_executor(None, contrast_image, image_bytes, strength)
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your modified image:",
            image="attachment://contrast.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["meme", "text"])
    async def impact(
        self,
        ctx: commands.Context,
        image: Optional[ImageConverter],
        top_text: str,
        bottom_text: Optional[str]
    ):
        """
        Adds text with impact font to specified image!
        """
        
        if not image:
            image_bytes = await ImageConverter().convert(ctx, image)
        else:
            image_bytes = image
            
        file = await self.bot.loop.run_in_executable(
            None,
            add_impact,
            image_bytes,
            ctx.guild.filesize_limit if ctx.guild else 8 * 1000 * 1000,
            top_text,
            bottom_text
        )
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your modified image:",
            image="attachment://impact.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command()
    async def rotate(self, ctx: commands.Context, image: Optional[ImageConverter], angle=90):
        """
        Rotates an image! Positive number for clockwise, negative for counter-clockwise.
        """
        
        if not image:
            image_bytes = await ImageConverter().convert(ctx, image)
        else:
            image_bytes = image
            
        limit = ctx.guild.filesize_limit if ctx.guild else 8 * 1000 * 1000
        
        file = await self.bot.loop.run_in_executor(None, rotate_image, image_bytes, angle, limit)
        
        embed = create_embed(
            ctx.author,
            title=f"Here\'s your modified image:",
            image="attachment://rotate.png"
        )
        
        await ctx.send(embed=embed, file=file)
        
    @commands.command(aliases=["rainbow", "lgbt", "lgbtq"])
    async def pride(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the pride rainbow to image!
        """
        pride_colors = [
            (255, 0, 24),
            (255, 165, 44),
            (255, 255, 65),
            (0, 128, 24),
            (0, 0, 249),
            (134, 0, 125)
        ]
        
        await pride_flag(ctx, image, transparency, pride_colors)
        
    @commands.command(aliases=["homo", "homosexual"])
    async def gay(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the gay flag to image!
        """
        
        gay_colors = [
            (7, 141, 112),
            (38, 206, 170),
            (153, 232, 194),
            (255, 255, 255),
            (123, 173, 227),
            (80, 73, 203),
            (62, 26, 120)
        ]

        await pride_flag(ctx, image, transparency, gay_colors)
        
    @commands.command(aliases=["trans"])
    async def transgender(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the transgender flag to image!
        """
        
        trans_colors = [
            (91, 206, 250), 
            (245, 169, 184), 
            (255, 255, 255), 
            (245, 169, 184), 
            (91, 206, 250)
        ]

        await pride_flag(ctx, image, transparency, trans_colors)
        
        
    @commands.command(aliases=["bi"])
    async def bisexual(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the bisexual flag to image!
        """
        
        bi_colors = [
            (216, 9, 126), 
            (216, 9, 126), 
            (140, 87, 156), 
            (36, 70, 142), 
            (36, 70, 142)
        ]

        await pride_flag(ctx, image, transparency, bi_colors)
        
    @commands.command(aliases=["lesb"])
    async def lesbian(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the lesbian flag to image!
        """
        
        lesbian_colors = [
            (213, 45, 0), 
            (239, 118, 39), 
            (255, 154, 86), 
            (255, 255, 255), 
            (209, 98, 164), 
            (181, 86, 144), 
            (163, 2, 98)
        ]
        
        await pride_flag(ctx, image, transparency, lesbian_colors)
        
    @commands.command(aliases=["ace"])
    async def asexual(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the asexual flag to image!
        """
        
        ace_colors = [
            (0, 0, 0), 
            (164, 164, 164), 
            (255, 255, 255), 
            (129, 0, 129)
        ]

        await pride_flag(ctx, image, transparency, ace_colors)
        
    @commands.command(aliases=["pan"])
    async def pansexual(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the pansexual flag to image!
        """
        
        pan_colors = [
            (255, 28, 141), 
            (255, 215, 0), 
            (26, 179, 255)
        ]

        await pride_flag(ctx, image, transparency, pan_colors)
        
    @commands.command(aliases=["nb", "non-binary", "non_binary"])
    async def nonbinary(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the non-binary flag to image!
        """
        
        nonbinary_colors = [
            (255, 244, 48), 
            (255, 255, 255), 
            (156, 89, 209), 
            (0, 0, 0)
        ]

        await pride_flag(ctx, image, transparency, nonbinary_colors)
        
    @commands.command(aliases=["nonconforming"])
    async def gnc(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the gender nonconforming flag to image!
        """
        
        gnc_colors = [
            (80, 40, 76), 
            (150, 71, 122), 
            (93, 150, 247), 
            (255, 255, 255), 
            (93, 150, 247), 
            (150, 71, 122), 
            (80, 40, 76)
        ]

        await pride_flag(ctx, image, transparency, gnc_colors)
        
    @commands.command(aliases=["aro"])
    async def aromantic(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the aromantic flag to image!
        """
        
        aromantic_colors = [
            (58, 166, 63), 
            (168, 212, 122), 
            (255, 255, 255), 
            (170, 170, 170), 
            (0, 0, 0)
        ]

        await pride_flag(ctx, image, transparency, aromantic_colors)
        
    @commands.command(aliases=["gq"])
    async def genderqueer(self, ctx: commands.Context, image: Optional[ImageConverter], transparency=50):
        """
        Adds the genderqueer flag to image!
        """
        
        genderqueer_colors = [
            (181, 126, 220), 
            (255, 255, 255), 
            (73, 128, 34)
        ]

        await pride_flag(ctx, image, transparency, genderqueer_colors)
        
    
    @commands.command(aliases=["simp"])
    async def simpcard(self, ctx: commands.Context, member: discord.Member = None):
        """
        Have fun being a simp xD.
        """
        await ctx.trigger_typing()
        
        if not member:
            member = ctx.author
            
        async with self.session.get(
            f"https://some-random-api.ml/canvas/simpcard?avatar={member.avatar_url_as(format='png')}"
        ) as r:
            fp = io.BytesIO(await r.read())
            file = discord.File(fp, "simpcard.png")
            embed = discord.Embed(
                color=await ctx.embed_color(),
                timestamp=ctx.message.created_at
            )
            embed.set_image(url="attachment://simpcard.png")
            
            await ctx.send(embed=embed, file=file)
            
    @commands.command(aliases=["imspeed"])
    async def iamspeed(self, ctx, member: discord.Member = None):
        """
        I'm speeddddddd!
        """
        if not member:
            member = ctx.author
            
        embed = discord.Embed(
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=f"https://vacefron.nl/api/iamspeed?user={member.avatar_url_as(format='png')}")
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def tweet(self, ctx: commands.Context, comment, member: discord.Member = None, displayname= None):
        """
        Tweet something but inside discord!
        """
        await ctx.trigger_typing()
        
        if not member:
            member = ctx.author
            
        if not displayname:
            displayname = member.display_name
            
        async with self.session.get(
            f"https://some-random-api.ml/canvas/tweet?comment={comment}&displayname={displayname}&username={member.display_name}&avatar={member.avatar_url_as(format='png')}"
        ) as r:
            fp = io.BytesIO(await r.read())
            file = discord.File(fp, "tweet.png")
            embed = discord.Embed(
                color=await ctx.embed_color(),
                timestamp=ctx.message.created_at
            )
            embed.set_image(url="attachment://tweet.png")
            
            await ctx.send(embed=embed, file=file)
            
    @commands.command()
    async def wasted(self, ctx, membere: discord.Member = None):
        """
        Wasted in GTA style lmao!
        """
        await ctx.trigger_typing()
        if not member:
            member = ctx.author
            
        embed = discord.Embed(
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=f"https://some-random-api.ml/canvas/wasted?avatar={member.avatar_url_as(format='png')}")
        
        await ctx.send(embed=embed)
        
    @commands.command(aliases=["useless"])
    async def worthless(self, ctx, *, text):
        await ctx.trigger_typing()
        
        asset = requests.get("https://i.imgur.com/JdujF4G.jpg")
        uno = Image.open(io.BytesIO(asset.content))
        
        i = requests.get("https://github.com/matomo-org/travis-scripts/blob/master/fonts/Arial.ttf", allow_redirects=True)
        draw = ImageDraw.Draw(uno)
        font = ImageFont.truetype(io.BytesIO(i.content), 30)
        
        x = 98
        y = 80
        
        split_strings = []
        
        for index in range(0, len(text), 25):
            split_strings.append(text[index: index + 25])
            
        for line in split_strings:
            draw.text((x, y), line, (0, 0, 0), font=font)
            y += 30
            
        fp = io.BytesIO()
        uno.save(fp, "png")
        fp.seek(0)
        
        embed = discord.Embed(
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url="attachment://worthless.png")
        
        await ctx.send(embed=embed, file=discord.File(fp, "worthless.png"))
        
    @commands.command()
    async def yeet(self, ctx, *, text):
        """
        Yeet tf outta someone/something.
        """
        await ctx.trigger_typing()
        
        asset = requests.get("https://i.imgur.com/pFbPHlp.png")
        meme = Image.open(io.BytesIO(asset.content)).convert("RGBA")
        
        txt = Image.new(
            "RGBA",
            (300, 300),
            (255, 255, 255, 255)
        )
        
        i = requests.get("https://github.com/matomo-org/travis-scripts/blob/master/fonts/Arial.ttf", allow_redirects=True)
        draw = ImageDraw.Draw(txt)
        font = ImageFont.truetype(io.BytesIO(i.content), 30)
        
        x = 1
        y = 1
        
        split_strings = []
        
        for index in range(0, len(text), 20):
            split_strings.append(text[index: index + 20])
            
        for line in split_strings:
            draw.text((x, y), line, (0, 0, 0, 255), font=font)
            y += 30
            
        rotated = txt.rotate(angle=20, expand=True, fillcolor=(0, 0, 0, 0))
        
        meme.paste(rotated, (1015, 300), rotated)
        
        fp = io.BytesIO()
        meme.save(fp, "png")
        fp.seek(0)
        
        embed = discord.Embed(
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url="attachment://yeet.png")
        
        await ctx.send(embed=embed, file=discord.File(fp, "yeet.png"))
        
    @commands.command(aliases=["yodasay"])
    async def yoda(self, ctx, *, phrase):
        """
        Say something wise but as Yoda.
        """
        await ctx.trigger_typing()
        
        api = requests.get(f"https://yoda-api.appspot.com/api/v1/yodish?text-{phrase}")
        api = api.json()
        
        await ctx.send(api["yodish"])
        
    @commands.command(aliases=["waifu"])
    async def waifuai(self, ctx):
        embed = discord.Embed(
            color=await ctx.embed_color(),
            title=f"Here's your waifu!",
            description="Remember that these images are AI generated!",
            timestamp=ctx.message.created_at
        )
        embed.set_image(url="https://www.thiswaifudoesnotexist.net/eexample-" + str(random.randint(1, 100000)) + ".jpg")
        
        await ctx.send(embed=embed)
    
    @commands.command()
    async def water(self, ctx, *, text):
        """
        Water when?
        """
        embed = discord.Embed(
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=f'https://vacefron.nl/api/water?text={text.replace(" ", "%20")}')
        
        await ctx.send(embed=embed)
        
    @commands.command(aliases=["trigger"])
    async def triggered(self, ctx, member: discord.Member = None):
        """"
        UR SO TRIGERRED BRO!
        """
        if member == None:
            member = ctx.author
            
        await ctx.trigger_typing()
        
        async with self.session.get(
            f"https://some-random-api.ml/canvas/triggered?avatar={member.avatar_url_as(format='png', size=1024)}"
        ) as r:
            fp = io.BytesIO(await r.read())
            file = discord.File(fp, "triggered.png")
            embed = discord.Embed(
                color=await ctx.embed_color(),
                timestamp=ctx.message.created_at
            )
            embed.set_image(url="attachment://triggered.png")
            
            await ctx.send(embed=embed, file=file)
            
    @commands.command()
    async def rover(self, ctx, sol = "1000"):
        """
        Random rover mast images generated by nasa.
        """
        await ctx.trigger_typing()
        
        api =  requests.get(f"https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos?sol={sol}&api_key=S4hYTUEMT9xPsqB9fC3bhEr7q2g5gMwSHkG2YGHI")
        api = api.json()
        
        number = random.randint(0, len(api["photos"]))
        
        embed = discord.Embed(
            title=api["photos"][number]["camera"]["full_name"] + " | " + api["photos"][number]["rover"]["name"],
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url=api["photos"][number]["img_src"])
        
        await ctx.send(embed=embed)
        
    @commands.command()
    async def presentation(self, ctx, *, text):
        """
        Present this HUH!
        """
        await ctx.trigger_typing()
        
        asset = requests.get("https://i.imgur.com/fUkLr98.jpg")
        uno = Image.open(io.BytesIO(asset.content))
        
        i = requests.get("https://github.com/matomo-org/travis-scripts/blob/master/fonts/Arial.ttf", allow_redirects=True)
        draw = ImageDraw.Draw(uno)
        font = ImageFont.truetype(io.BytesIO(i.content), 30)
        
        x = 75
        y = 220
        
        split_strings = []
        
        for index in range(0, len(text), 32):
            split_strings.append(text[index: index + 32])
            
        for line in split_strings:
            draw.text((x, y), line, (0, 0, 0), font=font)
            y += 50
            
        fp = io.BytesIO()
        uno.save(fp, "png")
        fp.seek(0)
        
        embed = discord.Embed(
            color=await ctx.embed_color(),
            timestamp=ctx.message.created_at
        )
        embed.set_image(url="attachment://presentation.png")
        
        await ctx.send(embed=embed, file=discord.File(fp, "presentation.png"))
        
    async def cog_command_error(self, ctx: commands.Context, error: Exception) -> None:
        embed = None
        
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
            
        if isinstance(error, UnidentifiedImageError):
            embed = create_embed(
                ctx.author,
                title="Error while generating image!",
                description="The bot wasn\'t able to identify the image\'s format\n"
                            "**Note:** Links from sites like Tenor and GIPHY don\'t wotk, "
                            "use the direct image url instead.",
                color=await ctx.embed_color()
            )
            
        if embed:
            return await ctx.send(embed=embed)
        
        ctx.uncaught_error = True
        