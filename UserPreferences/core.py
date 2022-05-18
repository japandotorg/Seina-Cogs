import pickle
import logging
from io import BytesIO

from redbot.core.bot import Red
from redbot.core import Config, commands
from redbot.core.commands import Context

from userpreferences.preferences.util_mixin import UtilsPreference
from userpreferences.preferences.timezone import TimezonePreference

log = logging.getLogger("red.seina-cogs.userpreferences")

class UserPreferences(TimezonePreference, UtilsPreference):
    """ Stores user Preferences for users. """
    
    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=6969420666420)
        self.setup_mixins()
        
    async def red_get_data_for_user(self, *, user_id):
        """ Get a user's personal data. """
        data = []

        if (tz := await self.config.user_by_id(user_id).timezone()) is not None:
            data.append(f"Timezone: `{pickle.loads(tz)}`")

        data = '\n'.join(await self.get_mixin_user_data(user_id))
        if not data:
            data = "No data is stored for user with ID {}.\n".format(user_id)
        return {"user_data.txt": BytesIO(data.encode())}

    async def red_delete_data_for_user(self, *, requester, user_id):
        """ Delete a user's personal data. """
        await self.delete_mixin_user_data(requester, user_id)

    @commands.group(aliases=['preference', 'prefs', 'pref'])
    async def preferences(self, ctx: Context):
        """ Set user preferences """
