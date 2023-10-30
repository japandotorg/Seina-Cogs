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

import discord
from redbot.core import commands
from redbot.core.utils.chat_formatting import box

from .abc import CompositeMetaClass, MixinMeta
from .utils import cleanup_code


class CommandsMixin(MixinMeta, metaclass=CompositeMetaClass):
    @commands.is_owner()
    @commands.group(name="errorhandler", aliases=["eh"])  # type: ignore
    async def _error_handler(self, _: commands.Context):
        """
        Set and view the code for when a CommandInvokeError is raised.
        """
        pass

    @_error_handler.command(name="view")  # type: ignore
    async def _error_handler_view(self, ctx: commands.Context):
        """
        View the string set to eval when a CommandInvokeError is raised.
        """
        message: str = await self.config.message()
        await ctx.send(
            f"The current evaluated code is:\n{box(str(message), lang='py')}",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )

    @_error_handler.command(name="set")  # type: ignore
    async def _error_handler_set(self, ctx: commands.Context, *, code: str):
        """
        Set the string to evaluate, use a python code block.

        Environment variables:
            cf      - redbot.core.utils.chat_formatting module
            ctx     - context of invokation
            error   - the error that was raised
            discord - discord.py library
        """
        body: str = cleanup_code(code)
        await self.config.message.set(body)
        await ctx.send(
            f"Handler code set to:\n{box(code, lang='py')}",
            reference=ctx.message.to_reference(fail_if_not_exists=False),
            allowed_mentions=discord.AllowedMentions(replied_user=False),
        )
        self._eval_string = body

    @_error_handler.command(name="test")  # type: ignore
    async def _error_handler_test(self, ctx: commands.Context):
        """
        This command contains an AssertionError purposely so that you can make sure your handler works
        """
        assert False
