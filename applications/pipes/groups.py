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

from redbot.core import app_commands, commands

from ..abc import CompositeMetaClass, PipeMeta
from ..common.utils import has_guild_permissions


class Groups(PipeMeta, metaclass=CompositeMetaClass):

    @commands.hybrid_group(
        name="application",
        aliases=[
            "app",
            "apps",
        ],
    )
    @has_guild_permissions(manage_guild=True)
    async def application(self, _: commands.GuildContext) -> None:
        """Base command for applications."""

    @application.group(name="config", aliases=["conf"])
    async def application_config(self, _: commands.GuildContext) -> None:
        """Configuration commands for applications."""

    @application.group(name="role", aliases=["roles"])
    async def application_role(self, _: commands.GuildContext) -> None:
        """Role configuration commands for applications."""

    @application.group(name="question", aliases=["questions", "ques"])
    async def application_question(self, _: commands.GuildContext) -> None:
        """Question configuration commands for applications."""
