from .core import UserPreferences

__red_end_user_data_statement__ = "All explicitly stored user preferences are kept persistantly."


def setup(bot):
    bot.add_cog(UserPreferences(bot))
