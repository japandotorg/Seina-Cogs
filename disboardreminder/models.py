"""
MIT License

Copyright (c) 2020-2023 PhenoM4n4n
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

from typing import Dict, Optional, Set, Tuple

import discord


class LocalizedMessageValidator:
    __slots__: Tuple[str, str] = (
        "_languages",
        "_success_messages",
    )

    def __init__(self, languages: Set[str] = {"en"}) -> None:
        self._languages: Set[str] = languages
        self._success_messages: Dict[str, str] = {
            "ar": "تم الرفع!",
            "az": "Server qabağa çıxarıldı!",
            "cs": "Úspěšný bump!",
            "de": "Bump erfolgreich!",
            "en": "Bump done!",
            "fr": "Bump effectué !",
            "he": "באמפ בוצע!",
            "hi": "बम्प हो गया!",
            "id": "Bump berhasil! 👍",
            "ja": "表示順をアップしたよ :thumbsup:",
            "ko": "서버 갱신 완료!",
            "pl": "Podbito serwer!",
            "pt": "Bump feito!",
            "ro": "Bump gata!",
            "tr": "Öne çıkarma başarılı!",
            "vi": "Đã bump!",
            "zh-CN": "服务器已顶！",
        }

    def validate_success(self, message: discord.Message) -> Optional[discord.Embed]:
        if not message.embeds:
            return None
        embed: discord.Embed = message.embeds[0]
        if ":thumbsup:" in embed.description:  # type: ignore
            return embed
        for language in self._languages:
            if message.webhook_id and self._success_messages[language] in embed.description:  # type: ignore
                return embed
        return None
