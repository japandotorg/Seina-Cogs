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

import difflib

import discord
from redbot.core import commands

from .util import STATUS_CODES

class StatusCodes(commands.Cog):
    """
    Find the meaning behind various status codes.
    """
    
    __author__ = "inthedark.org#0666"
    __version__ = "0.1.0"
    
    def __init__(self, bot):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @commands.command(name="statuscodes", aliases=["statuscode"])
    async def statuscodes(self, ctx, *, code=None):
        """
        Find the meaning behind various status codes.
        """
        embed = discord.Embed(color=await ctx.embed_color())
        
        if not code:
            for codes in STATUS_CODES.values():
                message = ""
                
                for code, tag in codes.items():
                    if not code.isdigit():
                        continue
                    message += f"\n{code} {tag}"
                    
                embed.add_field(
                    name=codes["title"],
                    value=f"{codes['message']}\n```prolog\n{message}\n```",
                    inline=False,
                )
            return await ctx.send(embed=embed)
        
        group = code[0]
        info = STATUS_CODES.get(group)
        if not info:
            statuses = {}
            for data in STATUS_CODES.values():
                for scode, tag in data.items():
                    if scode.isdigit():
                        statuses[tag] = scode
            match = difflib.get_close_matches(
                code,
                [*statuses],
                n=1,
                cutoff=0.0,
            )
            code = statuses[match[0]]
            info = STATUS_CODES.get(code[0])
            
            if not info:
                embed.description = (
                    f"```No {code} status code found in the {group}xx group```"
                )
                return await ctx.send(embed=embed)
            
            embed.title =  info["title"]
            embed.description = f"{info['message']}\n```prolog\n{code} {info[code]}```"
            await ctx.send(embed=embed)