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
