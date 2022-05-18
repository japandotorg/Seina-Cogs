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

    @mixin_command('preferences')
    async def deleteconfirmations(self, ctx, delete: bool):
        """ Set whether confirmation messages are deleted """
        await self.config.user(ctx.author).delete_confirmation.set(delete)
        await ctx.tick()
        