from redbot.core import data_manager

from .json_utils import *


class CogSettings(object):
    SETTINGS_FILE_NAME = "cog_settings.json"

    def __init__(self, cog_name, bot=None):
        self.folder = str(data_manager.cog_data_path(raw_name=cog_name))
        self.file_path = os.path.join(self.folder, CogSettings.SETTINGS_FILE_NAME)

        self.bot = bot

        self.check_folder()

        self.default_settings = self.make_default_settings()
        if not os.path.isfile(self.file_path):
            log.warning(
                "CogSettings config for {} not found.  Creating default...".format(self.file_path)
            )
            self.bot_settings = self.default_settings
            self.save_settings()
        else:
            current = self.intify(read_json_file(self.file_path))
            updated = False
            for key in self.default_settings.keys():
                if key not in current.keys():
                    current[key] = self.default_settings[key]
                    updated = True

            self.bot_settings = current
            if updated:
                self.save_settings()

    def check_folder(self):
        if not os.path.exists(self.folder):
            log.info("Creating {}".format(self.folder))
            os.makedirs(self.folder)

    def save_settings(self):
        write_json_file(self.file_path, self.bot_settings)

    def make_default_settings(self):
        return {}

    @classmethod
    def intify(cls, key):
        if isinstance(key, dict):
            return {cls.intify(k): cls.intify(v) for k, v in key.items()}
        elif isinstance(key, (list, tuple)):
            return [cls.intify(x) for x in key]
        elif isinstance(key, str) and key.isdigit():
            return int(key)
        elif isinstance(key, str) and key.replace(".", "", 1).isdigit():
            return float(key)
        else:
            return key
