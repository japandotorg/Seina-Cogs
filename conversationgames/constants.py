from datetime import timedelta
from typing import Dict, Final, Literal, Union

import yarl

SESSION_TIMEOUT: int = 15

URL_EXPIRE_AFTER: Dict[str, timedelta] = {"*.truthordarebot.xyz": timedelta(seconds=3)}

StrOrUrl = Union[str, yarl.URL]
BASE_URL: Final[StrOrUrl] = "https://api.truthordarebot.xyz/v1"

Endpoints = Literal["truth", "dare", "wyr", "nhie", "paranoia"]
Ratings = Literal["pg", "pg13", "r"]
Methods = Literal["GET", "HEAD"]
RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]
