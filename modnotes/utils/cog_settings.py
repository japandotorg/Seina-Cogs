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

from typing import Any, Dict

from redbot.core import data_manager
from redbot.core.bot import Red

from .json_utils import *


class CogSettings(object):
    SETTINGS_FILE_NAME = "cog_settings.json"

    def __init__(self, cog_name: str, bot: Red = None) -> None:
        self.folder: str = str(data_manager.cog_data_path(raw_name=cog_name))
        self.file_path: str = os.path.join(self.folder, CogSettings.SETTINGS_FILE_NAME)

        self.bot: Red = bot

        self.check_folder()

        self.default_settings: Dict[Any, Any] = self.make_default_settings()
        if not os.path.isfile(self.file_path):
            log.warning(f"CogSettings config for {self.file_path} not found.  Creating default...")

            self.bot_settings: Dict[Any, Any] = self.default_settings
            self.save_settings()
        else:
            current: Any = self.intify(read_json_file(self.file_path))
            updated: bool = False
            for key in self.default_settings:
                if key not in current.keys():
                    current[key] = self.default_settings[key]
                    updated: bool = True

            self.bot_settings = current
            if updated:
                self.save_settings()

    def check_folder(self) -> None:
        if not os.path.exists(self.folder):
            log.info(f"Creating {self.folder}")
            os.makedirs(self.folder)

    def save_settings(self) -> None:
        write_json_file(self.file_path, self.bot_settings)

    def make_default_settings(self) -> Dict[Any, Any]:
        return {}

    @classmethod
    def intify(cls, key: Any) -> Any:
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
