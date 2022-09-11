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

from typing import Optional

import discord
from redbot.core import commands  # type: ignore
from redbot.core.bot import Red  # type: ignore

from .api import *
from .typehints import CratesIOCrate


class Crates(commands.Cog):
    """
    Get information about a crate on crates.io
    """

    __author__ = ["inthedark.org#0666"]
    __version__ = "0.1.0"

    async def red_delete_data_for_user(self, **kwargs):
        return

    def __init__(self, bot: Red):
        self.bot: Red = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        pre_processed = super().format_help_for_context(ctx) or ""
        n = "\n" if "\n\n" not in pre_processed else ""
        text = [
            f"{pre_processed}{n}",
            f"Cog Version: **{self.__version__}**",
            f"Author: **{self.__author__}**",
        ]
        return "\n".join(text)

    @commands.group(name="crates", aliases=["crate"], invoke_without_command=True)
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _crates(
        self,
        ctx: commands.Context,
    ) -> None:
        """
        Group for the crates command.
        """

    @_crates.command(name="info", aliases=["i"])
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def _into(self, ctx: commands.Context, crate: CratesIOCrate) -> None:
        data: Optional[dict] = await CratesIOAPI._get_crate_data(crate=crate.lower())
        if data:
            owners: list = await CratesIOAPI._get_crate_owners(crate=crate.lower())
            crate_url: str = f"https://crates.io/crates/{data['crate']['name']}"
            embed: discord.Embed = discord.Embed(
                color=await ctx.embed_color(),
                title=f"{data['crate']['name']} `{data['crate']['newest_version']}`",
                url=data["crate"].get("homepage", crate_url),
            ).set_thumbnail(url=owners[0]["avatar"])

            if (crate_desc := data["crate"]["description"]) is not None and len(crate_desc) != 0:
                embed.add_field(
                    name="Crate Description:",
                    value=f"```{crate_desc.strip()}```",
                    inline=False,
                )

            more_authors: str = f"[{len(owners) - 5}]({crate_url})" if len(owners) > 5 else ""
            authors: str = (
                "authors, ".join(
                    f"[{owner['name']}{' `(team)`' if owner['kind'] == 'team' else ''}]"
                    f"({owner['url']})"
                    for owner in owners[:5]
                )
                + more_authors
                + "\n"
            )

            created_at: str = data["crate"]["created_at"]

            all_time_downloads: str = (
                f"```rust\n{data['crate']['downloads']} //"
                f"{CratesIOAPI._get_crate_downloads}```\n"
            )

            info: str = f"{authors}{created_at}{all_time_downloads}"

            embed.add_field(
                name="Info:",
                value=info,
                inline=False,
            )

            links: list = []
            link_strings: list = []
            for link in links:
                if link[0] is not None and len(link[0]) != 0:
                    link_strings.append(f"- [{link[1]}]({link[0]})")

            if len(link_strings) != 0:
                embed.add_field(name=f"Links:", value="\n".join(link_strings), inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(
                embed=discord.Embed(
                    description=f"No crate with the name `{crate}`", color=discord.Color.red()
                )
            )
