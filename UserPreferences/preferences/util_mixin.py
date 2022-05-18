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

from redbot.core import Config

from .utils import CogMixin, mixin_command


class UtilsPreference(CogMixin):
    config: Config

    def setup_self(self):
        self.deleteconfirmations.setup(self)
        self.config.register_user(delete_confirmation=True)

    async def red_get_data_for_user(self, *, user_id):
        return None

    async def red_delete_data_for_user(self, *, requester, user_id):
        await self.config.user_from_id(user_id).delete_confirmation.set(True)

    @mixin_command("preferences")
    async def deleteconfirmations(self, ctx, delete: bool):
        """Set whether confirmation messages are deleted"""
        await self.config.user(ctx.author).delete_confirmation.set(delete)
        await ctx.tick()
